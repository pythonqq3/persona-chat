"""
微信聊天数据清洗脚本
功能：将 WeFlow 或其他工具导出的 TXT 文件清洗成可用于人格分析的纯文本
支持格式：
  1. WeFlow TXT 格式（时间戳 '说话人' + 内容 + 空行）
  2. WeChatMsg CSV 格式

用法：
  # 模拟自己（从多个聊天窗口合并数据）
  python clean_chat.py --input data/raw/texts/ --person "我" --output data/clean/

  # 模拟别人
  python clean_chat.py --input data/raw/texts/私聊_xxx.txt --person "陈琴" --output data/clean/
"""

import re
import json
import argparse
from pathlib import Path
from collections import defaultdict

# ============================================================
# 配置区
# ============================================================

# 需要过滤的系统消息关键词
SYSTEM_KEYWORDS = [
    '以上是打招呼的消息',
    '我通过了你的朋友验证请求',
    '现在我们可以开始聊天了',
    '你已添加了',
    '对方已添加你',
    '你们已成功',
    '你发起了一笔转账',
    '对方发起了一笔转账',
    '[转发的聊天记录]',
]

# 需要过滤的消息内容模式（完全匹配）
SYSTEM_PATTERNS = [
    r'^\[表情包\]$',
    r'^\[图片\]$',
    r'^\[语音\]$',
    r'^\[视频\]$',
    r'^\[文件\]$',
    r'^\[链接\]$',
    r'^\[小程序\]$',
    r'^\[视频号\]$',
    r'^\[音乐\]$',
    r'^\[动画表情\]$',
    r'^\[红包\]$',
    r'^\[转账\]$',
    r'^\[名片\]$',
    r'^\[位置\]$',
    r'^\[语音通话\]$',
    r'^\[视频通话\]$',
    r'^\[聊天记录\]$',
    r'.*撤回了一条消息.*',
    # WeFlow 导出时的特殊格式残留
    r'^\[语音消息\]$',
    r'^语音消息$',
]

# 需要从消息内容中清除的残留（正则替换后用空字符串替换）
CLEANUP_PATTERNS = [
    (r'\[引用 .+?\]', ''),    # 微信引用回复标记
    (r'\.\.\/im[a-z]+\/', ''), # 图片路径残留
    (r'\.jpg$', ''),          # 图片扩展名
    (r'\.png$', ''),
    (r'\.gif$', ''),
]

# 最少消息长度（太短没分析价值）
MIN_MSG_LENGTH = 2


# ============================================================
# 解析 WeFlow TXT 格式
# ============================================================

def parse_weflow_txt(file_path, target_person=None):
    """
    解析 WeFlow 导出的 TXT 文件
    格式示例：
        2026-03-13 22:39:28 '我'
        你好

        2026-03-13 22:39:48 '陈琴农历9月23'
        好嘟
    """
    messages = []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # WeFlow 格式：时间戳行 + 内容行 + 空行
    # 时间戳行正则：2026-03-13 22:39:28 '说话人'
    header_pattern = re.compile(
        r"^(\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2}:\d{2})\s+'(.+)'$"
    )

    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n').rstrip('\r')

        # 尝试匹配时间戳行
        match = header_pattern.match(line)
        if match:
            timestamp = match.group(1)
            speaker = match.group(2)

            # 下一行是消息内容
            i += 1
            if i < len(lines):
                content = lines[i].rstrip('\n').rstrip('\r').strip()
            else:
                content = ''

            # 过滤系统消息和无效内容
            if is_valid_message(content):
                cleaned = clean_content(content)
                if not cleaned:
                    continue
                # 如果指定了目标人物，只保留那个人的发言
                if target_person:
                    if speaker == target_person:
                        messages.append({
                            'time': timestamp,
                            'speaker': speaker,
                            'content': cleaned,
                        })
                else:
                    messages.append({
                        'time': timestamp,
                        'speaker': speaker,
                        'content': cleaned,
                    })

            # 跳过多余空行
            i += 1
            while i < len(lines) and lines[i].strip() == '':
                i += 1
        else:
            i += 1

    return messages


# ============================================================
# 解析 WeChatMsg CSV 格式（兼容旧版）
# ============================================================

def parse_csv(input_file, target_person=None):
    """解析 WeChatMsg 导出的 CSV 格式"""
    import csv

    messages = []

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                msg_type = int(row.get('Type', 0))
                if msg_type != 1:  # 只保留文本消息
                    continue

                content = row.get('StrContent', '').strip()
                if not content:
                    continue

                speaker = row.get('StrTalker', '').strip()

                if target_person and speaker != target_person:
                    continue

                if not is_valid_message(content):
                    continue

                messages.append({
                    'time': row.get('CreateTime', ''),
                    'speaker': speaker,
                    'content': clean_content(content),
                })
            except (ValueError, KeyError):
                continue

    messages.sort(key=lambda x: x['time'])
    return messages


# ============================================================
# 清洗工具函数
# ============================================================

def clean_content(text):
    """清洗单条消息内容"""
    text = text.strip()
    # 应用清理模式
    for pattern, replacement in CLEANUP_PATTERNS:
        text = re.sub(pattern, replacement, text)
    # 清理多余空格
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def is_valid_message(content):
    """判断消息是否有效（过滤系统消息和无效内容）"""
    content = content.strip()

    if len(content) < MIN_MSG_LENGTH:
        return False

    # 检查完全匹配的系统模式
    for pattern in SYSTEM_PATTERNS:
        if re.match(pattern, content):
            return False

    # 检查系统关键词
    for keyword in SYSTEM_KEYWORDS:
        if keyword in content:
            return False

    # 纯数字/纯英文短消息过滤（无中文内容且太短）
    if not re.search(r'[一-鿿]', content) and len(content) <= 3:
        return False

    return True


