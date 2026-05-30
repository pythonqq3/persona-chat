"""
张仕达数字分身 · 全功能版
"""

import streamlit as st
import json
import urllib.request
import urllib.error
import os
import re
import hashlib
import time
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="张仕达 · 数字分身", page_icon="👤", layout="wide",
                   initial_sidebar_state="expanded",
                   menu_items={"Get Help": None, "Report a bug": None, "About": "张仕达的数字分身"})

# ============================================================
# 全局 CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
html,body,[class*="css"]{font-family:'Noto Sans SC',-apple-system,sans-serif;scroll-behavior:smooth}
#MainMenu,footer,header{visibility:hidden}

/* 主卡片 */
.main-header{background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);border-radius:16px;padding:24px 32px;margin-bottom:16px;color:#fff;box-shadow:0 8px 32px rgba(0,0,0,.3);position:relative;overflow:hidden}
.main-header::before{content:'';position:absolute;top:-50%;right:-20%;width:200px;height:200px;background:radial-gradient(circle,rgba(168,192,255,.15),transparent);border-radius:50%}
.main-header .name{font-size:26px;font-weight:700;background:linear-gradient(90deg,#a8c0ff,#c4b5fd);-webkit-background-clip:text;-webkit-text-fill-color:transparent;position:relative;z-index:1}
.main-header .tagline{font-size:13px;color:#a0aec0;margin-top:4px;position:relative;z-index:1}
.main-header .tags{margin-top:10px;display:flex;gap:6px;flex-wrap:wrap;position:relative;z-index:1}
.main-header .tag{background:rgba(255,255,255,.08);color:#c8c8f0;padding:3px 10px;border-radius:14px;font-size:11px;backdrop-filter:blur(4px)}

/* 状态 */
.status-badge{display:flex;align-items:center;gap:8px;padding:10px 14px;border-radius:12px;font-size:12px;font-weight:500}
.status-badge.online{background:rgba(52,211,153,.1);color:#34d399;border:1px solid rgba(52,211,153,.2)}
.status-badge.offline{background:rgba(251,191,36,.1);color:#fbbf24;border:1px solid rgba(251,191,36,.2)}
.status-dot{width:7px;height:7px;border-radius:50%;animation:pulse 2s infinite}
.status-dot.green{background:#34d399}.status-dot.yellow{background:#fbbf24}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}

/* 欢迎卡片 */
.welcome-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px;margin:12px 0}
.welcome-card{background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.05);border-radius:12px;padding:14px 10px;text-align:center;transition:all .2s;cursor:pointer}
.welcome-card:hover{background:rgba(255,255,255,.06);border-color:rgba(168,192,255,.25);transform:translateY(-2px);box-shadow:0 4px 16px rgba(0,0,0,.2)}
.welcome-card .icon{font-size:24px;margin-bottom:4px}
.welcome-card .text{font-size:11px;color:#9ca3af;line-height:1.5}

/* 快捷回复 */
.quick-replies{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0}
.quick-reply{background:rgba(168,192,255,.08);color:#a8c0ff;border:1px solid rgba(168,192,255,.15);border-radius:18px;padding:5px 14px;font-size:12px;cursor:pointer;transition:all .15s;white-space:nowrap}
.quick-reply:hover{background:rgba(168,192,255,.18);border-color:rgba(168,192,255,.4)}

/* 打字动画 */
.typing-dots{display:flex;gap:4px;padding:8px 0}
.typing-dots span{width:6px;height:6px;border-radius:50%;background:#6b7280;animation:typing 1.4s infinite}
.typing-dots span:nth-child(2){animation-delay:.2s}
.typing-dots span:nth-child(3){animation-delay:.4s}
@keyframes typing{0%,60%,100%{opacity:.2;transform:translateY(0)}30%{opacity:1;transform:translateY(-4px)}}

/* 统计 */
.stat-row{display:flex;gap:6px;margin:6px 0}
.stat-item{flex:1;background:rgba(255,255,255,.025);border-radius:8px;padding:10px 8px;text-align:center}
.stat-item .value{font-size:18px;font-weight:700;color:#a8c0ff}
.stat-item .label{font-size:10px;color:#6b7280;margin-top:1px}

/* 登录 */
.auth-box{max-width:420px;margin:30px auto;background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);border-radius:20px;padding:40px 36px;text-align:center}
.auth-box .logo{font-size:48px;margin-bottom:8px}
.auth-box h2{font-size:20px;font-weight:700;color:#e0e0f0;margin-bottom:2px}
.auth-box .sub{font-size:12px;color:#6b7280;margin-bottom:24px}

/* 侧边栏 */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0f0f1a,#1a1a2e);border-right:1px solid rgba(255,255,255,.05)}
[data-testid="stSidebar"] .stButton>button{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);color:#d0d0e0}
[data-testid="stSidebar"] .stButton>button:hover{background:rgba(255,255,255,.08);border-color:rgba(168,192,255,.3)}

/* 通用 */
hr{border-color:rgba(255,255,255,.05)!important}
.stButton>button{border-radius:10px!important;font-weight:500!important;transition:all .15s!important}
.stButton>button:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,.2)}
[data-testid="stExpander"]{border-radius:12px!important;border:1px solid rgba(255,255,255,.05)!important;background:rgba(255,255,255,.01)!important}

/* 移动端优化 */
@media(max-width:768px){
    .main-header{padding:16px 20px}.main-header .name{font-size:22px}
    .welcome-grid{grid-template-columns:repeat(3,1fr);gap:6px}
    .auth-box{padding:28px 20px;margin:20px 10px}
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# 数据加载
# ============================================================
@st.cache_data
def load_skill():
    p = Path(__file__).parent.parent / "output" / "persona-me" / "SKILL.md"
    with open(p, "r", encoding="utf-8") as f:
        raw = f.read()
    return raw[raw.find("---", 3) + 3:].strip() if raw.startswith("---") else raw.strip()


SYSTEM_PROMPT = load_skill()
SUGGESTIONS = ["最近在干嘛", "写首诗", "无为是什么意思", "我好累", "你觉得人生的意义是什么",
               "羽毛球怎么练", "你喜欢什么样的女生", "来句道家的东西"]


# ============================================================
# 认证
# ============================================================
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


# ============================================================
# API
# ============================================================
def chat_ds(messages, api_key, model="deepseek-chat", temp=0.7):
    body = json.dumps({"model": model, "messages": messages,
                       "temperature": temp, "max_tokens": 400}).encode("utf-8")
    req = urllib.request.Request("https://api.deepseek.com/v1/chat/completions", data=body,
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        r = json.loads(resp.read().decode("utf-8"))
        return r["choices"][0]["message"]["content"], r.get("usage", {})


# ============================================================
# Session 初始化
# ============================================================
INIT = {
    "logged_in": False, "username": "", "is_admin": False, "is_authorized": False,
    "user_api_key": "", "messages": [], "total_cost": 0.0,
    "login_mode": "login", "login_error": "",
    "sidebar_model": "deepseek-chat", "sidebar_temp": 0.7,
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
# 登录页
# ============================================================
def auth_page():
    st.markdown("""
    <div style="text-align:center;padding-top:20px;">
        <div style="font-size:42px;">👤</div>
        <div style="font-size:22px;font-weight:700;color:#e0e0f0;margin-top:6px;">张仕达的数字分身</div>
        <div style="font-size:13px;color:#6b7280;">两万四千条真实聊天记录 · 十九岁大学生</div>
    </div>""", unsafe_allow_html=True)

    mode = st.session_state.login_mode
    auth_users = get_authorized()
    admins = get_admins()

    _, col, _ = st.columns([1, 1.3, 1])
    with col:
        st.markdown('<div class="auth-box">', unsafe_allow_html=True)

        if mode == "login":
            st.markdown('<div class="logo">🔐</div>', unsafe_allow_html=True)
            st.markdown("<h2>登录</h2>", unsafe_allow_html=True)
            st.markdown('<p class="sub">已有账号直接登录</p>', unsafe_allow_html=True)

            u = st.text_input("用户名", key="li_u", placeholder="输入用户名", label_visibility="collapsed")
            p = st.text_input("密码", type="password", key="li_p", placeholder="输入密码", label_visibility="collapsed")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("登 录", use_container_width=True, type="primary"):
                    if not u or not p:
                        st.session_state.login_error = "请输入用户名和密码"
                        st.rerun()
                    elif u in auth_users:
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
                if st.button("注册新账号", use_container_width=True):
                    st.session_state.login_mode = "register"
                    st.session_state.login_error = ""
                    st.rerun()

        else:
            st.markdown('<div class="logo">📝</div>', unsafe_allow_html=True)
            st.markdown("<h2>注册</h2>", unsafe_allow_html=True)
            st.markdown('<p class="sub">授权用户联系管理员 · 访客需自备 Key</p>', unsafe_allow_html=True)

            nu = st.text_input("用户名", key="rg_u", placeholder="3-20个字符", label_visibility="collapsed")
            np = st.text_input("密码", type="password", key="rg_p", placeholder="至少6位", label_visibility="collapsed")
            nc = st.text_input("确认密码", type="password", key="rg_c", placeholder="再次输入", label_visibility="collapsed")
            nk = st.text_input("API Key（授权用户可跳过）", type="password", key="rg_k",
                               placeholder="sk-xxx，platform.deepseek.com", label_visibility="collapsed")

            ca, cb = st.columns(2)
            with ca:
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
                        st.session_state.login_error = err
                        st.rerun()
                    st.session_state.logged_in = True
                    st.session_state.username = nu
                    st.session_state.is_authorized = False
                    st.session_state.is_admin = False
                    st.session_state.user_api_key = nk
                    st.session_state.login_error = ""
                    st.rerun()
            with cb:
                if st.button("返回登录", use_container_width=True):
                    st.session_state.login_mode = "login"
                    st.session_state.login_error = ""
                    st.rerun()

        if st.session_state.login_error:
            st.error(st.session_state.login_error)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="text-align:center;color:#4b5563;font-size:11px;margin-top:12px;">🔒 密钥全程加密 · 授权用户自动配置</div>', unsafe_allow_html=True)


# ============================================================
# 聊天页
# ============================================================
def chat_page():
    u = st.session_state.username
    is_adm = st.session_state.is_admin
    is_au = st.session_state.is_authorized
    key = active_key()

    # ====== 侧边栏 ======
    with st.sidebar:
        # ---- 账号信息 ----
        badge = "👑 管理员" if is_adm else ("🔓 授权用户" if is_au else "📝 访客")
        bc = "#fbbf24" if is_adm else ("#34d399" if is_au else "#6b7280")
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:16px;">
            <div style="font-size:32px;">{'👑' if is_adm else '👤'}</div>
            <div style="font-size:16px;font-weight:700;color:#e0e0f0;">{u}</div>
            <div style="font-size:10px;color:{bc};margin-top:2px;">{badge}</div>
        </div>""", unsafe_allow_html=True)

        # ---- API 状态 ----
        with st.expander("🔑 API", expanded=False):
            if is_adm or is_au:
                k = get_key()
                masked = (k[:6] + "****" + k[-4:]) if len(k) > 10 else "(未配置)"
                if not is_adm:
                    masked = "sk-****" + k[-4:] if len(k) > 10 else "(已配置)"
                st.text_input("密钥", value=masked, disabled=True, label_visibility="collapsed")
                st.caption("DeepSeek · 已配置 · " + ("完整可见" if is_adm else "脱敏显示"))
            else:
                nk = st.text_input("密钥", type="password", value=st.session_state.user_api_key,
                                   placeholder="sk-xxxxxxxx", label_visibility="collapsed")
                if nk != st.session_state.user_api_key:
                    st.session_state.user_api_key = nk
                st.caption("platform.deepseek.com 免费获取")

        # ---- 对话设置 ----
        with st.expander("⚙️ 设置", expanded=False):
            st.session_state.sidebar_model = st.selectbox(
                "模型", ["deepseek-chat", "deepseek-reasoner"],
                format_func=lambda x: "💬 日常对话" if "chat" in x else "🧠 深度思考")
            st.session_state.sidebar_temp = st.slider("随机度", 0.0, 1.5, 0.7, 0.1,
                                                      help="0=稳定  1.5=创意")
            st.caption("💡 日常聊天用「日常对话」即可")

        # ---- 统计 ----
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

        # ---- 工具 ----
        with st.expander("🛠 工具", expanded=False):
            if st.button("🗑 清空对话", use_container_width=True):
                st.session_state.messages = []
                st.session_state.total_cost = 0.0
                st.rerun()
            if st.session_state.messages:
                txt = "\n\n".join(f"{'你' if m['role']=='user' else '张仕达'}：{m['content']}"
                                  for m in st.session_state.messages)
                st.download_button("📥 导出记录", txt, f"聊天_{datetime.now():%m%d_%H%M}.txt",
                                   use_container_width=True)
            else:
                st.caption("暂无对话记录")

        # ---- 关于 ----
        with st.expander("ℹ️ 关于", expanded=False):
            st.markdown("""
            <div style="font-size:12px;color:#9ca3af;line-height:1.8;">
            <b>张仕达的数字分身</b><br>
            人格模型版本：V5<br>
            训练数据：24,060 条微信消息<br>
            数据时间：2024.08 - 2026.05<br>
            驱动模型：DeepSeek<br>
            部署平台：Streamlit Cloud<br>
            源码：<a href="https://github.com/pythonqq3/persona-chat" style="color:#a8c0ff;">GitHub</a><br>
            域名：chat.061230zsd.xyz<br>
            <br>
            ⚠️ 本AI仅供娱乐，<br>
            不构成真实意见或立场
            </div>
            """, unsafe_allow_html=True)

        # ---- 退出 ----
        st.markdown("---")
        if "show_logout" not in st.session_state:
            st.session_state.show_logout = False
        if not st.session_state.show_logout:
            if st.button("🚪 退出登录", use_container_width=True):
                st.session_state.show_logout = True
                st.rerun()
        else:
            st.warning("退出将清空当前对话")
            cq1, cq2 = st.columns(2)
            with cq1:
                if st.button("✅ 确认", use_container_width=True, type="primary"):
                    st.session_state.show_logout = False
                    logout()
            with cq2:
                if st.button("❌ 取消", use_container_width=True):
                    st.session_state.show_logout = False
                    st.rerun()

    # ====== 主区域 ======
    c1, c2 = st.columns([5, 1])
    with c1:
        st.markdown("""
        <div class="main-header">
            <div class="name">张仕达</div>
            <div class="tagline">19岁 · 江西中医药大学 · 打羽毛球 · 写诗词 · 偶尔毒舌 · 聊道家</div>
            <div class="tags">
                <span class="tag">🏸 羽毛球</span><span class="tag">📝 诗词</span>
                <span class="tag">☯ 道家</span><span class="tag">🎮 王者</span>
                <span class="tag">💻 编程</span><span class="tag">🏃 跑步</span>
            </div>
        </div>""", unsafe_allow_html=True)
    with c2:
        if key:
            st.markdown('<div class="status-badge online"><div class="status-dot green"></div>在线</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-badge offline"><div class="status-dot yellow"></div>离线</div>',
                        unsafe_allow_html=True)

    # 欢迎区
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-grid">
            <div class="welcome-card"><div class="icon">🏸</div><div class="text">羽毛球<br>怎么练</div></div>
            <div class="welcome-card"><div class="icon">📝</div><div class="text">写首诗<br>来看看</div></div>
            <div class="welcome-card"><div class="icon">☯</div><div class="text">无为<br>是什么</div></div>
            <div class="welcome-card"><div class="icon">💭</div><div class="text">最近<br>好烦</div></div>
            <div class="welcome-card"><div class="icon">🎮</div><div class="text">来打<br>王者</div></div>
            <div class="welcome-card"><div class="icon">🤔</div><div class="text">人生<br>有意义吗</div></div>
        </div>""", unsafe_allow_html=True)

        # 快捷回复按钮
        st.caption("💡 快速话题")
        cols = st.columns(4)
        for i, s in enumerate(SUGGESTIONS):
            with cols[i % 4]:
                if st.button(s, key=f"sug_{i}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": s})
                    st.rerun()

    # 对话
    for i, msg in enumerate(st.session_state.messages):
        role_label = "你" if msg["role"] == "user" else "张仕达"
        time_str = datetime.now().strftime("%H:%M")
        avatar = "👤" if msg["role"] == "user" else None
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # 输入
    prompt = st.chat_input("说点什么..." if st.session_state.messages else f"嘿 {u}，想聊什么？")

    if prompt:
        if not key:
            st.error("请先在侧边栏配置 API Key")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                ph = st.empty()
                # 打字动画
                ph.markdown('<div class="typing-dots"><span></span><span></span><span></span></div>',
                            unsafe_allow_html=True)
                try:
                    msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
                    reply, usage = chat_ds(msgs, key, st.session_state.sidebar_model, st.session_state.sidebar_temp)
                    ph.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})

                    if usage:
                        cost_add = (usage.get("prompt_tokens", 0) * 1 + usage.get("completion_tokens", 0) * 2) / 1_000_000
                        st.session_state.total_cost += cost_add
                except urllib.error.HTTPError as e:
                    m = {401: "密钥无效", 402: "余额不足，联系管理员", 429: "太频繁了，稍等"}
                    ph.error(m.get(e.code, f"API 错误 {e.code}"))
                except Exception as e:
                    ph.error(f"网络异常：{str(e)[:100]}")

            st.rerun()


# ============================================================
# 入口
# ============================================================
chat_page() if st.session_state.logged_in else auth_page()
