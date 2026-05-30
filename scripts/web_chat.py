"""
网页版人格对话 — 基于 Streamlit
用法：
  pip install streamlit
  python -m streamlit run scripts/web_chat.py
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
    page_title="张仕达 · 数字分身",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "张仕达的数字分身 · 基于 24,000 条真实聊天记录",
    },
)

# ============================================================
# 自定义 CSS
# ============================================================
st.markdown("""
<style>
    /* === 全局 === */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* === 隐藏 Streamlit 默认元素 === */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* === 主区域 === */
    .main-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        border-radius: 16px;
        padding: 32px 40px;
        margin-bottom: 24px;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .main-header .name {
        font-size: 32px;
        font-weight: 700;
        background: linear-gradient(90deg, #a8c0ff, #c4b5fd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .main-header .tagline {
        font-size: 15px;
        color: #a0aec0;
        margin-top: 8px;
    }
    .main-header .tags {
        margin-top: 14px;
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }
    .main-header .tag {
        background: rgba(255,255,255,0.12);
        color: #d4d4f7;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 13px;
        backdrop-filter: blur(4px);
    }

    /* === 状态指示器 === */
    .status-badge {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 18px;
        border-radius: 12px;
        font-size: 14px;
        font-weight: 500;
        margin-left: auto;
    }
    .status-badge.online {
        background: rgba(52, 211, 153, 0.15);
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.3);
    }
    .status-badge.offline {
        background: rgba(251, 191, 36, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(251, 191, 36, 0.3);
    }
    .status-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    .status-dot.green { background: #34d399; }
    .status-dot.yellow { background: #fbbf24; }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }

    /* === 欢迎卡片 === */
    .welcome-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 12px;
        margin: 20px 0;
    }
    .welcome-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        transition: all 0.2s;
        cursor: default;
    }
    .welcome-card:hover {
        background: rgba(255,255,255,0.08);
        border-color: rgba(168, 192, 255, 0.3);
        transform: translateY(-2px);
    }
    .welcome-card .icon {
        font-size: 28px;
        margin-bottom: 8px;
    }
    .welcome-card .text {
        font-size: 13px;
        color: #a0aec0;
        line-height: 1.6;
    }

    /* === 聊天容器 === */
    .stChatMessage {
        border-radius: 12px !important;
    }

    /* === 侧边栏美化 === */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    [data-testid="stSidebar"] .stMetric {
        background: rgba(255,255,255,0.03);
        border-radius: 10px;
        padding: 10px 14px;
    }

    /* === 统计卡片 === */
    .stat-row {
        display: flex;
        gap: 8px;
        margin: 10px 0;
    }
    .stat-item {
        flex: 1;
        background: rgba(255,255,255,0.04);
        border-radius: 10px;
        padding: 14px 12px;
        text-align: center;
    }
    .stat-item .value {
        font-size: 22px;
        font-weight: 700;
        color: #a8c0ff;
    }
    .stat-item .label {
        font-size: 11px;
        color: #6b7280;
        margin-top: 4px;
    }

    /* === 按钮 === */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }

    /* === 展开项 === */
    [data-testid="stExpander"] {
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
    }

    /* === 输入框 === */
    [data-testid="stChatInput"] textarea {
        border-radius: 14px !important;
    }

    /* === 分割线 === */
    hr {
        border-color: rgba(255,255,255,0.06) !important;
    }
