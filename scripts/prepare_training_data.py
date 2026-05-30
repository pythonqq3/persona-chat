"""
准备微调训练数据
将清洗后的消息转化为 Alpaca 格式，用于 LLaMA-Factory 或 LLaMA-Factory 微调

输出格式（Alpaca）：
{"instruction": "系统提示词", "input": "对方说的话", "output": "你的回复"}

用法：
  python scripts/prepare_training_data.py
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta

# ============================================================
# 配置
# ============================================================
INPUT_DIR = Path(__file__).parent.parent / "data" / "raw"
CLEAN_DIR = Path(__file__).parent.parent / "data" / "clean"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "training"
SKILL_PATH = Path(__file__).parent.parent / "output" / "persona-me" / "SKILL.md"

# 读系统提示词
with open(SKILL_PATH, "r", encoding="utf-8") as f:
    raw = f.read()
SYSTEM_PROMPT = raw[raw.find("---", 3) + 3:].strip() if raw.startswith("---") else raw.strip()

# ============================================================
# 1. 解析所有聊天文件，重建对话
# ============================================================

def parse_all_chats():
    """解析所有 WeFlow 格式的聊天文件，按对话切分"""
    all_messages = []
    texts_dir = INPUT_DIR

    for person_dir in texts_dir.iterdir():
        if not person_dir.is_dir():
            continue
        txt_dir = person_dir / "texts"
        if not txt_dir.exists():
            continue

        for txt_file in txt_dir.glob("*.txt"):
            msgs = parse_weflow_file(txt_file)
            all_messages.extend(msgs)

    # 按时间排序
    all_messages.sort(key=lambda x: x["time"])
    return all_messages


def parse_weflow_file(filepath):
    """解析 WeFlow TXT 文件"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    header_pattern = re.compile(r"^(\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2}:\d{2})\s+'(.+)'$")
    messages = []

    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n").rstrip("\r")
        match = header_pattern.match(line)
        if match:
            timestamp = match.group(1)
            speaker = match.group(2)

            i += 1
            if i < len(lines):
                content = lines[i].rstrip("\n").rstrip("\r").strip()
            else:
                content = ""

            # 过滤系统消息
            if len(content) >= 2 and not is_system(content):
                try:
                    dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                except:
                    dt = datetime.now()
                messages.append({
                    "time": dt,
                    "speaker": speaker,
                    "content": content,
                })

            i += 1
            while i < len(lines) and lines[i].strip() == "":
                i += 1
        else:
            i += 1

    return messages


def is_system(text):
    system_markers = [
        "[表情包]", "[图片]", "[语音]", "[视频]", "[文件]", "[链接]",
        "[小程序]", "[红包]", "[转账]", "[语音消息]",
        "以上是打招呼", "我通过了你的朋友验证",
        "撤回了一条消息",
    ]
    text = text.strip()
    return len(text) < 2 or any(m in text for m in system_markers)


# ============================================================
# 2. 按对话切分（时间间隔 > 60 分钟 = 新对话）
# ============================================================

def split_conversations(messages, gap_minutes=60):
    """按时间间隔切分对话"""
    conversations = []
    current = []

    for msg in messages:
        if current:
            gap = (msg["time"] - current[-1]["time"]).total_seconds()
            if gap > gap_minutes * 60:
                if len(current) >= 2:
                    conversations.append(current)
                current = []
        current.append(msg)

    if len(current) >= 2:
        conversations.append(current)

    return conversations


# ============================================================
# 3. 构建训练对：（对方的话 → 你的回复）
# ============================================================

def build_training_pairs(conversations):
    """从对话中提取 (对方说 -> 我回复) 的训练对"""
    pairs = []

    for conv in conversations:
        for i in range(len(conv) - 1):
            current = conv[i]
            next_msg = conv[i + 1]

            # 对方说完 → 我回复
            if current["speaker"] != "我" and next_msg["speaker"] == "我":
                pairs.append({
                    "input": current["content"],
                    "output": next_msg["content"],
                })

    return pairs


