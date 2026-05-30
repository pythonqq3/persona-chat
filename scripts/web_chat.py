"""
张仕达数字分身 · 全功能版
"""

import streamlit as st
import json, urllib.request, urllib.error, os, re, hashlib, time
from datetime import datetime
from pathlib import Path

st.set_page_config(
    page_title="张仕达 · 数字分身", page_icon="👤", layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"Get Help": None, "Report a bug": None, "About": "张仕达的数字分身"},
)

# ============================================================
# 全局样式 — 深色 + 玻璃效果
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');

* { font-family: 'Noto Sans SC', -apple-system, sans-serif; }
#MainMenu, footer, header { visibility: hidden; }

/* === 全局背景 + 全屏（暴力解除所有宽度限制）=== */
.stApp {
    background: linear-gradient(160deg, #0a0a14 0%, #111827 40%, #0f1729 100%);
}
/* 干掉 Streamlit 所有的 max-width */
.stMainBlockContainer,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > div,
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stVerticalBlock"],
section.main > div,
section.main > div > div,
section.main > div > div > div {
    max-width: 100% !important;
}
/* 调整外边距 */
.block-container {
    max-width: 100% !important;
    padding: 0.5rem 1.5rem !important;
}
@media (min-width: 768px) {
    .block-container { padding: 1rem 2rem !important; }
}

/* === 侧边栏 === */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0c0c1d 0%, #13132b 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.04) !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    color: #c0c0d0 !important;
    border-radius: 10px !important;
    font-size: 13px !important;
    transition: all 0.15s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(168,192,255,0.1) !important;
    border-color: rgba(168,192,255,0.25) !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: rgba(255,255,255,0.015) !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    border-radius: 12px !important;
}

/* === 主卡片 === */
.main-card {
    background: linear-gradient(135deg, rgba(30,27,75,0.7), rgba(36,36,62,0.6));
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 28px 36px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
}
.main-card::before {
    content: '';
    position: absolute;
    top: -80px; right: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(139,92,246,0.12), transparent);
    border-radius: 50%;
}
.main-card::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 30%;
    width: 160px; height: 160px;
    background: radial-gradient(circle, rgba(59,130,246,0.08), transparent);
    border-radius: 50%;
}
.main-card .name {
    font-size: 28px; font-weight: 700;
    background: linear-gradient(135deg, #a5b4fc, #c4b5fd, #e9d5ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    position: relative; z-index: 1;
}
.main-card .tagline {
    font-size: 13px; color: #94a3b8; margin-top: 4px;
    position: relative; z-index: 1;
}
.main-card .tags {
    margin-top: 12px; display: flex; gap: 8px; flex-wrap: wrap;
    position: relative; z-index: 1;
}
.main-card .tag {
    padding: 5px 14px; border-radius: 20px; font-size: 11px; font-weight: 500;
    background: rgba(255,255,255,0.06); color: #c4c4e0;
    border: 1px solid rgba(255,255,255,0.06);
    transition: all 0.2s;
}
.main-card .tag:hover { background: rgba(168,192,255,0.12); border-color: rgba(168,192,255,0.25); }

/* === 状态指示器 === */
.status-badge {
    display: flex; align-items: center; gap: 8px;
    padding: 12px 18px; border-radius: 14px;
    font-size: 13px; font-weight: 500;
}
.status-badge.online {
    background: rgba(52,211,153,0.08); color: #34d399;
    border: 1px solid rgba(52,211,153,0.15);
}
.status-badge.offline {
    background: rgba(251,191,36,0.08); color: #fbbf24;
    border: 1px solid rgba(251,191,36,0.15);
}
.status-dot { width: 8px; height: 8px; border-radius: 50%; animation: pulse 2s infinite; }
.status-dot.green { background: #34d399; box-shadow: 0 0 8px rgba(52,211,153,0.4); }
.status-dot.yellow { background: #fbbf24; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }

/* === 欢迎卡片 === */
.welcome-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 10px; margin: 16px 0;
}
.welcome-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 14px; padding: 18px 12px;
    text-align: center; transition: all 0.25s; cursor: pointer;
}
.welcome-card:hover {
    background: rgba(168,192,255,0.06);
    border-color: rgba(168,192,255,0.2);
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}
.welcome-card .icon { font-size: 26px; margin-bottom: 8px; display: block; }
.welcome-card .text { font-size: 12px; color: #94a3b8; line-height: 1.6; }

/* === 快捷按钮 === */
.quick-chip {
    display: inline-block;
    background: rgba(168,192,255,0.06);
    border: 1px solid rgba(168,192,255,0.1);
    color: #a5b4fc;
    padding: 6px 16px; border-radius: 20px;
    font-size: 12px; cursor: pointer;
    transition: all 0.15s; margin: 3px;
}
.quick-chip:hover {
    background: rgba(168,192,255,0.15);
    border-color: rgba(168,192,255,0.35);
    color: #c7d2fe;
}

/* === 登录页 === */
.auth-page {
    min-height: 80vh;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
}
.auth-box {
    background: linear-gradient(160deg, rgba(30,27,75,0.7), rgba(17,24,39,0.6));
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 24px;
    padding: 48px 44px;
    max-width: 440px;
    width: 100%;
    text-align: center;
    box-shadow: 0 16px 48px rgba(0,0,0,0.4);
}
.auth-box .logo {
    font-size: 52px; margin-bottom: 12px;
    display: block;
    filter: drop-shadow(0 0 20px rgba(168,192,255,0.3));
}
.auth-box h2 {
    font-size: 22px; font-weight: 700;
    color: #e2e8f0; margin: 0 0 4px;
}
.auth-box .sub {
    font-size: 13px; color: #64748b; margin-bottom: 28px;
}
.auth-box input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    padding: 10px 16px !important;
}
.auth-box input:focus {
    border-color: rgba(168,192,255,0.4) !important;
    box-shadow: 0 0 0 3px rgba(168,192,255,0.08) !important;
}
.auth-box .stButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 8px 0 !important;
}

