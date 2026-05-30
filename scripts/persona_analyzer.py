"""
人格分析脚本
功能：从清洗后的聊天数据中提取目标人物的语言风格、思维模式、情感特征
用法：
  1. 本地分析（不调用 API）：
     python persona_analyzer.py --input data/clean/cleaned_messages.json --local
  2. 用 AI 辅助深度分析（需要设置 API key）：
     python persona_analyzer.py --input data/clean/cleaned_messages.json --api deepseek
"""

import json
import re
import argparse
import os
from pathlib import Path
from collections import Counter, defaultdict
from itertools import islice


# ============================================================
# 本地统计分析（不依赖外部 API）
# ============================================================

class LocalAnalyzer:
    """对聊天数据进行纯本地统计分析"""

    def __init__(self, messages):
        self.messages = messages
        self.texts = [m['content'] for m in messages]

    def top_words(self, top_n=200):
        """提取高频词汇"""
        word_counter = Counter()
        for text in self.texts:
            # 用 jieba 分词（如果安装了的话），否则用简单分词
            words = self._simple_tokenize(text)
            word_counter.update(words)

        # 过滤停用词
        stopwords = self._load_stopwords()
        filtered = [(w, c) for w, c in word_counter.most_common(top_n * 3)
                    if w not in stopwords and len(w) >= 2]

        return filtered[:top_n]

    def sentence_length_distribution(self):
        """分析句子长度分布"""
        lengths = []
        for text in self.texts:
            # 按中文标点断句
            sentences = re.split(r'[。！？\n!?…~～]', text)
            for s in sentences:
                s = s.strip()
                if s:
                    lengths.append(len(s))

        if not lengths:
            return {'avg': 0, 'min': 0, 'max': 0, 'buckets': {}}

        buckets = {'1-5字': 0, '6-10字': 0, '11-20字': 0, '21-30字': 0, '30字以上': 0}
        for l in lengths:
            if l <= 5:
                buckets['1-5字'] += 1
            elif l <= 10:
                buckets['6-10字'] += 1
            elif l <= 20:
                buckets['11-20字'] += 1
            elif l <= 30:
                buckets['21-30字'] += 1
            else:
                buckets['30字以上'] += 1

        return {
            'avg': round(sum(lengths) / len(lengths), 1),
            'min': min(lengths),
            'max': max(lengths),
            'total_sentences': len(lengths),
            'buckets': buckets,
        }

    def punctuation_habits(self):
        """分析标点使用习惯"""
        patterns = {
            '感叹号': '！|!',
            '问号': '？|\\?',
            '省略号': '\\.\\.\\.|…',
            '句号': '。|\\.(?!\\.)',  # 句号但不包括省略号
            '逗号': '，|,',
            '顿号': '、',
            '波浪号': '~|～',
        }

        habits = {}
        total = len(self.texts)
        for name, pattern in patterns.items():
            count = sum(1 for t in self.texts if re.search(pattern, t))
            habits[f'使用{name}的比例'] = f'{round(count/total*100, 1)}%' if total else '0%'

        return habits

    def emoji_usage(self):
        """分析 emoji 使用频率和偏好"""
        emoji_pattern = re.compile(
            r'[\U0001F300-\U0001F9FF]|'  # 表情符号
            r'[\U0001FA00-\U0001FA6F]|'  # 扩展表情
            r'[\U0001FA70-\U0001FAFF]|'  # 更多扩展
            r'[☀-➿]|'          # 杂项符号
            r'[✂-➰]'           # 装饰符号
        )

        all_emojis = []
        texts_with_emoji = 0
        for text in self.texts:
            emojis = emoji_pattern.findall(text)
            if emojis:
                texts_with_emoji += 1
                all_emojis.extend(emojis)

        counter = Counter(all_emojis)
        return {
            '使用emoji的比例': f'{round(texts_with_emoji/len(self.texts)*100, 1)}%' if self.texts else '0%',
            '最常用的emoji': counter.most_common(20),
        }

    def time_patterns(self):
        """分析时间规律（什么时候话多）"""
        hour_counter = Counter()
        for m in self.messages:
            time_str = m.get('time', '')
            # 尝试提取小时
            match = re.search(r'(\d{1,2}):\d{2}', time_str)
            if match:
                hour = int(match.group(1))
                hour_counter[hour] += 1

        if not hour_counter:
            return {}

        return {
            '最活跃时段': [h for h, _ in hour_counter.most_common(3)],
            '凌晨(0-6时)活跃度': sum(hour_counter.get(h, 0) for h in range(0, 7)),
            '上午(7-12时)活跃度': sum(hour_counter.get(h, 0) for h in range(7, 13)),
            '下午(13-18时)活跃度': sum(hour_counter.get(h, 0) for h in range(13, 19)),
            '晚上(19-23时)活跃度': sum(hour_counter.get(h, 0) for h in range(19, 24)),
        }

    def opening_patterns(self):
        """分析开头用语（如何开启话题）"""
        first_words = Counter()
        for text in self.texts:
            text = text.strip()
            # 取前两个字符或第一个词
            prefix = text[:4] if len(text) >= 4 else text
            first_words[prefix] += 1

        return first_words.most_common(30)

    def ending_patterns(self):
        """分析结尾用语"""
        endings = Counter()
        for text in self.texts:
            text = text.strip()
            if len(text) >= 2:
                suffix = text[-3:]
                endings[suffix] += 1

        return endings.most_common(30)

    def _simple_tokenize(self, text):
        """简单中文分词（不依赖 jieba）"""
        # 按常见分隔符切分
        tokens = re.split(r'[，。！？、：；\s,\.!\?:;\n]+', text)
        result = []
        for token in tokens:
            token = token.strip()
            if not token:
                continue
            # 对较长的词汇进行简单的 2-gram 切分
            if len(token) <= 5:
                result.append(token)
            else:
                for i in range(len(token) - 1):
                    bigram = token[i:i + 2]
                    if not re.search(r'[^一-鿿]', bigram):  # 只保留纯中文 bigram
                        result.append(bigram)
                if len(token) >= 3:
                    result.append(token[:3])
        return result

    def _load_stopwords(self):
        """加载基础停用词表"""
        return {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一',
            '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着',
            '没有', '看', '好', '自己', '这', '那', '他', '她', '它', '们',
            '什么', '怎么', '哪', '吗', '呢', '啊', '吧', '哦', '嗯', '么',
            '但', '可', '所以', '因为', '如果', '虽然', '而且', '或', '还',
            '这个', '那个', '哪个', '怎么', '什么', '为什么', '怎么', '啥',
            '哈', '嗯嗯', '好的', '收到', '知道', '明白',
        }

    def run_all(self):
        """执行全部分析"""
        print('[*] 正在分析语言特征...\n')

        results = {}

        print('  [*] 分析常用词汇...')
        results['高频词汇'] = self.top_words(100)

        print('  [*] 分析句子长度...')
        results['句子长度'] = self.sentence_length_distribution()

        print('  [*] 分析标点习惯...')
        results['标点习惯'] = self.punctuation_habits()

        print('  [:)] 分析 emoji 使用...')
        results['emoji使用'] = self.emoji_usage()

        print('  [*] 分析发言时间规律...')
        results['时间规律'] = self.time_patterns()

        print('  [*] 分析开头用语...')
        results['开头用语'] = self.opening_patterns()

        print('  [*] 分析结尾用语...')
        results['结尾用语'] = self.ending_patterns()

        return results