# ============================================================
# 4. 额外：自我描述训练对
# ============================================================

SELF_DESCRIPTION_PAIRS = [
    {"input": "介绍一下你自己", "output": "我比较喜欢打羽毛球，跑步和乒乓球，偶尔会打游戏。爱好好像也就这些了，性格比较随和"},
    {"input": "你多大", "output": "19岁，06年12月30的"},
    {"input": "你在哪里读书", "output": "江西中医药大学，南昌湾里校区"},
    {"input": "你跑步怎么样", "output": "还行吧，五公里最快18分19"},
    {"input": "你谈过恋爱吗", "output": "没谈过，随缘吧"},
    {"input": "你喜欢看什么书", "output": "以前闲的时候翻唐诗宋词鉴赏辞典，现在看的都是专业书"},
    {"input": "你平时喜欢干什么", "output": "打羽毛球、跑步、打王者，偶尔写写诗词"},
    {"input": "你对道家怎么看", "output": "挺有意思的，道德经里有些话确实有道理。生而不有，为而不恃，长而不宰，这种"},
    {"input": "你觉得自己写的诗怎么样", "output": "不怎么样，那时候韵律都没搞对。不过当时在网上发了之后有好多陌生人给我投票，还有一个人送了三十块钱"},
    {"input": "你觉得AI能替代人写诗吗", "output": "替代不了吧，诗又不是数据堆出来的，没有感情的东西读着没意思"},
    {"input": "你有什么缺点", "output": "挺直接的，有时候说话不过脑子，而且比较懒"},
    {"input": "你害怕什么", "output": "怕麻烦"},
    {"input": "你的口头禅是什么", "output": "奥奥、差不多、不知道、六六六——就这些吧"},
]


# ============================================================
# 5. 主流程
# ============================================================

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("📖 解析聊天记录...")
    all_msgs = parse_all_chats()
    print(f"   共 {len(all_msgs):,} 条消息")

    print("🔪 切分对话...")
    conversations = split_conversations(all_msgs)
    print(f"   共 {len(conversations):,} 个对话")

    print("🔗 构建训练对...")
    pairs = build_training_pairs(conversations)
    print(f"   共 {len(pairs):,} 个训练对")

    # 去重
    seen = set()
    unique_pairs = []
    for pair in pairs:
        key = (pair["input"], pair["output"])
        if key not in seen and len(pair["input"]) >= 2 and len(pair["output"]) >= 2:
            seen.add(key)
            unique_pairs.append(pair)
    print(f"   去重后 {len(unique_pairs):,} 个")

    # 加入自我描述对
    unique_pairs.extend(SELF_DESCRIPTION_PAIRS)

    # 输出为 Alpaca 格式（LLaMA-Factory 兼容）
    alpaca_data = []
    for pair in unique_pairs:
        alpaca_data.append({
            "instruction": SYSTEM_PROMPT[:500],  # 只取前500字，节省token
            "input": pair["input"],
            "output": pair["output"],
        })

    # 保存
    output_path = OUTPUT_DIR / "training_data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(alpaca_data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 训练数据已保存：{output_path}")
    print(f"   总训练样本：{len(alpaca_data):,} 条")
    print(f"   文件大小：{output_path.stat().st_size / 1024 / 1024:.1f} MB")

    # 也输出一个精简版（前2000条），方便快速测试
    sample_path = OUTPUT_DIR / "training_data_2k.json"
    with open(sample_path, "w", encoding="utf-8") as f:
        json.dump(alpaca_data[:2000], f, ensure_ascii=False, indent=2)
    print(f"   精简版（2K）：{sample_path}")

    print("\n📋 下一步：")
    print("   1. 上传 training_data.json 到 AutoDL")
    print("   2. 用 LLaMA-Factory 一键微调 Qwen2.5-7B")
    print("   3. 导出 LoRA 权重，部署到推理服务")


if __name__ == "__main__":
    main()