/* === 打字动画 === */
.typing-dots {
    display: flex; gap: 5px; padding: 6px 0;
}
.typing-dots span {
    width: 7px; height: 7px; border-radius: 50%;
    background: #64748b;
    animation: typing 1.4s infinite;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing {
    0%, 60%, 100% { opacity: 0.15; transform: translateY(0); }
    30% { opacity: 1; transform: translateY(-5px); }
}

/* === 统计 === */
.stat-row {
    display: flex; gap: 8px;
}
.stat-item {
    flex: 1;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 10px;
    padding: 12px 10px; text-align: center;
}
.stat-item .value { font-size: 19px; font-weight: 700; color: #a5b4fc; }
.stat-item .label { font-size: 10px; color: #64748b; margin-top: 2px; }

/* === 通用 === */
hr { border-color: rgba(255,255,255,0.04) !important; }
[data-testid="stChatInput"] textarea {
    border-radius: 16px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    background: rgba(255,255,255,0.02) !important;
}
.stChatMessage { border-radius: 14px !important; }

/* === 移动端 === */
@media (max-width: 768px) {
    .main-card { padding: 18px 20px; }
    .main-card .name { font-size: 22px; }
    .welcome-grid { grid-template-columns: repeat(3, 1fr); gap: 6px; }
    .auth-box { padding: 32px 24px; margin: 20px 12px; }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# 数据与认证
# ============================================================
@st.cache_data
def load_skill():
    p = Path(__file__).parent.parent / "output" / "persona-me" / "SKILL.md"
    with open(p, "r", encoding="utf-8") as f:
        raw = f.read()
    return raw[raw.find("---", 3) + 3:].strip() if raw.startswith("---") else raw.strip()


SYSTEM_PROMPT = load_skill()
SUGGESTIONS = ["最近在干嘛", "写首诗", "无为是什么意思", "我好累",
               "你觉得人生的意义是什么", "羽毛球怎么练", "你喜欢什么样的女生", "来句道家的东西"]


@st.cache_data
def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def get_authorized():
    try:
        s = st.secrets.get("authorized_users", "")
    except Exception:
        return {}
    users = {}
    if s and s.strip():
        for line in s.strip().split("\n"):
            for e in line.split(","):
                e = e.strip()
                if ":" in e:
                    u, h = e.split(":", 1)
                    users[u.strip()] = h.strip()
    return users


def get_admins():
    try:
        s = st.secrets.get("admin_users", "")
    except Exception:
        return set()
    if not s or not s.strip(): return set()
    r = set()
    for line in s.strip().split("\n"):
        for u in line.split(","):
            if u.strip(): r.add(u.strip())
    return r


def get_key():
    try:
        return st.secrets.get("DEEPSEEK_API_KEY", "")
    except Exception:
        return os.environ.get("DEEPSEEK_API_KEY", "")


def chat_ds(messages, api_key, model="deepseek-chat", temp=0.7):
    body = json.dumps({"model": model, "messages": messages,
                       "temperature": temp, "max_tokens": 400}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.deepseek.com/v1/chat/completions", data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        r = json.loads(resp.read().decode("utf-8"))
        return r["choices"][0]["message"]["content"], r.get("usage", {})


# ============================================================
# Session
# ============================================================
INIT = {
    "logged_in": False, "username": "", "is_admin": False, "is_authorized": False,
    "user_api_key": "", "messages": [], "total_cost": 0.0,
    "login_mode": "login", "login_error": "",
    "sidebar_model": "deepseek-chat", "sidebar_temp": 0.7,
    "show_logout": False,
}
for k, v in INIT.items():
    if k not in st.session_state:
        st.session_state[k] = v


def active_key():
    if st.session_state.is_authorized or st.session_state.is_admin:
        return get_key()
    return st.session_state.user_api_key or get_key()


def logout():
    for k, v in INIT.items():
        st.session_state[k] = v
    st.rerun()


# ============================================================
# 登录/注册页
# ============================================================
def auth_page():
    st.markdown('<div class="auth-page">', unsafe_allow_html=True)
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)

    mode = st.session_state.login_mode
    auth_users = get_authorized()
    admins = get_admins()

    if mode == "login":
        st.markdown('<span class="logo">🔐</span>', unsafe_allow_html=True)
        st.markdown("<h2>欢迎回来</h2>", unsafe_allow_html=True)
        st.markdown('<p class="sub">登录后即可开始对话</p>', unsafe_allow_html=True)

        u = st.text_input("用户名", key="li_u", placeholder="输入用户名", label_visibility="collapsed")
        p = st.text_input("密码", type="password", key="li_p", placeholder="输入密码", label_visibility="collapsed")

        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("登 录", use_container_width=True, type="primary"):
                if not u or not p:
                    st.session_state.login_error = "请输入用户名和密码"
                    st.rerun()
                if u in auth_users:
                    if auth_users[u] == hash_pw(p):
                        st.session_state.logged_in = True
                        st.session_state.username = u
                        st.session_state.is_authorized = True
                        st.session_state.is_admin = u in admins
                        st.session_state.login_error = ""
                        st.rerun()
                    else:
                        st.session_state.login_error = "密码错误"
                        st.rerun()
                else:
                    st.session_state.login_error = "账号不存在"
                    st.rerun()
        with c2:
            if st.button("创建账号", use_container_width=True):
                st.session_state.login_mode = "register"
                st.session_state.login_error = ""
                st.rerun()

    else:
        st.markdown('<span class="logo">✨</span>', unsafe_allow_html=True)
        st.markdown("<h2>创建账号</h2>", unsafe_allow_html=True)
        st.markdown('<p class="sub">授权账号联系管理员 · 访客需自备 Key</p>', unsafe_allow_html=True)

        nu = st.text_input("用户名", key="rg_u", placeholder="3-20个字符", label_visibility="collapsed")
        np = st.text_input("密码", type="password", key="rg_p", placeholder="至少6位", label_visibility="collapsed")
        nc = st.text_input("确认密码", type="password", key="rg_c", placeholder="再次输入确认", label_visibility="collapsed")
        nk = st.text_input("API Key（授权用户跳过）", type="password", key="rg_k",
                           placeholder="sk-xxx · platform.deepseek.com", label_visibility="collapsed")

        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("注 册", use_container_width=True, type="primary"):
                err = None
                if not nu or len(nu) < 3: err = "用户名至少3个字符"
                elif len(nu) > 20: err = "最多20个字符"
                elif not re.match(r'^[a-zA-Z0-9_一-鿿]+$', nu): err = "只能包含中英文数字下划线"
                elif nu in auth_users: err = "此用户名已被预留"
                elif not np or len(np) < 6: err = "密码至少6位"
                elif np != nc: err = "两次密码不一致"
                elif not nk and not get_key(): err = "请填写 API Key"
                if err:
                    st.session_state.login_error = err; st.rerun()
                st.session_state.logged_in = True
                st.session_state.username = nu
                st.session_state.is_authorized = False
                st.session_state.is_admin = False
                st.session_state.user_api_key = nk
                st.session_state.login_error = ""
                st.rerun()
        with c2:
            if st.button("返回登录", use_container_width=True):
                st.session_state.login_mode = "login"
                st.session_state.login_error = ""
                st.rerun()

    if st.session_state.login_error:
        st.error(st.session_state.login_error)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;color:#475569;font-size:11px;margin-top:16px;">'
        '🔒 通信加密 · 密钥安全存储</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# 聊天主页
# ============================================================
def chat_page():
    u = st.session_state.username
    is_adm = st.session_state.is_admin
    is_au = st.session_state.is_authorized
    key = active_key()

    # ====== 侧边栏 ======
    with st.sidebar:
        badge = "👑 管理员" if is_adm else ("🔓 授权" if is_au else "📝 访客")
        bc = "#fbbf24" if is_adm else ("#34d399" if is_au else "#64748b")
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:18px;">
            <div style="font-size:36px;">{'👑' if is_adm else '👤'}</div>
            <div style="font-size:17px;font-weight:600;color:#e2e8f0;">{u}</div>
            <div style="font-size:11px;color:{bc};margin-top:3px;">{badge}</div>
        </div>""", unsafe_allow_html=True)

        # API
        with st.expander("🔑 API", expanded=False):
            if is_adm or is_au:
                k = get_key()
                m = (k[:6] + "****" + k[-4:]) if len(k) > 10 else "(未配置)"
                if not is_adm: m = "sk-****" + k[-4:] if len(k) > 10 else "(已配置)"
                st.text_input("密钥", value=m, disabled=True, label_visibility="collapsed")
                st.caption("DeepSeek · " + ("完整可见" if is_adm else "脱敏显示"))
            else:
                nk = st.text_input("密钥", type="password", value=st.session_state.user_api_key,
                                   placeholder="sk-xxxxxxxx", label_visibility="collapsed")
                if nk != st.session_state.user_api_key: st.session_state.user_api_key = nk
                st.caption("platform.deepseek.com 免费获取")

        # 设置
        with st.expander("⚙️ 设置", expanded=False):
            st.session_state.sidebar_model = st.selectbox(
                "模型", ["deepseek-chat", "deepseek-reasoner"],
                format_func=lambda x: "💬 日常对话" if "chat" in x else "🧠 深度思考")
            st.session_state.sidebar_temp = st.slider("创意度", 0.0, 1.5, 0.7, 0.1,
                                                      help="0=稳定 1.5=天马行空")

        # 统计
        with st.expander("📊 统计", expanded=bool(st.session_state.messages)):
            n = len(st.session_state.messages) // 2
            tks = len(SYSTEM_PROMPT) // 2 + sum(len(m["content"]) // 2 for m in st.session_state.messages)
            cost = st.session_state.total_cost
            st.markdown(f"""
            <div class="stat-row">
                <div class="stat-item"><div class="value">{n}</div><div class="label">轮对话</div></div>
                <div class="stat-item"><div class="value">~{tks:,}</div><div class="label">Token</div></div>
                <div class="stat-item"><div class="value">¥{cost:.4f}</div><div class="label">花费</div></div>
            </div>""", unsafe_allow_html=True)

        # 工具
        with st.expander("🛠 工具", expanded=False):
            if st.button("🗑 清空对话", use_container_width=True):
                st.session_state.messages = []; st.session_state.total_cost = 0.0; st.rerun()
            if st.session_state.messages:
                txt = "\n\n".join(
                    f"{'你' if m['role']=='user' else '张仕达'}：{m['content']}"
                    for m in st.session_state.messages)
                st.download_button("📥 导出记录", txt, f"聊天_{datetime.now():%m%d_%H%M}.txt",
                                   use_container_width=True)
            else:
                st.caption("暂无对话")

        # 关于
        with st.expander("ℹ️ 关于", expanded=False):
            st.markdown("""
            <div style="font-size:12px;color:#94a3b8;line-height:2;">
            <b style="color:#c4b5fd;">张仕达的数字分身</b><br>
            版本 V5 · 24,060 条消息<br>
            数据：2024.08 - 2026.05<br>
            驱动：DeepSeek<br>
            源码：<a href="https://github.com/pythonqq3/persona-chat" style="color:#a5b4fc;">GitHub ↗</a>
            </div>""", unsafe_allow_html=True)

        # 退出
        st.markdown("---")
        if not st.session_state.show_logout:
            if st.button("🚪 退出登录", use_container_width=True):
                st.session_state.show_logout = True; st.rerun()
        else:
            st.warning("退出将清空当前对话")
            q1, q2 = st.columns(2)
            with q1:
                if st.button("✅ 确认", use_container_width=True, type="primary"):
                    st.session_state.show_logout = False; logout()
            with q2:
                if st.button("❌ 取消", use_container_width=True):
                    st.session_state.show_logout = False; st.rerun()

    # ====== 顶部卡片 ======
    c1, c2 = st.columns([5, 1])
    with c1:
        st.markdown("""
        <div class="main-card">
            <div class="name">张仕达</div>
            <div class="tagline">19 岁 · 江西中医药大学 · 打羽毛球 · 写诗词 · 偶尔毒舌 · 聊道家</div>
            <div class="tags">
                <span class="tag">🏸 羽毛球</span>
                <span class="tag">📝 写诗词</span>
                <span class="tag">☯ 道家思想</span>
                <span class="tag">🎮 王者荣耀</span>
                <span class="tag">💻 编程</span>
                <span class="tag">🏃 跑步</span>
            </div>
        </div>""", unsafe_allow_html=True)
    with c2:
        if key:
            st.markdown(
                '<div class="status-badge online"><div class="status-dot green"></div>分身在线</div>',
                unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="status-badge offline"><div class="status-dot yellow"></div>未配置 Key</div>',
                unsafe_allow_html=True)

    # ====== 欢迎区 ======
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-grid">
            <div class="welcome-card"><span class="icon">🏸</span><span class="text">羽毛球<br>怎么练</span></div>
            <div class="welcome-card"><span class="icon">📝</span><span class="text">写首诗<br>来看看</span></div>
            <div class="welcome-card"><span class="icon">☯</span><span class="text">无为<br>是什么</span></div>
            <div class="welcome-card"><span class="icon">💭</span><span class="text">最近<br>好烦</span></div>
            <div class="welcome-card"><span class="icon">🎮</span><span class="text">来打<br>王者</span></div>
            <div class="welcome-card"><span class="icon">🤔</span><span class="text">人生<br>有意义吗</span></div>
        </div>""", unsafe_allow_html=True)

        st.caption("💡 试试这些话题")
        cols = st.columns(4)
        for i, s in enumerate(SUGGESTIONS):
            with cols[i % 4]:
                if st.button(s, key=f"sug_{i}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": s})
                    st.rerun()

    # ====== 对话 ======
    for msg in st.session_state.messages:
        avatar = "👤" if msg["role"] == "user" else None
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # ====== 输入 ======
    prompt = st.chat_input("说点什么..." if st.session_state.messages else f"嘿 {u}，想聊什么？")

    if prompt:
        if not key:
            st.error("请先在侧边栏配置 API Key")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                ph = st.empty()
                ph.markdown(
                    '<div class="typing-dots"><span></span><span></span><span></span></div>',
                    unsafe_allow_html=True)
                try:
                    msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
                    reply, usage = chat_ds(msgs, key, st.session_state.sidebar_model,
                                           st.session_state.sidebar_temp)
                    ph.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    if usage:
                        c = (usage.get("prompt_tokens", 0) * 1 +
                             usage.get("completion_tokens", 0) * 2) / 1_000_000
                        st.session_state.total_cost += c
                except urllib.error.HTTPError as e:
                    m = {401: "密钥无效", 402: "余额不足", 429: "太频繁了，稍等"}
                    ph.error(m.get(e.code, f"API 错误 {e.code}"))
                except Exception as e:
                    ph.error(f"网络异常：{str(e)[:100]}")
            st.rerun()


# ============================================================
chat_page() if st.session_state.logged_in else auth_page()
