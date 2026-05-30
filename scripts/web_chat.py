"""
网页版人格对话 — 基于 Streamlit
用法：
  pip install streamlit
  python -m streamlit run scripts/web_chat.py

首次运行前设置 API key：
  set DEEPSEEK_API_KEY=sk-xxx   (Windows)
  export DEEPSEEK_API_KEY=sk-xxx (Mac/Linux)
"""

import streamlit as st
import json
import urllib.request
import urllib.error
import os
import re
import time
from datetime import datetime
from pathlib import Path

# ============================================================
# 页面配置
# ============================================================

st.set_page_config(
    page_title="张仕达的数字分身",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 加载 SKILL.md
# ============================================================

@st.cache_data
def load_skill():
    skill_path = Path(__file__).parent.parent / "output" / "persona-me" / "SKILL.md"
    with open(skill_path, "r", encoding="utf-8") as f:
        raw = f.read()
    if raw.startswith("---"):
        end = raw.find("---", 3)
        return raw[end + 3:].strip(), raw[:end].strip()
    return raw.strip(), ""

SYSTEM_PROMPT, FRONTMATTER = load_skill()

# 提取 persona 名称
persona_name = "张仕达"
match = re.search(r"persona_name:\s*\"(.+?)\"", FRONTMATTER)
if match:
    persona_name = match.group(1)


# ============================================================
# Token 估算（粗略：中文约 1.5 字/token，英文约 4 字/token）
# ============================================================

def estimate_tokens(text):
    """粗略估算 token 数"""
    chinese_chars = len(re.findall(r'[一-鿿]', text))
    other_chars = len(text) - chinese_chars
    return int(chinese_chars / 1.5 + other_chars / 4)


def count_session_tokens(messages):
    """计算当前会话已使用的 token 数"""
    total = estimate_tokens(SYSTEM_PROMPT)
    for msg in messages:
        total += estimate_tokens(msg["content"])
    return total


# ============================================================
# DeepSeek API 调用
# ============================================================

def chat_deepseek(messages, api_key, model="deepseek-chat", temperature=0.7):
    """调用 DeepSeek API，返回 (回复内容, 实际消耗token数)"""
    body = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 400,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.deepseek.com/v1/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        content = result["choices"][0]["message"]["content"]
        usage = result.get("usage", {})
        return content, usage


# ============================================================
# 初始化 session state
# ============================================================

DEFAULTS = {
    "messages": [],
    "total_input_tokens": 0,
    "total_output_tokens": 0,
    "total_cost": 0.0,
}

for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ============================================================
# 侧边栏
# ============================================================

with st.sidebar:
    st.image("https://img.icons8.com/color/96/person-male--v1.png", width=60)
    st.title(f"张仕达的数字分身")

    # ---- API 设置 ----
    st.subheader("🔑 API 设置")
    api_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        value=os.environ.get("DEEPSEEK_API_KEY", ""),
        help="在 platform.deepseek.com 注册获取",
        placeholder="sk-xxxxxxxx",
    )

    col1, col2 = st.columns(2)
    with col1:
        model = st.selectbox(
            "模型",
            ["deepseek-chat", "deepseek-reasoner"],
            help="chat = 日常对话 / reasoner = 深度思考（更贵）",
        )
    with col2:
        temperature = st.slider(
            "随机度",
            min_value=0.0,
            max_value=1.5,
            value=0.7,
            step=0.1,
            help="越高越有创意，越低越稳定",
        )

    # ---- 统计 ----
    st.divider()
    st.subheader("📊 本次会话")

    msg_count = len(st.session_state.messages) // 2
    est_tokens = count_session_tokens(st.session_state.messages)
    real_cost = st.session_state.total_cost

    col1, col2, col3 = st.columns(3)
    col1.metric("对话轮数", msg_count)
    col2.metric("估算 Token", f"{est_tokens:,}")
    col3.metric("实际花费", f"¥{real_cost:.4f}")

    # ---- 功能按钮 ----
    st.divider()

    if st.button("🔄 清空对话", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_input_tokens = 0
        st.session_state.total_output_tokens = 0
        st.session_state.total_cost = 0
        st.rerun()

    # 导出对话
    if st.session_state.messages:
        export_text = ""
        for msg in st.session_state.messages:
            role_label = "你" if msg["role"] == "user" else persona_name
            export_text += f"{role_label}：{msg['content']}\n\n"

        st.download_button(
            label="📥 导出对话记录",
            data=export_text,
            file_name=f"聊天记录_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # ---- 关于 ----
    st.divider()
    with st.expander("ℹ️ 关于这个人格"):
        st.markdown(f"""
        **数据来源**：微信聊天记录
        **时间跨度**：2024.08 - 2026.05
        **消息数量**：24,060 条
        **对话对象**：6 个不同聊天窗口
        **人格版本**：V5
        **技术栈**：DeepSeek API + Streamlit
        """)

    st.caption("⚡ 每轮对话约 ¥0.005-0.01")


# ============================================================
# 主区域
# ============================================================

# 顶部
col_title, col_status = st.columns([3, 1])
with col_title:
    st.title(f"💬 和 {persona_name} 聊天")
with col_status:
    if api_key:
        st.success("🟢 已连接")
    else:
        st.warning("🟡 未设置 Key")

st.caption("一个 19 岁大学生 — 打羽毛球、写诗词、偶尔毒舌、会聊道家 | 输入区在页面底部")

# 快速提示
if not st.session_state.messages:
    st.info("💡 试试这些话题：最近在干嘛 · 羽毛球怎么练 · 你觉得道家的无为是什么意思 · 写首诗 · 你觉得人生的意义是什么")

# ---- 对话区域 ----
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ---- 输入区域 ----
st.divider()
input_col, hint_col = st.columns([5, 1])
with input_col:
    prompt = st.chat_input(
        "说点什么..." if st.session_state.messages else "开始聊天吧...",
        key="chat_input",
    )
with hint_col:
    if st.session_state.messages:
        last_msg = st.session_state.messages[-1]
        elapsed = ""
        st.caption(f"共 {len(st.session_state.messages)} 条消息")

# ---- 处理输入 ----
if prompt:
    if not api_key:
        st.error("❌ 请先在左侧边栏输入 DeepSeek API Key")
        st.info("👉 在 platform.deepseek.com 注册即可免费获取")
    else:
        # 显示用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 调用 API
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("*输入中...*")

            try:
                full_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                full_messages.extend(st.session_state.messages)

                reply, usage = chat_deepseek(full_messages, api_key, model, temperature)

                placeholder.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

                # 更新 token 统计
                if usage:
                    st.session_state.total_input_tokens += usage.get("prompt_tokens", 0)
                    st.session_state.total_output_tokens += usage.get("completion_tokens", 0)
                    # DeepSeek 价格：chat 模型 输入 ¥1/百万token 输出 ¥2/百万token
                    input_cost = usage.get("prompt_tokens", 0) / 1_000_000 * 1
                    output_cost = usage.get("completion_tokens", 0) / 1_000_000 * 2
                    st.session_state.total_cost += input_cost + output_cost

            except urllib.error.HTTPError as e:
                error_body = e.read().decode("utf-8") if e.fp else str(e)
                placeholder.error(f"API 错误 ({e.code})：{error_body[:200]}")
            except Exception as e:
                placeholder.error(f"出错了：{str(e)[:200]}")
                if "timeout" in str(e).lower():
                    st.info("💡 网络超时，请检查网络连接或换用其他模型")

        # 刷新以更新侧边栏统计
        st.rerun()
