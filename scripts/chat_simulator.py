"""
人格模拟对话脚本
功能：加载 SKILL.md 作为系统提示词，调用大模型 API 模拟和目标人物对话
用法：
  # 交互式对话
  python chat_simulator.py --skill output/persona-zhangsan/SKILL.md --api deepseek

  # 命令行单次提问
  python chat_simulator.py --skill output/persona-zhangsan/SKILL.md --ask "你今天干嘛了"

支持的 API：
  - deepseek: DeepSeek API（国内推荐，便宜：¥1/百万token）
  - claude: Anthropic Claude API
  - openai: OpenAI 及兼容 API（通义千问、GLM 等）
"""

import json
import argparse
import os
import re
import sys
from pathlib import Path


# ============================================================
# API 客户端（多后端支持）
# ============================================================

class DeepSeekClient:
    """DeepSeek API 客户端（国内低延迟+便宜）"""
    BASE_URL = "https://api.deepseek.com/v1/chat/completions"

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('DEEPSEEK_API_KEY')

    def chat(self, system_prompt, user_message, history=None, model="deepseek-chat"):
        import urllib.request
        import urllib.error

        messages = [{"role": "system", "content": system_prompt}]
        # 加入历史对话
        if history:
            messages.extend(history)
        # 加入当前消息
        messages.append({"role": "user", "content": user_message})

        body = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500,
        }).encode('utf-8')

        req = urllib.request.Request(self.BASE_URL, data=body, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        })

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                return result['choices'][0]['message']['content']
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise RuntimeError(f"API 请求失败 ({e.code})：{error_body}")


class ClaudeClient:
    """Anthropic Claude API 客户端"""
    BASE_URL = "https://api.anthropic.com/v1/messages"

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')

    def chat(self, system_prompt, user_message, model="claude-sonnet-4-6"):
        import urllib.request
        import urllib.error

        body = json.dumps({
            "model": model,
            "max_tokens": 500,
            "temperature": 0.7,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_message},
            ],
        }).encode('utf-8')

        req = urllib.request.Request(self.BASE_URL, data=body, headers={
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        })

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                return result['content'][0]['text']
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise RuntimeError(f"API 请求失败 ({e.code})：{error_body}")


def create_client(api_type):
    """根据类型创建对应的 API 客户端"""
    clients = {
        'deepseek': DeepSeekClient,
        'claude': ClaudeClient,
    }

    if api_type not in clients:
        raise ValueError(f'不支持的 API 类型：{api_type}。支持：{list(clients.keys())}')

    return clients[api_type]()


# ============================================================
# 对话模拟
# ============================================================

def clean_skill_content(raw_content):
    """去除 YAML frontmatter，提取 SKILL.md 正文"""
    # 匹配 YAML frontmatter
    if raw_content.startswith('---'):
        # 找到第二个 ---
        end_idx = raw_content.find('---', 3)
        if end_idx != -1:
            return raw_content[end_idx + 3:].strip()
    return raw_content.strip()


def build_system_prompt(skill_path):
    """从 SKILL.md 构建系统提示词"""
    skill_file = Path(skill_path)
    if not skill_file.exists():
        # 尝试在 output 目录下查找
        alt_path = Path('output') / skill_path / 'SKILL.md'
        if alt_path.exists():
            skill_file = alt_path
        else:
            raise FileNotFoundError(f'找不到 SKILL.md：{skill_path} (也尝试了 {alt_path})')

    with open(skill_file, 'r', encoding='utf-8') as f:
        raw = f.read()

    skill_body = clean_skill_content(raw)
    return skill_body


def chat_loop(client, system_prompt, persona_name="对方"):
    """交互式对话循环"""
    print(f'\n{"=" * 50}')
    print(f'[*] 正在和"{persona_name}"对话')
    print(f'   输入 "quit" 或 "退出" 结束对话')
    print(f'   输入 "reset" 或 "重置" 清空对话')
    print(f'{"=" * 50}\n')

    # 保持对话历史
    messages = [
        {"role": "system", "content": system_prompt},
    ]

    while True:
        try:
            user_input = input('[*] 你: ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\n[*] 对话结束')
            break

        if not user_input:
            continue

        if user_input.lower() in ('quit', '退出', 'q', 'exit'):
            print('[*] 对话结束')
            break

        if user_input.lower() in ('reset', '重置'):
            messages = [{"role": "system", "content": system_prompt}]
            print('[*] 对话已重置\n')
            continue

        # 添加用户消息到历史
        messages.append({"role": "user", "content": user_input})

        try:
            print(f'\n[*] {persona_name}: ', end='', flush=True)
            # 传入对话历史
            reply = client.chat(system_prompt, user_message=user_input, history=messages[1:])  # 跳过 system prompt
            print(f'{reply}\n')

            # 将回复加入历史
            messages.append({"role": "assistant", "content": reply})

        except RuntimeError as e:
            print(f'\n[ERROR] {e}\n')
        except Exception as e:
            print(f'\n[ERROR] 未知错误：{e}\n')


def single_ask(client, system_prompt, question, persona_name="对方"):
    """单次提问模式"""
    print(f'[*] {persona_name}: ', end='', flush=True)
    reply = client.chat(system_prompt, user_message=question)
    print(reply)
    return reply


# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='加载人格技能，与模拟对象对话')
    parser.add_argument('--skill', '-s', required=True, help='SKILL.md 文件路径，或 persona 名称')
    parser.add_argument('--api', '-a', choices=['deepseek', 'claude'], default='deepseek',
                        help='使用哪个 API（默认 deepseek）')
    parser.add_argument('--ask', '-q', type=str, default=None,
                        help='单次提问模式（如果不提供，则进入交互式对话）')
    parser.add_argument('--model', '-m', type=str, default=None,
                        help='指定模型（可选）')

    args = parser.parse_args()

    # 构建系统提示词
    try:
        system_prompt = build_system_prompt(args.skill)
    except FileNotFoundError as e:
        print(f'[ERROR] {e}')
        print('\n[*] 提示：SKILL.md 应该放在 output/persona-xxx/ 目录下')
        return

    # 提取 persona 名称
    persona_name = "对方"
    name_match = re.search(r'模拟 (.+?) 的说话风格', system_prompt)
    if name_match:
        persona_name = name_match.group(1)

    print(f'[*] 已加载人格技能：{persona_name}')
    print(f'[*] API 类型：{args.api}')

    # 创建客户端
    try:
        client = create_client(args.api)
    except ValueError as e:
        print(f'[ERROR] {e}')
        return

    if not client.api_key:
        env_var = 'DEEPSEEK_API_KEY' if args.api == 'deepseek' else 'ANTHROPIC_API_KEY'
        print(f'\n[!]  未设置 API Key！请先设置环境变量：')
        print(f'   export {env_var}="sk-xxx"')
        print(f'\n   或者在命令行指定：')
        print(f'   set {env_var}=sk-xxx  (Windows)')
        return

    # 开始对话
    if args.ask:
        single_ask(client, system_prompt, args.ask, persona_name)
    else:
        chat_loop(client, system_prompt, persona_name)


if __name__ == '__main__':
    main()