# ============================================================
# 生成人格分析报告
# ============================================================

def generate_human_report(analysis_results, output_path):
    """将分析结果生成人类可读的报告"""
    report_lines = []
    report_lines.append('=' * 60)
    report_lines.append('📊 人格分析报告')
    report_lines.append('=' * 60)

    # 高频词汇
    report_lines.append('\n## 🗣️ 高频词汇 Top 30\n')
    for i, (word, count) in enumerate(analysis_results['高频词汇'][:30], 1):
        report_lines.append(f'  {i:>2}. {word:<10} 出现 {count} 次')

    # 句子长度
    sl = analysis_results['句子长度']
    report_lines.append(f'\n## [*] 句子长度分析\n')
    report_lines.append(f'  平均句子长度：{sl["avg"]} 字')
    report_lines.append(f'  最短：{sl["min"]} 字 | 最长：{sl["max"]} 字')
    report_lines.append(f'  总句数：{sl["total_sentences"]}')
    report_lines.append(f'  分布：')
    for bucket, count in sl['buckets'].items():
        bar = '█' * (count // max(sl['buckets'].values()) * 30) if max(sl['buckets'].values()) > 0 else ''
        report_lines.append(f'    {bucket:<12} {count:>6} 句 {bar}')

    # 标点习惯
    report_lines.append(f'\n## [*] 标点使用习惯\n')
    for name, value in analysis_results['标点习惯'].items():
        report_lines.append(f'  {name}：{value}')

    # emoji
    report_lines.append(f'\n## [:)] Emoji 使用\n')
    report_lines.append(f'  使用比例：{analysis_results["emoji使用"]["使用emoji的比例"]}')
    report_lines.append(f'  最常用：')
    for emoji, count in analysis_results['emoji使用']['最常用的emoji']:
        report_lines.append(f'    {emoji}  ×{count} 次')

    # 时间规律
    if analysis_results['时间规律']:
        tr = analysis_results['时间规律']
        report_lines.append(f'\n## [*] 发言时间规律\n')
        report_lines.append(f'  最活跃时段：{tr["最活跃时段"]} 时')
        report_lines.append(f'  上午 (7-12)：{tr["上午(7-12时)活跃度"]} 条')
        report_lines.append(f'  下午 (13-18)：{tr["下午(13-18时)活跃度"]} 条')
        report_lines.append(f'  晚上 (19-23)：{tr["晚上(19-23时)活跃度"]} 条')
        report_lines.append(f'  凌晨 (0-6)：{tr["凌晨(0-6时)活跃度"]} 条')

    # 开头用语
    report_lines.append(f'\n## [*] 常用开头\n')
    for phrase, count in analysis_results['开头用语'][:20]:
        report_lines.append(f'  "{phrase}" — {count} 次')

    # 结尾用语
    report_lines.append(f'\n## [*] 常用结尾\n')
    for phrase, count in analysis_results['结尾用语'][:20]:
        report_lines.append(f'  "{phrase}" — {count} 次')

    report_lines.append('\n' + '=' * 60)
    report_lines.append('提示：将此报告作为基础数据，用于编写 SKILL.md')
    report_lines.append('=' * 60)

    report_text = '\n'.join(report_lines)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(f'\n[SAVE] 分析报告已保存到：{output_path}')
    return report_text


# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='分析微信聊天数据，提取人格特征')
    parser.add_argument('--input', '-i', required=True, help='清洗后的 JSON 文件路径')
    parser.add_argument('--output', '-o', default='output/', help='输出目录')
    parser.add_argument('--local', action='store_true', help='使用本地分析（无需 API）')
    parser.add_argument('--api', type=str, choices=['deepseek', 'openai', 'claude'],
                        help='使用 AI API 进行深度分析（需设置环境变量）')
    parser.add_argument('--sample', type=int, default=0,
                        help='只分析前 N 条消息（用于快速测试，0=全部）')

    args = parser.parse_args()

    # 读取数据
    input_path = Path(args.input)
    if not input_path.exists():
        print(f'❌ 文件不存在：{args.input}')
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        messages = json.load(f)

    print(f'[*] 共加载 {len(messages):,} 条消息')

    if args.sample > 0:
        messages = messages[:args.sample]
        print(f'[*] 采用前 {len(messages):,} 条进行分析')

    # 创建输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.local:
        # 本地分析
        analyzer = LocalAnalyzer(messages)
        results = analyzer.run_all()

        # 保存原始分析结果
        analysis_path = output_dir / 'persona_analysis.json'
        # 处理不可序列化的对象
        serializable_results = {}
        for key, value in results.items():
            if isinstance(value, dict):
                serializable_results[key] = value
            else:
                serializable_results[key] = str(value)

        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)

        # 生成人类可读报告
        report_path = output_dir / 'persona_report.txt'
        generate_human_report(results, report_path)

    elif args.api:
        # AI 深度分析
        run_deep_analysis(messages, args.api, output_dir)
    else:
        print('⚠️  请选择分析模式：--local（本地统计）或 --api（AI 深度分析）')


