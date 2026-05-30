"""
网页版人格对话 — 带登录注册
用法：
  pip install streamlit
  python -m streamlit run scripts/web_chat.py

Streamlit Cloud Secrets 配置：
  DEEPSEEK_API_KEY = "sk-xxx"
  authorized_users = "zhangshida:hashed_pw, friend1:hashed_pw"
"""

import streamlit as st
import json
import urllib.request
import urllib.error
import os
import re
import hashlib
import secrets as rand_secrets
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
    menu_items={"Get Help": None, "Report a bug": None, "About": "张仕达的数字分身"},
)

# ============================================================
# CSS 样式
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    .main-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        border-radius: 16px; padding: 28px 36px; margin-bottom: 20px;
        color: white; box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .main-header .name {
        font-size: 28px; font-weight: 700;
        background: linear-gradient(90deg, #a8c0ff, #c4b5fd);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .main-header .tagline { font-size: 14px; color: #a0aec0; margin-top: 6px; }
    .main-header .tags { margin-top: 12px; display: flex; gap: 8px; flex-wrap: wrap; }
    .main-header .tag {
        background: rgba(255,255,255,0.1); color: #d4d4f7;
        padding: 4px 12px; border-radius: 16px; font-size: 12px;
    }

    .status-badge {
        display: flex; align-items: center; gap: 8px;
        padding: 10px 16px; border-radius: 12px; font-size: 13px; font-weight: 500;
    }
    .status-badge.online { background: rgba(52,211,153,0.12); color: #34d399; border: 1px solid rgba(52,211,153,0.25); }
    .status-badge.offline { background: rgba(251,191,36,0.12); color: #fbbf24; border: 1px solid rgba(251,191,36,0.25); }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; animation: pulse 2s infinite; }
    .status-dot.green { background: #34d399; }
    .status-dot.yellow { background: #fbbf24; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

    .welcome-grid {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 10px; margin: 16px 0;
    }
    .welcome-card {
        background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px; padding: 16px; text-align: center;
        transition: all 0.2s; cursor: default;
    }
    .welcome-card:hover { background: rgba(255,255,255,0.06); transform: translateY(-2px); }
    .welcome-card .icon { font-size: 26px; margin-bottom: 6px; }
    .welcome-card .text { font-size: 12px; color: #a0aec0; line-height: 1.6; }

    .stat-row { display: flex; gap: 8px; margin: 8px 0; }
    .stat-item {
        flex: 1; background: rgba(255,255,255,0.03);
        border-radius: 8px; padding: 12px 10px; text-align: center;
    }
    .stat-item .value { font-size: 20px; font-weight: 700; color: #a8c0ff; }
    .stat-item .label { font-size: 10px; color: #6b7280; margin-top: 2px; }

    /* 登录卡片 */
    .login-card {
        max-width: 420px; margin: 60px auto;
        background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px; padding: 40px 36px; text-align: center;
    }
    .login-card h2 {
        font-size: 24px; font-weight: 700; color: #e0e0f0; margin-bottom: 6px;
    }
    .login-card .sub { font-size: 13px; color: #6b7280; margin-bottom: 24px; }

    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0f0f1a, #1a1a2e); border-right: 1px solid rgba(255,255,255,0.06); }
    hr { border-color: rgba(255,255,255,0.06) !important; }
    .stButton > button { border-radius: 10px !important; font-weight: 500 !important; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 密码工具
# ============================================================

def hash_password(password: str) -> str:
    """SHA256 哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


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

# ============================================================
# 加载授权用户
# ============================================================

def load_authorized_users():
    """从 secrets 或本地文件加载授权用户列表"""
    users = {}
    # 先尝试 Streamlit secrets
    try:
        auth_str = st.secrets.get("authorized_users", "")
        if auth_str:
            for entry in auth_str.split(","):
                entry = entry.strip()
                if ":" in entry:
                    username, password_hash = entry.split(":", 1)
                    users[username.strip()] = password_hash.strip()
            return users
    except Exception:
        pass
    return users


AUTHORIZED_USERS = load_authorized_users()


def load_admin_users():
    """加载管理员列表"""
    try:
        admin_str = st.secrets.get("admin_users", "")
        if admin_str:
            return set(u.strip() for u in admin_str.split(",") if u.strip())
    except Exception:
        pass
    return set()


ADMIN_USERS = load_admin_users()


def get_default_api_key():
    """获取默认 API Key"""
    try:
        return st.secrets.get("DEEPSEEK_API_KEY", "")
    except Exception:
        return os.environ.get("DEEPSEEK_API_KEY", "")


DEFAULT_API_KEY = get_default_api_key()


# ============================================================
# API 调用
# ============================================================

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
        return result["choices"][0]["message"]["content"], result.get("usage", {})


# ============================================================
# 初始化 session state
# ============================================================

DEFAULTS = {
    "logged_in": False,
    "username": "",
    "is_admin": False,
    "is_authorized": False,
    "user_api_key": "",
    "messages": [],
    "total_input_tokens": 0,
    "total_output_tokens": 0,
    "total_cost": 0.0,
    "login_mode": "login",
    "login_error": "",
}
for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ============================================================
# 获取当前有效的 API Key
# ============================================================

def get_active_api_key():
    """授权用户用默认 key，其他用户用自己的 key"""
    if st.session_state.is_authorized:
        return DEFAULT_API_KEY
    return st.session_state.user_api_key or DEFAULT_API_KEY


# ============================================================
# 登出
# ============================================================

def logout():
    for key in DEFAULTS:
        st.session_state[key] = DEFAULTS[key]
    st.rerun()


# ============================================================
# ========== 登录/注册页面 ==========
# ============================================================

def show_auth_page():
    st.markdown("""
    <div style="text-align:center; padding-top:40px;">
        <div style="font-size:56px;">👤</div>
        <div style="font-size:28px; font-weight:700; color:#e0e0f0; margin-top:12px;">张仕达的数字分身</div>
        <div style="font-size:14px; color:#6b7280; margin-top:6px;">基于 24,000 条真实聊天记录训练</div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 1.2, 1])

    with col_m:
        mode = st.session_state.login_mode

        if mode == "login":
            st.markdown("### 登录")
            username = st.text_input("用户名", key="login_user", placeholder="输入用户名")
            password = st.text_input("密码", type="password", key="login_pass", placeholder="输入密码")

            err_placeholder = st.empty()

            c1, c2 = st.columns(2)
            with c1:
                if st.button("登录", use_container_width=True, type="primary"):
                    if not username or not password:
                        st.session_state.login_error = "请填写用户名和密码"
                        st.rerun()
                    elif username in AUTHORIZED_USERS:
                        if AUTHORIZED_USERS[username] == hash_password(password):
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.is_authorized = True
                            st.session_state.is_admin = username in ADMIN_USERS
                            st.session_state.login_error = ""
                            st.rerun()
                        else:
                            st.session_state.login_error = "密码错误"
                            st.rerun()
                    else:
                        st.session_state.login_error = "用户名不存在，请先注册"
                        st.rerun()

            with c2:
                if st.button("注册新账号", use_container_width=True):
                    st.session_state.login_mode = "register"
                    st.session_state.login_error = ""
                    st.rerun()

            if st.session_state.login_error:
                err_placeholder.error(st.session_state.login_error)

            st.caption("授权用户登录后可使用默认 API，无需自己填 Key")

        else:  # register
            st.markdown("### 注册")
            new_username = st.text_input("设置用户名", key="reg_user", placeholder="3-20 个字符")
            new_password = st.text_input("设置密码", type="password", key="reg_pass", placeholder="至少 6 位")
            confirm_password = st.text_input("确认密码", type="password", key="reg_confirm", placeholder="再次输入密码")

            st.markdown("---")
            st.caption("非授权用户需自备 DeepSeek API Key")
            own_api_key = st.text_input(
                "API Key（选填）",
                type="password",
                key="reg_api",
                placeholder="sk-xxxxxxxx，授权用户可跳过",
            )

            err_placeholder = st.empty()

            c1, c2 = st.columns(2)
            with c1:
                if st.button("注册", use_container_width=True, type="primary"):
                    error = None
                    if not new_username or len(new_username) < 3:
                        error = "用户名至少 3 个字符"
                    elif not new_password or len(new_password) < 6:
                        error = "密码至少 6 位"
                    elif new_password != confirm_password:
                        error = "两次密码不一致"
                    elif new_username in AUTHORIZED_USERS:
                        error = "此用户名已被预留，请换一个"
                    elif not own_api_key and not DEFAULT_API_KEY:
                        error = "请填写 API Key（在 platform.deepseek.com 获取）"

                    if error:
                        st.session_state.login_error = error
                        st.rerun()
                    else:
                        st.session_state.logged_in = True
                        st.session_state.username = new_username
                        st.session_state.is_authorized = False
                        st.session_state.user_api_key = own_api_key
                        st.session_state.login_error = ""
                        st.rerun()

            with c2:
                if st.button("返回登录", use_container_width=True):
                    st.session_state.login_mode = "login"
                    st.session_state.login_error = ""
                    st.rerun()

            if st.session_state.login_error:
                err_placeholder.error(st.session_state.login_error)

            st.caption("授权用户请联系张仕达添加账号")


# ============================================================
# ========== 聊天主页 ==========
# ============================================================

def estimate_tokens(text):
    chinese = len(re.findall(r'[一-鿿]', text))
    return int(chinese / 1.5 + (len(text) - chinese) / 4)


def count_session_tokens(messages):
    total = estimate_tokens(SYSTEM_PROMPT)
    for m in messages:
        total += estimate_tokens(m["content"])
    return total


def show_chat_page():
    api_key = get_active_api_key()
    username = st.session_state.username
    is_auth = st.session_state.is_authorized
    is_admin = st.session_state.is_admin

    # ====== 侧边栏 ======
    with st.sidebar:
        # 头像区
        role_badge = "👑 管理员" if is_admin else ("🔓 授权用户" if is_auth else "📝 访客")
        role_color = "#fbbf24" if is_admin else ("#34d399" if is_auth else "#6b7280")
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:20px;">
            <div style="font-size:40px;">{'👑' if is_admin else '👤'}</div>
            <div style="font-size:18px; font-weight:700; color:#e0e0f0;">{username}</div>
            <div style="font-size:12px; color:{role_color}; margin-top:2px;">{role_badge}</div>
        </div>
        """, unsafe_allow_html=True)

        # API 设置区域
        if is_admin:
            with st.expander("🔑 API 管理（管理员可见）", expanded=False):
                st.text_input("默认 API Key", value=DEFAULT_API_KEY[:8] + "***" + DEFAULT_API_KEY[-4:],
                              disabled=True, label_visibility="collapsed")
                st.caption("完整 Key 存储在服务器密钥中，不可导出")
                if st.button("🔄 刷新 Key 状态", use_container_width=True):
                    st.rerun()

        elif is_auth:
            with st.expander("🔑 API 状态", expanded=False):
                st.success("✅ 已自动配置，无需手动填写")
                st.caption("🔒 密钥已加密存储，不可查看")

        else:
            with st.expander("🔑 API 设置", expanded=not st.session_state.user_api_key):
                custom_key = st.text_input(
                    "你的 DeepSeek Key",
                    type="password",
                    value=st.session_state.user_api_key,
                    placeholder="sk-xxxxxxxx",
                    label_visibility="collapsed",
                )
                if custom_key != st.session_state.user_api_key:
                    st.session_state.user_api_key = custom_key
                st.caption("在 platform.deepseek.com 免费获取")

        # 模型
        with st.expander("⚙️ 对话设置", expanded=False):
            model = st.selectbox("模型", ["deepseek-chat", "deepseek-reasoner"],
                                 format_func=lambda x: "💬 日常对话" if "chat" in x else "🧠 深度思考",
                                 key="sidebar_model")
            temperature = st.slider("创意度", 0.0, 1.5, 0.7, 0.1, key="sidebar_temp")

        # 统计
        st.markdown("---")
        st.caption("📊 本次会话")
        msg_count = len(st.session_state.messages) // 2
        est_tokens = count_session_tokens(st.session_state.messages)
        real_cost = st.session_state.total_cost

        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-item"><div class="value">{msg_count}</div><div class="label">轮对话</div></div>
            <div class="stat-item"><div class="value">{est_tokens:,}</div><div class="label">Token</div></div>
            <div class="stat-item"><div class="value">¥{real_cost:.4f}</div><div class="label">花费</div></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔄 新对话", use_container_width=True):
                st.session_state.messages = []
                st.session_state.total_input_tokens = 0
                st.session_state.total_output_tokens = 0
                st.session_state.total_cost = 0.0
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

        st.markdown("---")
        if st.button("🚪 退出登录", use_container_width=True):
            logout()

        st.markdown("---")
        st.caption(f"⚡ 驱动：DeepSeek · 人格模型 V5")
        if is_auth:
            st.caption("🔒 API Key 已加密存储，不可查看")

    # ====== 主区域 ======
    col_main, col_status = st.columns([4, 1])
    with col_main:
        st.markdown("""
        <div class="main-header">
            <div class="name">张仕达</div>
            <div class="tagline">19 岁 · 大学生 · 打羽毛球 · 写诗词 · 偶尔毒舌</div>
            <div class="tags">
                <span class="tag">🏸 羽毛球</span><span class="tag">📝 写诗词</span>
                <span class="tag">☯ 道家思想</span><span class="tag">🎮 王者荣耀</span>
                <span class="tag">💻 编程</span><span class="tag">🏃 跑步</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_status:
        active_key = get_active_api_key()
        if active_key:
            st.markdown("""
            <div class="status-badge online">
                <div class="status-dot green"></div> 分身在线
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-badge offline">
                <div class="status-dot yellow"></div> 未配置 Key
            </div>
            """, unsafe_allow_html=True)

    # 欢迎引导
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-grid">
            <div class="welcome-card"><div class="icon">🏸</div><div class="text">问问羽毛球<br>怎么练</div></div>
            <div class="welcome-card"><div class="icon">📝</div><div class="text">让他写首诗<br>给你看</div></div>
            <div class="welcome-card"><div class="icon">☯</div><div class="text">聊聊道家<br>无为而治</div></div>
            <div class="welcome-card"><div class="icon">💭</div><div class="text">说说最近的<br>烦心事</div></div>
            <div class="welcome-card"><div class="icon">🎮</div><div class="text">约他打把<br>王者荣耀</div></div>
            <div class="welcome-card"><div class="icon">🤔</div><div class="text">问他怎么看<br>人生意义</div></div>
        </div>
        """, unsafe_allow_html=True)

    # 对话展示
    for msg in st.session_state.messages:
        avatar = "👤" if msg["role"] == "user" else None
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # 输入
    prompt = st.chat_input(
        "说点什么..." if st.session_state.messages else f"你好 {username}，想聊什么？"
    )

    if prompt:
        if not api_key:
            st.error("请先在侧边栏配置 API Key")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                placeholder = st.empty()
                placeholder.markdown("▊")

                try:
                    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                    full_messages.extend(st.session_state.messages)

                    reply, usage = chat_deepseek(full_messages, api_key,
                                                 st.session_state.get("sidebar_model", "deepseek-chat"),
                                                 st.session_state.get("sidebar_temp", 0.7))

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
                    if code == 401:
                        placeholder.error("密钥无效，请检查 API Key")
                    elif code == 402:
                        placeholder.error("余额不足，请联系管理员充值")
                    elif code == 429:
                        placeholder.error("请求太频繁，稍等片刻")
                    else:
                        placeholder.error(f"API 错误（{code}）")
                except Exception as e:
                    placeholder.error(f"网络错误：{str(e)[:150]}")

            st.rerun()


# ============================================================
# 主入口
# ============================================================

if st.session_state.logged_in:
    show_chat_page()
else:
    show_auth_page()
