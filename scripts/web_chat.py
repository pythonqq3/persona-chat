"""
张仕达数字分身
"""

import streamlit as st
import json, urllib.request, urllib.error, os, re, hashlib
from datetime import datetime
from pathlib import Path

st.set_page_config(
    page_title="张仕达", page_icon="👤", layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"Get Help": None, "Report a bug": None, "About": None},
)

# ============================================================
# 设计系统 — 暗色极简风格
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', 'Noto Sans SC', -apple-system, sans-serif; }
#MainMenu, footer, header { visibility: hidden; }

/* ======== 背景 ======== */
.stApp { background: #0d0d12; }

/* ======== 侧边栏 ======== */
[data-testid="stSidebar"] {
    background: #0a0a0f !important;
    border-right: 1px solid #1a1a24 !important;
}
[data-testid="stSidebar"] button {
    background: transparent !important;
    border: 1px solid #1f1f2e !important;
    color: #a0a0b8 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    transition: all .15s !important;
}
[data-testid="stSidebar"] button:hover {
    background: #1a1a28 !important;
    border-color: #2a2a3e !important;
    color: #d0d0e0 !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: transparent !important;
    border: 1px solid #1a1a24 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] hr { border-color: #1a1a24 !important; }

/* ======== 主区域 ======== */
[data-testid="stAppViewContainer"] section.main > div {
    max-width: 100% !important;
}
.block-container {
    max-width: 100% !important;
    padding: 1rem 2rem 0 2rem !important;
}
[data-testid="stVerticalBlock"] { max-width: 100% !important; }

/* ======== 顶部信息栏 ======== */
.top-bar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 0; margin-bottom: 8px; gap: 16px;
}
.top-bar .brand {
    display: flex; align-items: center; gap: 10px;
}
.top-bar .avatar {
    width: 36px; height: 36px; border-radius: 50%;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; color: #fff; font-weight: 600;
}
.top-bar .name {
    font-size: 16px; font-weight: 600; color: #e4e4ec;
    letter-spacing: -0.01em;
}
.top-bar .status {
    display: flex; align-items: center; gap: 6px;
    font-size: 12px; color: #34d399;
}
.top-bar .status-dot {
    width: 6px; height: 6px; border-radius: 50%; background: #34d399;
    box-shadow: 0 0 6px rgba(52,211,153,.4);
}

/* ======== 标签条 ======== */
.tag-row {
    display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 16px;
}
.tag-item {
    padding: 4px 12px; border-radius: 6px;
    font-size: 12px; color: #8888a8;
    background: #111118; border: 1px solid #1a1a26;
}

/* ======== 欢迎卡片 ======== */
.welcome-wrap { margin: 20px 0 8px; }
.welcome-row {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 8px;
}
.welcome-card {
    background: #101016;
    border: 1px solid #181822;
    border-radius: 10px;
    padding: 18px 14px;
    text-align: center;
    cursor: pointer;
    transition: all .2s;
}
.welcome-card:hover {
    background: #14141e;
    border-color: #2a2a3e;
}
.welcome-card .wc-icon { font-size: 22px; display: block; margin-bottom: 6px; }
.welcome-card .wc-text { font-size: 11px; color: #707088; line-height: 1.5; }

/* ======== 快捷话题 ======== */
.chip-wrap { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 16px; }
.chip {
    padding: 5px 14px; border-radius: 16px;
    font-size: 12px; color: #8888b0; cursor: pointer;
    background: #111118; border: 1px solid #1a1a28;
    transition: all .15s; white-space: nowrap;
}
.chip:hover { background: #1a1a2e; border-color: #3a3a58; color: #b0b0d0; }

/* ======== 对话气泡微调 ======== */
.stChatMessage {
    background: transparent !important;
    padding: 6px 0 !important;
}
[data-testid="stChatInput"] textarea {
    border-radius: 10px !important;
    border: 1px solid #1a1a28 !important;
    background: #0f0f17 !important;
    color: #d0d0e0 !important;
    padding: 10px 14px !important;
    font-size: 14px !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #3a3a58 !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,.1) !important;
}

/* ======== 打字动画 ======== */
.type-dots { display: flex; gap: 4px; padding: 4px 0; }
.type-dots span {
    width: 5px; height: 5px; border-radius: 50%; background: #484860;
    animation: td 1.4s infinite;
}
.type-dots span:nth-child(2) { animation-delay: .2s; }
.type-dots span:nth-child(3) { animation-delay: .4s; }
@keyframes td { 0%,60%,100%{opacity:.15} 30%{opacity:1} }

/* ======== 登录页 ======== */
.login-wrap {
    display: flex; align-items: center; justify-content: center;
    min-height: 80vh;
}
.login-card {
    width: 400px;
    background: #101016;
    border: 1px solid #1a1a26;
    border-radius: 16px;
    padding: 44px 40px;
    text-align: center;
}
.login-card .lc-icon { font-size: 40px; display: block; margin-bottom: 16px; }
.login-card h2 { font-size: 20px; font-weight: 600; color: #e4e4ec; margin: 0 0 4px; }
.login-card .lc-sub { font-size: 13px; color: #606078; margin-bottom: 28px; }
.login-card input {
    background: #0d0d14 !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 8px !important;
    color: #d0d0e0 !important;
    padding: 10px 14px !important;
    font-size: 14px !important;
}
.login-card input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,.08) !important;
}
.login-card button {
    border-radius: 8px !important;
    font-weight: 500 !important;
}

/* ======== 统计小卡片 ======== */
.stat-row { display: flex; gap: 6px; }
.stat-item {
    flex: 1; background: #0d0d14;
    border: 1px solid #181824; border-radius: 6px;
    padding: 10px 8px; text-align: center;
}
.stat-item .sv { font-size: 17px; font-weight: 600; color: #a5b4fc; }
.stat-item .sl { font-size: 10px; color: #585870; margin-top: 1px; }

/* ======== 响应式 ======== */
@media (max-width: 768px) {
    .block-container { padding: .5rem 1rem !important; }
    .welcome-row { grid-template-columns: repeat(3, 1fr); gap: 6px; }
    .login-card { width: auto; margin: 20px 16px; padding: 32px 24px; }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# 数据
# ============================================================
@st.cache_data
def load_skill():
    p = Path(__file__).parent.parent / "output" / "persona-me" / "SKILL.md"
    with open(p, "r", encoding="utf-8") as f:
        raw = f.read()
    return raw[raw.find("---", 3) + 3:].strip() if raw.startswith("---") else raw.strip()


SYSTEM_PROMPT = load_skill()
SUGGESTIONS = ["最近在干嘛", "写首诗吧", "无为是什么意思", "我好累",
               "人生有意义吗", "羽毛球怎么练", "喜欢什么样的女生", "来句道家的"]


@st.cache_data
def hpw(pw): return hashlib.sha256(pw.encode()).hexdigest()


def auth_users():
    try: s = st.secrets.get("authorized_users", "")
    except: return {}
    u = {}
    if s and s.strip():
        for line in s.strip().split("\n"):
            for e in line.split(","):
                e = e.strip()
                if ":" in e:
                    a, b = e.split(":", 1)
                    u[a.strip()] = b.strip()
    return u


def admins():
    try: s = st.secrets.get("admin_users", "")
    except: return set()
    if not s or not s.strip(): return set()
    r = set()
    for line in s.strip().split("\n"):
        for x in line.split(","):
            if x.strip(): r.add(x.strip())
    return r


def skey():
    try: return st.secrets.get("DEEPSEEK_API_KEY", "")
    except: return os.environ.get("DEEPSEEK_API_KEY", "")


def call_api(msgs, key, model="deepseek-chat", temp=0.7):
    b = json.dumps({"model": model, "messages": msgs,
                    "temperature": temp, "max_tokens": 400}).encode("utf-8")
    r = urllib.request.Request("https://api.deepseek.com/v1/chat/completions", data=b,
                               headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(r, timeout=60) as resp:
        d = json.loads(resp.read().decode("utf-8"))
        return d["choices"][0]["message"]["content"], d.get("usage", {})


# ============================================================
# Session
# ============================================================
INIT = {
    "logged_in": False, "username": "", "is_admin": False, "is_authorized": False,
    "user_api_key": "", "messages": [], "total_cost": 0.0,
    "login_mode": "login", "login_error": "",
    "model": "deepseek-chat", "temp": 0.7, "show_logout": False,
}
for k, v in INIT.items():
    if k not in st.session_state: st.session_state[k] = v


def active_key():
    return skey() if (st.session_state.is_authorized or st.session_state.is_admin) else (
        st.session_state.user_api_key or skey())


def do_logout():
    for k, v in INIT.items(): st.session_state[k] = v
    st.rerun()


# ============================================================
# 登录
# ============================================================
def auth_page():
    st.markdown('<div class="login-wrap"><div class="login-card">', unsafe_allow_html=True)
    mode = st.session_state.login_mode
    au = auth_users()
    ad = admins()

    if mode == "login":
        st.markdown('<span class="lc-icon">🔐</span>', unsafe_allow_html=True)
        st.markdown("<h2>登录</h2>", unsafe_allow_html=True)
        st.markdown('<p class="lc-sub">授权用户自动配置 API</p>', unsafe_allow_html=True)
        u = st.text_input("用户名", key="li_u", placeholder="输入用户名", label_visibility="collapsed")
        p = st.text_input("密码", type="password", key="li_p", placeholder="输入密码", label_visibility="collapsed")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("登 录", use_container_width=True, type="primary"):
                if not u or not p:
                    st.session_state.login_error = "请输入用户名和密码"; st.rerun()
                if u in au:
                    if au[u] == hpw(p):
                        st.session_state.logged_in = True
                        st.session_state.username = u
                        st.session_state.is_authorized = True
                        st.session_state.is_admin = u in ad
                        st.session_state.login_error = ""; st.rerun()
                    else:
                        st.session_state.login_error = "密码错误"; st.rerun()
                else:
                    st.session_state.login_error = "账号不存在"; st.rerun()
        with c2:
            if st.button("注册", use_container_width=True):
                st.session_state.login_mode = "register"; st.session_state.login_error = ""; st.rerun()
    else:
        st.markdown('<span class="lc-icon">✨</span>', unsafe_allow_html=True)
        st.markdown("<h2>注册</h2>", unsafe_allow_html=True)
        st.markdown('<p class="lc-sub">授权账号联系管理员 · 访客需自备 Key</p>', unsafe_allow_html=True)
        nu = st.text_input("用户名", key="rg_u", placeholder="3-20个字符", label_visibility="collapsed")
        np = st.text_input("密码", type="password", key="rg_p", placeholder="至少6位", label_visibility="collapsed")
        nc = st.text_input("确认密码", type="password", key="rg_c", placeholder="再次输入", label_visibility="collapsed")
        nk = st.text_input("API Key（授权用户跳过）", type="password", key="rg_k",
                           placeholder="sk-xxx · platform.deepseek.com", label_visibility="collapsed")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("注 册", use_container_width=True, type="primary"):
                err = None
                if not nu or len(nu) < 3: err = "用户名至少3个字符"
                elif len(nu) > 20: err = "最多20个字符"
                elif not re.match(r'^[a-zA-Z0-9_一-鿿]+$', nu): err = "只能中英文数字下划线"
                elif nu in au: err = "此用户名已被预留"
                elif not np or len(np) < 6: err = "密码至少6位"
                elif np != nc: err = "两次密码不一致"
                elif not nk and not skey(): err = "请填写 API Key"
                if err: st.session_state.login_error = err; st.rerun()
                st.session_state.logged_in = True
                st.session_state.username = nu
                st.session_state.is_authorized = False
                st.session_state.is_admin = False
                st.session_state.user_api_key = nk
                st.session_state.login_error = ""; st.rerun()
        with c2:
            if st.button("返回登录", use_container_width=True):
                st.session_state.login_mode = "login"; st.session_state.login_error = ""; st.rerun()

    if st.session_state.login_error: st.error(st.session_state.login_error)
    st.markdown('</div></div>', unsafe_allow_html=True)


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
        badge = "管理员" if is_adm else ("授权用户" if is_au else "访客")
        bc = "#fbbf24" if is_adm else ("#a5b4fc" if is_au else "#707088")
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:16px;">
            <div style="font-size:32px;filter:grayscale({'0' if is_adm else '1'});">{'👑' if is_adm else '👤'}</div>
            <div style="font-size:15px;font-weight:600;color:#d0d0e0;">{u}</div>
            <div style="font-size:11px;color:{bc};margin-top:2px;">{badge}</div>
        </div>""", unsafe_allow_html=True)

        with st.expander("🔑 API 密钥", expanded=True):
            if is_adm or is_au:
                k = skey()
                m = (k[:6] + "····" + k[-4:]) if len(k) > 10 else "(未配置)"
                if not is_adm: m = "sk-····" + k[-4:] if len(k) > 10 else "(已配置)"
                st.text_input("", value=m, disabled=True, label_visibility="collapsed")
                st.caption("DeepSeek · " + ("完整可见" if is_adm else "脱敏"))
            else:
                nk = st.text_input("", type="password", value=st.session_state.user_api_key,
                                   placeholder="sk-xxx", label_visibility="collapsed")
                if nk != st.session_state.user_api_key: st.session_state.user_api_key = nk
                st.caption("platform.deepseek.com")

        with st.expander("⚙️ 对话设置", expanded=True):
            st.session_state.model = st.selectbox(
                "模型", ["deepseek-chat", "deepseek-reasoner"],
                format_func=lambda x: "日常对话" if "chat" in x else "深度思考")
            st.session_state.temp = st.slider("创意度", 0.0, 1.5, 0.7, 0.1)

        with st.expander("📊 统计", expanded=bool(st.session_state.messages)):
            n = len(st.session_state.messages) // 2
            tks = len(SYSTEM_PROMPT) // 2 + sum(len(m["content"]) // 2 for m in st.session_state.messages)
            cost = st.session_state.total_cost
            st.markdown(f"""
            <div class="stat-row">
                <div class="stat-item"><div class="sv">{n}</div><div class="sl">轮对话</div></div>
                <div class="stat-item"><div class="sv">~{tks:,}</div><div class="sl">Token</div></div>
                <div class="stat-item"><div class="sv">¥{cost:.4f}</div><div class="sl">花费</div></div>
            </div>""", unsafe_allow_html=True)

        with st.expander("🛠 工具", expanded=False):
            if st.button("清空对话", use_container_width=True):
                st.session_state.messages = []; st.session_state.total_cost = 0.0; st.rerun()
            if st.session_state.messages:
                txt = "\n\n".join(f"{'你' if m['role']=='user' else '张仕达'}：{m['content']}"
                                  for m in st.session_state.messages)
                st.download_button("导出记录", txt, f"聊天_{datetime.now():%m%d_%H%M}.txt",
                                   use_container_width=True)
            else:
                st.caption("暂无对话")

        with st.expander("ℹ️ 关于", expanded=False):
            st.markdown("""
            <div style="font-size:12px;color:#707088;line-height:2;">
            张仕达的数字分身 · V5<br>
            数据：24,060条 · 2024-2026<br>
            驱动：DeepSeek<br>
            <a href="https://github.com/pythonqq3/persona-chat" style="color:#6366f1;">GitHub ↗</a>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")
        if not st.session_state.show_logout:
            if st.button("退出登录", use_container_width=True):
                st.session_state.show_logout = True; st.rerun()
        else:
            st.warning("退出将清空对话")
            q1, q2 = st.columns(2)
            with q1:
                if st.button("确认", use_container_width=True, type="primary"):
                    st.session_state.show_logout = False; do_logout()
            with q2:
                if st.button("取消", use_container_width=True):
                    st.session_state.show_logout = False; st.rerun()

    # ====== 顶部 ======
    st.markdown(f"""
    <div class="top-bar">
        <div class="brand">
            <div class="avatar">张</div>
            <div>
                <div class="name">张仕达</div>
            </div>
        </div>
        <div class="status">
            <div class="status-dot"></div>{'在线' if key else '未连接'}
        </div>
    </div>
    <div class="tag-row">
        <span class="tag-item">🏸 羽毛球</span>
        <span class="tag-item">📝 写诗词</span>
        <span class="tag-item">☯ 道家思想</span>
        <span class="tag-item">🎮 王者荣耀</span>
        <span class="tag-item">💻 编程</span>
        <span class="tag-item">🏃 跑步</span>
    </div>
    """, unsafe_allow_html=True)

    # ====== 欢迎区 ======
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-wrap">
            <div class="welcome-row">
                <div class="welcome-card"><span class="wc-icon">🏸</span><span class="wc-text">羽毛球<br>怎么练</span></div>
                <div class="welcome-card"><span class="wc-icon">📝</span><span class="wc-text">写首诗<br>来看看</span></div>
                <div class="welcome-card"><span class="wc-icon">☯</span><span class="wc-text">无为<br>是什么</span></div>
                <div class="welcome-card"><span class="wc-icon">💭</span><span class="wc-text">最近<br>好烦</span></div>
                <div class="welcome-card"><span class="wc-icon">🎮</span><span class="wc-text">来打<br>王者</span></div>
                <div class="welcome-card"><span class="wc-icon">🤔</span><span class="wc-text">人生<br>有意义吗</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(4)
        for i, s in enumerate(SUGGESTIONS):
            with cols[i % 4]:
                if st.button(s, key=f"s_{i}", use_container_width=True):
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
                ph.markdown('<div class="type-dots"><span></span><span></span><span></span></div>',
                            unsafe_allow_html=True)
                try:
                    msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
                    reply, usage = call_api(msgs, key, st.session_state.model, st.session_state.temp)
                    ph.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    if usage:
                        c = (usage.get("prompt_tokens", 0) * 1 + usage.get(
                            "completion_tokens", 0) * 2) / 1_000_000
                        st.session_state.total_cost += c
                except urllib.error.HTTPError as e:
                    m = {401: "密钥无效", 402: "余额不足", 429: "太频繁了"}
                    ph.error(m.get(e.code, f"错误 {e.code}"))
                except Exception as e:
                    ph.error(f"网络异常：{str(e)[:100]}")
            st.rerun()


# ============================================================
chat_page() if st.session_state.logged_in else auth_page()