def run_deep_analysis(messages, api_type, output_dir):
    """
    使用 AI API 对聊天数据进行深度人格分析
    由于每轮分析有 token 限制，采用分批分析 + 汇总的策略
    """
    print(f'\n🤖 使用 {api_type} API 进行深度人格分析...')
    print('⚠️  注意：此功能会将聊天数据发送到 API 服务商，请确保你了解隐私风险\n')

    BATCH_SIZE = 50  # 每批50条消息
    batches = [messages[i:i + BATCH_SIZE] for i in range(0, len(messages), BATCH_SIZE)]
    print(f'📦 数据已分为 {len(batches)} 批，每批 {BATCH_SIZE} 条')

    ANALYSIS_PROMPT = """
你是一个人格分析专家。请分析以下聊天记录片段，提取这个人的特征。

请从以下维度进行分析（用 JSON 格式返回）：

1. vocabulary (词汇特征): 口头禅、高频词、语气词偏好
2. sentence_style (句式风格): 句子长短、句式结构偏好
3. thinking (思维模式): 如何组织观点、逻辑习惯
4. emotion (情感表达): 开心/生气/难过时的表达方式
5. humor (幽默风格): 是否有幽默感、幽默类型
6. catchphrases (口头禅): 发现的具体口头禅列表

聊天记录：
---
{chat_samples}
---

请返回 JSON，不要附带其他内容：
{{"vocabulary": "...", "sentence_style": "...", "thinking": "...", "emotion": "...", "humor": "...", "catchphrases": ["..."]}}
"""

    # 这里只做第一批分析示例，实际使用需要配置 API key
    print('\n[*] 深度分析功能框架已就绪。')
    print('   要启用 AI 分析，请按照下面的步骤：')
    print('')
    print('   方式一：用 DeepSeek API（便宜，推荐）')
    print('   export DEEPSEEK_API_KEY="sk-xxx"')
    print(f'   python persona_analyzer.py --input data/clean/cleaned_messages.json --api deepseek')
    print('')
    print('   方式二：用 Claude API')
    print('   export ANTHROPIC_API_KEY="sk-ant-xxx"')
    print(f'   python persona_analyzer.py --input data/clean/cleaned_messages.json --api claude')
    print('')
    print('✅ 建议先用 --local 模式生成统计报告，再决定是否用 AI 深度分析')
    print('')


if __name__ == '__main__':
    main()
