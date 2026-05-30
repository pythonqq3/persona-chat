"""
张仕达数字分身 — 带登录注册 + 三级权限
用法: python -m streamlit run scripts/web_chat.py

Streamlit Cloud Secrets:
  DEEPSEEK_API_KEY = "sk-xxx"
  authorized_users = "user1:hash1, user2:hash2"
  admin_users = "admin1"
"""

import streamlit as st
import json
import urllib.request
import urllib.error
import os
import re
import hashlib
from datetime import datetime
from pathlib import Path

# ============================================================
st.set_page_config(
    page_title="张仕达 · 数字分身", page_icon="👤", layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"Get Help": None, "Report a bug": None, "About": "张仕达的数字分身"},
)

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
html,body,[class*="css"]{font-family:'Noto Sans SC',-apple-system,BlinkMacSystemFont,sans-serif}
#MainMenu,footer,header{visibility:hidden}
.main-header{background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);border-radius:16px;padding:28px 36px;margin-bottom:20px;color:#fff;box-shadow:0 8px 32px rgba(0,0,0,.3)}
.main-header .name{font-size:28px;font-weight:700;background:linear-gradient(90deg,#a8c0ff,#c4b5fd);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.main-header .tagline{font-size:14px;color:#a0aec0;margin-top:6px}
.main-header .tags{margin-top:12px;display:flex;gap:8px;flex-wrap:wrap}
.main-header .tag{background:rgba(255,255,255,.1);color:#d4d4f7;padding:4px 12px;border-radius:16px;font-size:12px}
.status-badge{display:flex;align-items:center;gap:8px;padding:10px 16px;border-radius:12px;font-size:13px;font-weight:500}
.status-badge.online{background:rgba(52,211,153,.12);color:#34d399;border:1px solid rgba(52,211,153,.25)}
.status-badge.offline{background:rgba(251,191,36,.12);color:#fbbf24;border:1px solid rgba(251,191,36,.25)}
.status-dot{width:8px;height:8px;border-radius:50%;animation:pulse 2s infinite}
.status-dot.green{background:#34d399}.status-dot.yellow{background:#fbbf24}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
.welcome-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:16px 0}
.welcome-card{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:16px;text-align:center;transition:all .2s;cursor:pointer}
.welcome-card:hover{background:rgba(255,255,255,.08);transform:translateY(-2px);border-color:rgba(168,192,255,.2)}
.welcome-card .icon{font-size:26px;margin-bottom:6px}
.welcome-card .text{font-size:12px;color:#a0aec0;line-height:1.6}
.stat-row{display:flex;gap:8px;margin:8px 0}
.stat-item{flex:1;background:rgba(255,255,255,.03);border-radius:8px;padding:12px 10px;text-align:center}
.stat-item .value{font-size:20px;font-weight:700;color:#a8c0ff}
.stat-item .label{font-size:10px;color:#6b7280;margin-top:2px}
.auth-box{max-width:440px;margin:40px auto;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.08);border-radius:20px;padding:44px 40px;text-align:center}
.auth-box .logo{font-size:56px;margin-bottom:12px}
.auth-box h2{font-size:22px;font-weight:700;color:#e0e0f0;margin-bottom:4px}
.auth-box .sub{font-size:13px;color:#6b7280;margin-bottom:28px}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0f0f1a,#1a1a2e);border-right:1px solid rgba(255,255,255,.06)}
hr{border-color:rgba(255,255,255,.06)!important}
.stButton>button{border-radius:10px!important;font-weight:500!important;transition:all .2s!important}
.stButton>button:hover{transform:translateY(-1px)}
</style>
""", unsafe_allow_html=True)


# ============================================================
# 数据加载（延迟加载，避免模块初始化时访问 st.secrets）
# ============================================================

@st.cache_data
def load_skill():
    skill_path = Path(__file__).parent.parent / "output" / "persona-me" / "SKILL.md"
    with open(skill_path, "r", encoding="utf-8") as f:
        raw = f.read()
    if raw.startswith("---"):
        end = raw.find("---", 3)
        return raw[end + 3:].strip()
    return raw.strip()

SYSTEM_PROMPT = load_skill()


# ============================================================
# 认证函数
# ============================================================

def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_secrets_safe():
    """安全获取 secrets，初始化失败时返回空"""
    try:
        return dict(st.secrets)
    except Exception:
        return {}


def get_authorized_users():
    """获取授权用户字典 {username: password_hash}，兼容逗号分隔和换行分隔"""
    try:
        auth_str = st.secrets.get("authorized_users", "")
    except Exception:
        return {}
    users = {}
    if auth_str and auth_str.strip():
        # 统一处理：先按换行分，再按逗号分，去空白
        entries = []
        for line in auth_str.strip().split("\n"):
            for entry in line.split(","):
                entry = entry.strip()
                if entry and ":" in entry:
                    entries.append(entry)
        for entry in entries:
            u, h = entry.split(":", 1)
            users[u.strip()] = h.strip()
    return users


def get_admin_set():
    """获取管理员集合，兼容逗号和换行"""
    try:
        s = st.secrets.get("admin_users", "")
    except Exception:
        return set()
    if not s or not s.strip():
        return set()
    result = set()
    for line in s.strip().split("\n"):
        for u in line.split(","):
            u = u.strip()
            if u:
                result.add(u)
    return result


def get_api_key():
    try:
        return st.secrets.get("DEEPSEEK_API_KEY", "")
    except Exception:
        return os.environ.get("DEEPSEEK_API_KEY", "")


# ============================================================
# API 调用
# ============================================================

def chat_deepseek(messages, api_key, model="deepseek-chat", temperature=0.7):
    body = json.dumps({"model": model, "messages": messages,
                       "temperature": temperature, "max_tokens": 400}).encode("utf-8")
    req = urllib.request.Request("https://api.deepseek.com/v1/chat/completions", data=body,
                                 headers={"Content-Type": "application/json",
                                          "Authorization": f"Bearer {api_key}"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"], result.get("usage", {})


# ============================================================
# Session 初始化
# ============================================================

KEYS = ["logged_in", "username", "is_admin", "is_authorized",
        "user_api_key", "messages", "total_cost",
        "login_mode", "login_error", "sidebar_model", "sidebar_temp"]
for k in KEYS:
    if k not in st.session_state:
        st.session_state[k] = None if k in ["login_error"] else (
            False if k in ["logged_in", "is_admin", "is_authorized"] else (
                [] if k == "messages" else (
                    0.0 if k == "total_cost" else (
                        "login" if k == "login_mode" else (
                            "deepseek-chat" if k == "sidebar_model" else (
                                0.7 if k == "sidebar_temp" else ""
                            ))))))


def reset_chat():
    st.session_state.messages = []
    st.session_state.total_cost = 0.0


def full_reset():
    for k in KEYS:
        st.session_state[k] = None if k in ["login_error"] else (
            False if k in ["logged_in", "is_admin", "is_authorized"] else (
                [] if k == "messages" else (
                    0.0 if k == "total_cost" else (
                        "login" if k == "login_mode" else (
                            "deepseek-chat" if k == "sidebar_model" else (
                                0.7 if k == "sidebar_temp" else ""))))))


def get_active_key():
    if st.session_state.is_authorized or st.session_state.is_admin:
        return get_api_key()
    return st.session_state.user_api_key or get_api_key()


# ============================================================
# 登录页面
# ============================================================

def show_auth_page():
    st.markdown("""
    <div style="text-align:center;padding-top:30px;">
        <div style="font-size:48px;">👤</div>
        <div style="font-size:24px;font-weight:700;color:#e0e0f0;margin-top:8px;">张仕达的数字分身</div>
        <div style="font-size:14px;color:#6b7280;">基于两万四千条真实聊天记录</div>
    </div>
    """, unsafe_allow_html=True)

    mode = st.session_state.login_mode
    authorized = get_authorized_users()
    admins = get_admin_set()

    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown('<div class="auth-box">', unsafe_allow_html=True)

        if mode == "login":
            st.markdown('<div class="logo">🔐</div>', unsafe_allow_html=True)
            st.markdown("<h2>登录</h2>", unsafe_allow_html=True)
            st.markdown('<p class="sub">授权用户自动配置 API，无需手动填写</p>', unsafe_allow_html=True)

            username = st.text_input("用户名", key="li_user", placeholder="输入用户名",
                                     label_visibility="collapsed")
            password = st.text_input("密码", type="password", key="li_pass", placeholder="输入密码",
                                     label_visibility="collapsed")

            c1, c2 = st.columns(2)
            with c1:
                login_btn = st.button("登 录", use_container_width=True, type="primary")
            with c2:
                reg_btn = st.button("注册新账号", use_container_width=True)

            if login_btn:
                if not username or not password:
                    st.session_state.login_error = "请填写用户名和密码"
                    st.rerun()
                elif username in authorized:
                    if authorized[username] == hash_pw(password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.is_authorized = True
                        st.session_state.is_admin = username in admins
                        st.session_state.login_error = ""
                        st.rerun()
                    else:
                        st.session_state.login_error = "密码错误"
                        st.rerun()
                else:
                    st.session_state.login_error = "账号不存在，请先注册"
                    st.rerun()

            if reg_btn:
                st.session_state.login_mode = "register"
                st.session_state.login_error = ""
                st.rerun()

        else:
            st.markdown('<div class="logo">📝</div>', unsafe_allow_html=True)
            st.markdown("<h2>注册</h2>", unsafe_allow_html=True)
            st.markdown('<p class="sub">授权用户联系管理员添加，访客需自备 Key</p>', unsafe_allow_html=True)

            new_user = st.text_input("用户名（3-20字符）", key="rg_user", placeholder="设置用户名",
                                     label_visibility="collapsed")
            new_pass = st.text_input("密码（至少6位）", type="password", key="rg_pass",
                                     placeholder="设置密码", label_visibility="collapsed")
            new_confirm = st.text_input("确认密码", type="password", key="rg_confirm",
                                        placeholder="再次输入密码", label_visibility="collapsed")

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            own_key = st.text_input("API Key（授权用户可跳过）", type="password", key="rg_api",
                                    placeholder="sk-xxxxxxxx，在 platform.deepseek.com 获取",
                                    label_visibility="collapsed")

            c1, c2 = st.columns(2)
            with c1:
                reg_btn2 = st.button("注 册", use_container_width=True, type="primary")
            with c2:
                back_btn = st.button("返回登录", use_container_width=True)

            if reg_btn2:
                err = None
                if not new_user or len(new_user) < 3:
                    err = "用户名至少 3 个字符"
                elif len(new_user) > 20:
                    err = "用户名最多 20 个字符"
                elif not re.match(r'^[a-zA-Z0-9_一-鿿]+$', new_user):
                    err = "用户名只能包含中英文、数字和下划线"
                elif new_user in authorized:
                    err = "此用户名已被预留"
                elif not new_pass or len(new_pass) < 6:
                    err = "密码至少 6 位"
                elif new_pass != new_confirm:
                    err = "两次密码输入不一致"
                elif not own_key and not get_api_key():
                    err = "请填写 API Key"

                if err:
                    st.session_state.login_error = err
                    st.rerun()
                else:
                    st.session_state.logged_in = True
                    st.session_state.username = new_user
                    st.session_state.is_authorized = False
                    st.session_state.is_admin = False
                    st.session_state.user_api_key = own_key
                    st.session_state.login_error = ""
                    st.rerun()

            if back_btn:
                st.session_state.login_mode = "login"
                st.session_state.login_error = ""
                st.rerun()

        # 显示错误
        if st.session_state.login_error:
            st.error(st.session_state.login_error)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;color:#4b5563;font-size:12px;margin-top:20px;">
    授权用户登录后自动使用管理员配置的 API，Key 全程加密不可见
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# 聊天页面
# ============================================================

def estimate_tokens(text):
    ch = len(re.findall(r'[一-鿿]', text))
    return int(ch / 1.5 + (len(text) - ch) / 4)


def show_chat_page():
    username = st.session_state.username
    is_admin = st.session_state.is_admin
    is_auth = st.session_state.is_authorized
    api_key = get_active_key()

    # ====== 侧边栏 ======
    with st.sidebar:
        badge = "👑 管理员" if is_admin else ("🔓 授权用户" if is_auth else "📝 访客")
        badge_color = "#fbbf24" if is_admin else ("#34d399" if is_auth else "#6b7280")
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:16px;">
            <div style="font-size:36px;">{'👑' if is_admin else '👤'}</div>
            <div style="font-size:17px;font-weight:700;color:#e0e0f0;">{username}</div>
            <div style="font-size:11px;color:{badge_color};margin-top:4px;">{badge}</div>
        </div>
        """, unsafe_allow_html=True)

        # API 区
        if is_admin:
            with st.expander("🔑 API 管理", expanded=False):
                k = get_api_key()
                masked = k[:6] + "****" + k[-4:] if len(k) > 10 else "(未配置)"
                st.code(masked, language=None)
                st.caption("完整密钥存储在服务器环境，不可导出")
        elif is_auth:
            with st.expander("🔑 API 状态", expanded=False):
                st.success("已自动配置 ✅")
                st.caption("由管理员统一管理，密钥不可见")
        else:
            with st.expander("🔑 API 设置", expanded=not st.session_state.user_api_key):
                new_key = st.text_input("你的 Key", type="password",
                                        value=st.session_state.user_api_key,
                                        placeholder="sk-xxxxxxxx", label_visibility="collapsed")
                if new_key != st.session_state.user_api_key:
                    st.session_state.user_api_key = new_key
                st.caption("platform.deepseek.com → 免费获取")

        # 模型设置
        with st.expander("⚙️ 对话设置", expanded=False):
            st.session_state.sidebar_model = st.selectbox(
                "模型", ["deepseek-chat", "deepseek-reasoner"],
                format_func=lambda x: "💬 日常" if "chat" in x else "🧠 深思")
            st.session_state.sidebar_temp = st.slider("创意度", 0.0, 1.5, 0.7, 0.1)

        # 统计
        st.markdown("---")
        st.caption("📊 本次会话")
        n = len(st.session_state.messages) // 2
        tks = estimate_tokens(SYSTEM_PROMPT) + sum(estimate_tokens(m["content"]) for m in st.session_state.messages)
        cost = st.session_state.total_cost
        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-item"><div class="value">{n}</div><div class="label">轮对话</div></div>
            <div class="stat-item"><div class="value">{tks:,}</div><div class="label">Token</div></div>
            <div class="stat-item"><div class="value">¥{cost:.4f}</div><div class="label">花费</div></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        ca, cb = st.columns(2)
        with ca:
            if st.button("🔄 新对话", use_container_width=True):
                reset_chat()
                st.rerun()
        with cb:
            if st.session_state.messages:
                txt = "\n\n".join(f"{'你' if m['role']=='user' else '张仕达'}：{m['content']}"
                                  for m in st.session_state.messages)
                st.download_button("📥 导出", txt, f"聊天_{datetime.now().strftime('%m%d_%H%M')}.txt",
                                   use_container_width=True)

        st.markdown("---")
        if st.button("🚪 退出登录", use_container_width=True):
            full_reset()
            st.rerun()

        st.caption("⚡ DeepSeek · 人格 V5 · 24K 消息")

    # ====== 主区域 ======
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown("""
        <div class="main-header">
            <div class="name">张仕达</div>
            <div class="tagline">19 岁 · 大学生 · 爱羽毛球 · 写诗词 · 偶尔毒舌 · 聊道家</div>
            <div class="tags">
                <span class="tag">🏸 羽毛球</span><span class="tag">📝 写诗词</span>
                <span class="tag">☯ 道家</span><span class="tag">🎮 王者</span>
                <span class="tag">💻 编程</span><span class="tag">🏃 跑步</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        if api_key:
            st.markdown('<div class="status-badge online"><div class="status-dot green"></div>在线</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-badge offline"><div class="status-dot yellow"></div>未配置</div>',
                        unsafe_allow_html=True)

    # 欢迎引导
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-grid">
            <div class="welcome-card"><div class="icon">🏸</div><div class="text">羽毛球怎么练</div></div>
            <div class="welcome-card"><div class="icon">📝</div><div class="text">写首诗看看</div></div>
            <div class="welcome-card"><div class="icon">☯</div><div class="text">无为是什么意思</div></div>
            <div class="welcome-card"><div class="icon">💭</div><div class="text">最近好烦</div></div>
            <div class="welcome-card"><div class="icon">🎮</div><div class="text">来打王者</div></div>
            <div class="welcome-card"><div class="icon">🤔</div><div class="text">人生有什么意义</div></div>
        </div>
        """, unsafe_allow_html=True)

    # 对话
    for msg in st.session_state.messages:
        avatar = "👤" if msg["role"] == "user" else None
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # 输入
    prompt = st.chat_input("说点什么..." if st.session_state.messages else f"你好 {username}，想聊点什么？")

    if prompt:
        if not api_key:
            st.error("请先在侧边栏配置 API Key")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                ph = st.empty()
                ph.markdown("▊")

                try:
                    msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
                    reply, usage = chat_deepseek(msgs, api_key,
                                                 st.session_state.sidebar_model,
                                                 st.session_state.sidebar_temp)
                    ph.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})

                    if usage:
                        total_tokens = usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0)
                        # deepseek-chat: ¥1/M input, ¥2/M output
                        cost = (usage.get("prompt_tokens", 0) * 1 + usage.get("completion_tokens", 0) * 2) / 1_000_000
                        st.session_state.total_cost += cost

                except urllib.error.HTTPError as e:
                    msgs_map = {401: "密钥无效", 402: "余额不足，联系管理员", 429: "太频繁了，稍等几秒"}
                    ph.error(msgs_map.get(e.code, f"API 错误 ({e.code})"))
                except Exception as e:
                    ph.error(f"网络异常：{str(e)[:120]}")

            st.rerun()


# ============================================================
# 入口
# ============================================================

if st.session_state.logged_in:
    show_chat_page()
else:
    show_auth_page()