</style>
""", unsafe_allow_html=True)


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

persona_name = "张仕达"
match = re.search(r"persona_name:\s*\"(.+?)\"", FRONTMATTER)
if match:
    persona_name = match.group(1)


# ============================================================
# 工具函数
# ============================================================

def estimate_tokens(text):
    chinese_chars = len(re.findall(r'[一-鿿]', text))
    other_chars = len(text) - chinese_chars
    return int(chinese_chars / 1.5 + other_chars / 4)


def count_session_tokens(messages):
    total = estimate_tokens(SYSTEM_PROMPT)
    for msg in messages:
        total += estimate_tokens(msg["content"])
    return total


def chat_deepseek(messages, api_key, model="deepseek-chat", temperature=0.7):
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
# 初始化
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
    # Logo & 标题
    st.markdown("""
    <div style="text-align:center; margin-bottom:24px;">
        <div style="font-size:48px; margin-bottom:8px;">👤</div>
        <div style="font-size:20px; font-weight:700; color:#e0e0f0;">张仕达</div>
        <div style="font-size:13px; color:#6b7280; margin-top:4px;">数字分身 · V5</div>
    </div>
    """, unsafe_allow_html=True)

    # API 设置卡片
    with st.expander("🔑 API 设置", expanded=not os.environ.get("DEEPSEEK_API_KEY")):
        api_key = st.text_input(
            "DeepSeek 密钥",
            type="password",
            value=os.environ.get("DEEPSEEK_API_KEY", ""),
            placeholder="sk-xxxxxxxx",
            label_visibility="collapsed",
        )

        c1, c2 = st.columns(2)
        with c1:
            model = st.selectbox("模型", ["deepseek-chat", "deepseek-reasoner"],
                                 format_func=lambda x: "💬 日常" if "chat" in x else "🧠 深思")
        with c2:
            temperature = st.slider("创意度", 0.0, 1.5, 0.7, 0.1,
                                    help="越高越天马行空，越低越稳定")

    # 统计面板
    st.markdown("---")
    st.markdown('<p style="font-size:13px; font-weight:600; color:#a0aec0; margin-bottom:10px;">📊 会话统计</p>',
                unsafe_allow_html=True)

    msg_count = len(st.session_state.messages) // 2
    est_tokens = count_session_tokens(st.session_state.messages)
    real_cost = st.session_state.total_cost

    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-item">
            <div class="value">{msg_count}</div>
            <div class="label">轮对话</div>
        </div>
        <div class="stat-item">
            <div class="value">{est_tokens:,}</div>
            <div class="label">Token</div>
        </div>
        <div class="stat-item">
            <div class="value">¥{real_cost:.4f}</div>
            <div class="label">花费</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 操作按钮
    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 新对话", use_container_width=True):
            for key in DEFAULTS:
                st.session_state[key] = DEFAULTS[key]
            st.rerun()
    with col_b:
        if st.session_state.messages:
            export_text = "\n\n".join(
                f"{'你' if m['role'] == 'user' else persona_name}：{m['content']}"
                for m in st.session_state.messages
            )
            st.download_button("📥 导出", export_text,
                               f"聊天_{datetime.now().strftime('%m%d_%H%M')}.txt",
                               use_container_width=True)

    # 关于
    st.markdown("---")
    with st.expander("ℹ️ 关于"):
        st.markdown("""
        <div style="font-size:12px; color:#9ca3af; line-height:1.8;">
        📅 数据时间：2024.08 - 2026.05<br>
        💬 训练数据：24,060 条消息<br>
        👥 对话窗口：6 个<br>
        🧠 驱动模型：DeepSeek<br>
        ⚡ 单轮成本：约 ¥0.005
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# 主区域 - 顶部
# ============================================================

col_main, col_status = st.columns([4, 1])
with col_main:
    st.markdown("""
    <div class="main-header">
        <div class="name">张仕达</div>
        <div class="tagline">19 岁 · 大学生 · 打羽毛球 · 写诗词 · 偶尔毒舌</div>
        <div class="tags">
            <span class="tag">🏸 羽毛球</span>
            <span class="tag">📝 写诗词</span>
            <span class="tag">☯ 道家思想</span>
            <span class="tag">🎮 王者荣耀</span>
            <span class="tag">💻 编程</span>
            <span class="tag">🏃 跑步</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_status:
    if api_key:
        st.markdown("""
        <div class="status-badge online">
            <div class="status-dot green"></div> 分身在线
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-badge offline">
            <div class="status-dot yellow"></div> 未连接
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# 欢迎引导
# ============================================================

if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-grid">
        <div class="welcome-card">
            <div class="icon">🏸</div>
            <div class="text">问问羽毛球<br>怎么练</div>
        </div>
        <div class="welcome-card">
            <div class="icon">📝</div>
            <div class="text">让他写首诗<br>给你看</div>
        </div>
        <div class="welcome-card">
            <div class="icon">☯</div>
            <div class="text">聊聊道家<br>无为而治</div>
        </div>
        <div class="welcome-card">
            <div class="icon">💭</div>
            <div class="text">说说最近的<br>烦心事</div>
        </div>
        <div class="welcome-card">
            <div class="icon">🎮</div>
            <div class="text">约他打把<br>王者荣耀</div>
        </div>
        <div class="welcome-card">
            <div class="icon">🤔</div>
            <div class="text">问他怎么看<br>人生意义</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# 对话展示
# ============================================================

chat_placeholder = st.container()
with chat_placeholder:
    for msg in st.session_state.messages:
        avatar = "👤" if msg["role"] == "user" else None
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])


# ============================================================
# 输入处理
# ============================================================

prompt = st.chat_input("说点什么..." if st.session_state.messages else "你好，我是你的数字分身，想聊什么？")

if prompt:
    if not api_key:
        st.error("请在左侧「API 设置」中输入 DeepSeek 密钥")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("▊")

            try:
                full_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                full_messages.extend(st.session_state.messages)

                reply, usage = chat_deepseek(full_messages, api_key, model, temperature)

                placeholder.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

                if usage:
                    st.session_state.total_input_tokens += usage.get("prompt_tokens", 0)
                    st.session_state.total_output_tokens += usage.get("completion_tokens", 0)
                    input_cost = usage.get("prompt_tokens", 0) / 1_000_000 * 1
                    output_cost = usage.get("completion_tokens", 0) / 1_000_000 * 2
                    st.session_state.total_cost += input_cost + output_cost

            except urllib.error.HTTPError as e:
                code = e.code
                placeholder.error(f"API 请求失败（{code}）")
                if code == 401:
                    st.caption("密钥无效，请检查 API Key 是否正确")
                elif code == 402:
                    st.caption("账户余额不足，请前往 platform.deepseek.com 充值")
                elif code == 429:
                    st.caption("请求太频繁，稍等几秒再试")
            except Exception as e:
                placeholder.error(f"网络错误：{str(e)[:150]}")

        st.rerun()