# ============================================================
# 自动检测格式
# ============================================================

def auto_parse(input_path, target_person=None):
    """自动检测输入格式并解析"""
    suffix = input_path.suffix.lower()

    if suffix == '.csv':
        return parse_csv(input_path, target_person)
    elif suffix == '.txt':
        return parse_weflow_txt(input_path, target_person)
    else:
        # 尝试用 WeFlow 格式
        messages = parse_weflow_txt(input_path, target_person)
        if not messages:
            # 尝试 CSV
            messages = parse_csv(input_path, target_person)
        return messages


# ============================================================
# 批量处理目录
# ============================================================

def parse_directory(input_dir, target_person=None):
    """递归处理目录下所有 TXT 文件，合并结果"""
    all_messages = []
    input_path = Path(input_dir)

    if not input_path.is_dir():
        # 单个文件
        return auto_parse(input_path, target_person)

    # 递归查找所有 .txt 文件
    supported = list(input_path.glob('**/*.txt')) + list(input_path.glob('**/*.csv'))
    # 过滤掉 emojis、images、voices 目录
    supported = [f for f in supported if not any(p in str(f) for p in ['/emojis/', '/images/', '/voices/', '\\emojis\\', '\\images\\', '\\voices\\'])]
    if not supported:
        print(f'[!] 在 {input_dir} 中没有找到 .txt 或 .csv 文件')
        return []

    print(f'[+] 找到 {len(supported)} 个文件：')
    for f in supported:
        print(f'    - {f.name}')

    for file_path in supported:
        print(f'\n[*] 正在处理：{file_path.name}')
        try:
            msgs = auto_parse(file_path, target_person)
            print(f'    OK 提取 {len(msgs):,} 条有效消息')
            all_messages.extend(msgs)
        except Exception as e:
            print(f'    ERROR 解析失败：{e}')

    # 按时间排序
    all_messages.sort(key=lambda x: x['time'])

    # 去重（完全相同的消息只保留一条）
    seen = set()
    unique = []
    for m in all_messages:
        key = (m['time'], m['speaker'], m['content'])
        if key not in seen:
            seen.add(key)
            unique.append(m)

    return unique


# ============================================================
# 统计与输出
# ============================================================

def generate_statistics(messages):
    """生成基本统计信息"""
    if not messages:
        return {}

    stats = {
        'total_messages': len(messages),
        'total_chars': sum(len(m['content']) for m in messages),
        'avg_length': 0,
        'date_range': {
            'start': messages[0]['time'],
            'end': messages[-1]['time'],
        },
    }
    if stats['total_messages'] > 0:
        stats['avg_length'] = round(stats['total_chars'] / stats['total_messages'], 1)

    # 按月统计
    monthly = defaultdict(int)
    for m in messages:
        month_key = m['time'][:7]  # YYYY-MM
        monthly[month_key] += 1
    stats['monthly_breakdown'] = dict(sorted(monthly.items()))

    return stats


def main():
    parser = argparse.ArgumentParser(
        description='清洗微信聊天记录（支持 WeFlow TXT 和 WeChatMsg CSV 格式）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 模拟自己（处理 texts 目录下所有文件）
  python clean_chat.py -i data/raw/texts/ -p "我" -o data/clean/

  # 模拟别人（处理单个文件）
  python clean_chat.py -i data/raw/texts/私聊_陈琴.txt -p "陈琴农历9月23" -o data/clean/
        """
    )
    parser.add_argument('--input', '-i', required=True,
                        help='输入文件或目录路径')
    parser.add_argument('--person', '-p', type=str, default=None,
                        help='目标人物名称（只保留此人的发言）')
    parser.add_argument('--output', '-o', default='data/clean/',
                        help='输出目录（默认 data/clean/）')

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f'[ERROR] 路径不存在：{args.input}')
        return

    # 解析
    if input_path.is_dir():
        messages = parse_directory(input_path, args.person)
    else:
        print(f'[*] 正在读取：{input_path}')
        messages = auto_parse(input_path, args.person)

    if not messages:
        print('\n[!] 没有提取到任何有效消息，请检查：')
        print('   1. 文件格式是否正确')
        print('   2. --person 名称是否和文件中出现的一致（注意单引号和空格）')
        print('   3. 文件中是否包含文本消息')
        return

    # 统计
    stats = generate_statistics(messages)
    print(f'\n{"="*50}')
    print(f'[OK] 清洗完成！')
    print(f'{"="*50}')
    print(f'    有效消息数：{stats["total_messages"]:,} 条')
    print(f'    总字数：{stats["total_chars"]:,} 字')
    print(f'    平均每条：{stats["avg_length"]} 字')
    print(f'    时间范围：{stats["date_range"]["start"]} ~ {stats["date_range"]["end"]}')

    if stats.get('monthly_breakdown'):
        print(f'\n    每月消息数：')
        max_count = max(stats['monthly_breakdown'].values())
        for month, count in stats['monthly_breakdown'].items():
            bar_len = int(count / max_count * 30) if max_count > 0 else 0
            bar = '#' * bar_len
            print(f'      {month}: {count:>6,} 条 {bar}')

    # 保存
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # JSON
    json_path = output_dir / 'cleaned_messages.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    print(f'\n[SAVED] 数据已保存：{json_path}')

    # 纯文本（方便看）
    txt_path = output_dir / 'cleaned_messages.txt'
    with open(txt_path, 'w', encoding='utf-8') as f:
        for m in messages:
            f.write(f"{m['content']}\n")
    print(f'[SAVED] 纯文本版：{txt_path}')

    # 统计
    stats_path = output_dir / 'statistics.json'
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
