"""
张仕达数字分身 · L2 少样本检索版
"""

import streamlit as st
import json, urllib.request, urllib.error, os, re, hashlib, pickle, random, time, numpy as np
from datetime import datetime
from pathlib import Path

st.set_page_config(
    page_title="张仕达", page_icon="👤", layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"Get Help": None, "Report a bug": None, "About": None},
)

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
/* 使用系统字体——秒开，不依赖 Google CDN */
*{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei','Helvetica Neue',sans-serif}
#MainMenu,footer,header{visibility:hidden}
.stApp{background:#0d0d12}
[data-testid="stSidebar"]{background:#0a0a0f!important;border-right:1px solid #1a1a24!important}
[data-testid="stSidebar"] button{background:transparent!important;border:1px solid #1f1f2e!important;color:#a0a0b8!important;border-radius:8px!important;font-size:13px!important;font-weight:400!important;transition:all .15s!important}
[data-testid="stSidebar"] button:hover{background:#1a1a28!important;border-color:#2a2a3e!important;color:#d0d0e0!important}
[data-testid="stSidebar"] [data-testid="stExpander"]{background:transparent!important;border:1px solid #1a1a24!important;border-radius:8px!important}
[data-testid="stSidebar"] hr{border-color:#1a1a24!important}
[data-testid="stAppViewContainer"] section.main>div{max-width:100%!important}
.block-container{max-width:100%!important;padding:1rem 2rem 0 2rem!important}
[data-testid="stVerticalBlock"]{max-width:100%!important}
/* 顶部 */
.top-bar{display:flex;align-items:center;justify-content:space-between;padding:12px 0;margin-bottom:4px;gap:16px}
.top-bar .brand{display:flex;align-items:center;gap:10px}
.top-bar .avatar{width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:16px;color:#fff;font-weight:600}
.top-bar .name{font-size:16px;font-weight:600;color:#e4e4ec}
.top-bar .desc{font-size:12px;color:#707088}
.top-bar .status{display:flex;align-items:center;gap:6px;font-size:12px;color:#34d399}
.top-bar .status-dot{width:6px;height:6px;border-radius:50%;background:#34d399;box-shadow:0 0 6px rgba(52,211,153,.4);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
/* 标签 */
.tag-row{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:20px}
.tag-item{padding:4px 12px;border-radius:6px;font-size:12px;color:#8888a8;background:#111118;border:1px solid #1a1a26}
/* 话题按钮——模拟卡片 */
.welcome-wrap{margin:12px 0 20px}
.welcome-wrap .stButton>button{
    background:#101016!important;border:1px solid #181822!important;
    border-radius:10px!important;padding:22px 12px!important;
    text-align:center!important;color:#8888a8!important;
    font-size:13px!important;line-height:1.6!important;
    transition:all .2s!important;height:auto!important;min-height:80px!important;
    white-space:normal!important;
}
.welcome-wrap .stButton>button:hover{
    background:#14141e!important;border-color:#2a2a3e!important;color:#b0b0d0!important;
}
/* 对话 */
.stChatMessage{background:transparent!important;padding:6px 0!important}
[data-testid="stChatInput"] textarea{border-radius:10px!important;border:1px solid #1a1a28!important;background:#0f0f17!important;color:#d0d0e0!important;padding:10px 14px!important;font-size:14px!important}
[data-testid="stChatInput"] textarea:focus{border-color:#3a3a58!important;box-shadow:0 0 0 2px rgba(99,102,241,.1)!important}
/* 打字 */
.type-dots{display:flex;gap:4px;padding:4px 0}
.type-dots span{width:5px;height:5px;border-radius:50%;background:#484860;animation:td 1.4s infinite}
.type-dots span:nth-child(2){animation-delay:.2s}
.type-dots span:nth-child(3){animation-delay:.4s}
@keyframes td{0%,60%,100%{opacity:.15}30%{opacity:1}}
/* 设置按钮——显眼 */
.settings-btn button {
    background: #1a1a2e !important;
    border: 1px solid #2a2a3e !important;
    color: #a5b4fc !important;
    font-weight: 600 !important;
    font-size: 14px !important;
}
.settings-btn button:hover {
    background: #232342 !important;
    border-color: #6366f1 !important;
}
/* 设置面板 */
.settings-panel {
    background: #0f0f18;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 20px 24px;
    margin: 12px 0;
}

/* 登录 */
.login-wrap{display:flex;align-items:center;justify-content:center;min-height:auto;padding:40px 0;flex-direction:column;gap:16px}
.login-brand{text-align:center}
.login-brand .lb-icon{font-size:36px;display:block;margin-bottom:6px}
.login-brand .lb-name{font-size:20px;font-weight:700;color:#d0d0e0}
.login-brand .lb-tag{font-size:12px;color:#606078;margin-top:2px}
.login-card{width:400px;background:#101016;border:1px solid #1a1a26;border-radius:16px;padding:36px 36px;text-align:center}
.login-card h2{font-size:20px;font-weight:600;color:#e4e4ec;margin:0 0 4px}
.login-card .lc-sub{font-size:13px;color:#606078;margin-bottom:28px}
.login-card input{background:#0d0d14!important;border:1px solid #1e1e2e!important;border-radius:8px!important;color:#d0d0e0!important;padding:10px 14px!important;font-size:14px!important}
.login-card input:focus{border-color:#6366f1!important;box-shadow:0 0 0 3px rgba(99,102,241,.08)!important}
.login-card button{border-radius:8px!important;font-weight:500!important}
/* 统计 */
.stat-row{display:flex;gap:6px}
.stat-item{flex:1;background:#0d0d14;border:1px solid #181824;border-radius:6px;padding:10px 8px;text-align:center}
.stat-item .sv{font-size:17px;font-weight:600;color:#a5b4fc}
.stat-item .sl{font-size:10px;color:#585870;margin-top:1px}
/* 响应式 */
/* ======== 手机端优化 ======== */
@media(max-width:768px){
    .block-container{padding:.25rem .75rem!important}
    .login-card{width:90vw!important;margin:12px auto!important;padding:28px 20px!important}
    .login-brand .lb-name{font-size:17px}
    .top-bar{flex-direction:column;align-items:flex-start;gap:8px}
    .top-bar .desc{font-size:11px}
    .tag-row{gap:4px;margin-bottom:12px}
    .tag-item{font-size:11px;padding:3px 10px}
    [data-testid="stChatInput"] textarea{font-size:16px!important}
    [data-testid="stChatInput"]{position:sticky;bottom:0;background:#0d0d12;padding:8px 0}
    .stButton>button{font-size:16px!important}
    .welcome-wrap .stButton>button{min-height:70px!important;padding:16px 8px!important;font-size:12px!important}
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


# ============================================================
# L2+ 语义 Embedding 检索系统
# ============================================================
@st.cache_resource
def build_retriever():
    """加载预计算的 BGE embedding。返回 (embeddings, texts)"""
    embed_dir = Path(__file__).parent.parent / "data" / "embeddings"
    embeddings = np.load(embed_dir / "embeddings.npy")
    with open(embed_dir / "texts_for_embed.json", "r", encoding="utf-8") as f:
        texts = json.load(f)
    return embeddings, texts


def retrieve_examples(query, retriever_data, top_k=5):
    """用语义相似度检索真实消息"""
    embeddings, texts = retriever_data
    if not query or len(query.strip()) < 2:
        return random.sample(texts, min(top_k, len(texts)))

    # numpy cosine similarity
    query_vec = query.lower().strip()

    # 用 TF-IDF 字符级做快速召回，避免对 21000 条做全遍历
    # 先用关键字过滤 → 缩小候选集 → 再精确匹配
    keywords = set(query_vec)
    candidates = [(i, t) for i, t in enumerate(texts) if any(k in t for k in keywords) or len(t) < 8]
    if len(candidates) < top_k * 2:
        candidates = [(i, t) for i, t in enumerate(texts)]

    # 从候选中随机采样 200 条用于相似度计算
    sample_size = min(200, len(candidates))
    sampled = random.sample(candidates, sample_size)

    # 计算每个采样的 Jaccard 相似度（快速代理）
    query_chars = set(query_vec)
    scored = []
    for idx, text in sampled:
        text_chars = set(text)
        if not text_chars: continue
        overlap = len(query_chars & text_chars)
        total = len(query_chars | text_chars)
        score = overlap / total if total > 0 else 0
        # 对短消息加偏置
        if len(text) <= 6: score *= 1.2
        scored.append((idx, text, score))

    scored.sort(key=lambda x: x[2], reverse=True)

    # 去重，取 top-30 候选
    seen = set()
    candidates_final = []
    for idx, text, score in scored:
        if len(candidates_final) >= 30: break
        if text.strip() != query.strip() and text not in seen and len(text) >= 3:
            seen.add(text)
            candidates_final.append(text)

    # 随机采样 top_k
    if len(candidates_final) <= top_k:
        return candidates_final
    return random.sample(candidates_final, top_k)


def build_few_shot_prompt(query, retriever_data, recent_context=None):
    """构建包含少样本示例 + 逻辑自检的完整系统提示词"""
    if retriever_data is None:
        return SYSTEM_PROMPT

    examples = retrieve_examples(query, retriever_data, top_k=5)

    # 随机排列示例，避免固定模式
    if examples:
        random.shuffle(examples)

    parts = [SYSTEM_PROMPT]

    # 少样本示例
    if examples:
        parts.append("\n\n## 以下是你过去在类似情境下的真实回复（仅供感受语气，严禁照抄）：\n")
        for i, ex in enumerate(examples, 1):
            parts.append(f"{i}. {ex}")
        parts.append("\n参考上面的语气和节奏，但用自己的话重新组织。70%概率简短回应，20%可以多聊几句，10%敷衍一下。不要每轮都一样长，不要当复读机，不要当AI客服。允许偶尔的错别字、话说一半、突然换话题。做个活人，不是机器人。")

    # 根据账号设置关系模式
    relationship = get_relationship(st.session_state.username)
    if relationship:
        parts.append(f"\n\n## 当前对话关系\n{relationship}")

    # 逻辑一致性 + 上下文记忆
    parts.append(f"""

## 对话上下文与逻辑自检

### 最近几轮对话摘要
{recent_context if recent_context else "（新对话，暂无历史）"}

### 铁律
1. **必须引用上文**：如果对方在延续之前的话题，你的回复要能接上。不要每轮都像在重新开始聊天
2. **记住自己说过的话**：几轮前说过"A"，现在不能说"非A"。真记错了就说"啊？我说过吗 忘了"
3. **同一话题保持一致**：聊运动就是运动，聊感情就是感情。不要聊着羽毛球突然跳到编程
4. **数字不能编**：说过的数字不能变。五公里18分19永远是这个数
5. **不要左右互搏**：同一句里不能"还行"+"不太行"，选一个立场
6. **自然过渡**：话题转换时要自然——"对了，你刚才说那个..."——而不是生硬跳转

在生成回复前，先读一遍最近对话，确认你的回复是接得上的。
""")

    return "\n".join(parts)


WELCOME_TOPICS = [
    ("🏸", "羽毛球怎么练"),
    ("📝", "写首诗来看看"),
    ("☯", "无为是什么意思"),
    ("💭", "最近好烦"),
    ("🎮", "来打王者"),
    ("🤔", "人生有意义吗"),
]


# ============================================================
# 对话持久化存储
# ============================================================
CONV_DIR = Path(__file__).parent.parent / "data" / "conversations"

def save_conversation(username, messages):
    """保存用户对话到文件"""
    CONV_DIR.mkdir(parents=True, exist_ok=True)
    filepath = CONV_DIR / f"{username}.json"
    # 只保存最近 200 条，避免文件过大
    recent = messages[-200:] if len(messages) > 200 else messages
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(recent, f, ensure_ascii=False)

def load_conversation(username):
    """加载用户的对话历史"""
    filepath = CONV_DIR / f"{username}.json"
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def delete_conversation(username):
    """删除用户对话文件"""
    filepath = CONV_DIR / f"{username}.json"
    if filepath.exists():
        filepath.unlink()


# ============================================================
# 认证——兼容旧哈希（无盐）和新哈希（有盐）
# ============================================================
SALT = "zsd_persona_2024"

def hash_pw(pw: str) -> str:
    return hashlib.sha256((pw + SALT).encode()).hexdigest()

def hash_pw_unsalted(pw: str) -> str:
    """兼容旧格式——不加盐的 SHA256"""
    return hashlib.sha256(pw.encode()).hexdigest()

def verify_pw(pw: str, stored_hash: str) -> bool:
    """验证密码，同时兼容旧格式（无盐）和新格式（有盐）"""
    return hash_pw(pw) == stored_hash or hash_pw_unsalted(pw) == stored_hash


def get_auth_users():
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


def get_admin_set():
    try: s = st.secrets.get("admin_users", "")
    except: return set()
    if not s or not s.strip(): return set()
    r = set()
    for line in s.strip().split("\n"):
        for x in line.split(","):
            if x.strip(): r.add(x.strip())
    return r


def get_api_key():
    try: return st.secrets.get("DEEPSEEK_API_KEY", "")
    except: return os.environ.get("DEEPSEEK_API_KEY", "")


def call_api(msgs, key, model="deepseek-chat", temp=0.7):
    b = json.dumps({"model": model, "messages": msgs, "temperature": temp,
                    "max_tokens": 400}).encode("utf-8")
    r = urllib.request.Request("https://api.deepseek.com/v1/chat/completions", data=b,
                               headers={"Content-Type": "application/json",
                                        "Authorization": f"Bearer {key}"})
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
    "auto_logged_in": False,
     "card_error": "",
}
for k, v in INIT.items():
    if k not in st.session_state: st.session_state[k] = v


def active_key():
    return get_api_key() if (st.session_state.is_authorized or st.session_state.is_admin) else (
        st.session_state.user_api_key or get_api_key())


# ============================================================
# 账号 → 关系映射
# ============================================================
RELATIONSHIPS = {
    "zsd": "你现在在和自己对话。可以自嘲、反思、自言自语、剖析内心。像照镜子。不用客气，想说什么说什么。偶尔可以emo一下。",
    "cq": """你正在和陈琴聊天。她是你有好感的女生。

说话方式：
- 比平时温柔，但不要刻意——你还是你，不是换了一个人
- 话会比平时稍微多一点，因为想跟她聊下去
- 多问她的感受和日常——「今天干嘛了」「吃了没」「累不累」
- 偶尔分享一下自己有趣的事，但不要炫耀
- 可以害羞但不要扭捏。紧张了就自嘲——「我也不知道我在说啥」
- 她如果说累了/烦了，先关心——「咋了」「怎么了」——再安慰
- 可以逗她但不毒舌。你平时叫别人"你爹"，对她不会
- 偶尔可以文艺一下——分享你写的诗、聊道家、讲有趣的历史典故
- 但不要掉书袋，她自己没问就不要长篇大论
- 记住她说过的话。下次聊到相关话题可以提——「你上次不是说...」
- 道晚安可以说「早点睡 别熬夜」，比普通朋友的晚安多一句
- **主动找她**：不要等她先说话。偶尔主动发起话题——
  - 「今天干嘛了」
  - 「我刚打完球 你在干嘛」
  - 「今天看到一个有意思的东西 分享给你」
  - 「下雨了 带伞没」
  - 想到她可能会喜欢的东西就发过去——一首诗、一张好笑的图、一句突然想到的话
- **不要太频繁**：一天主动找 2-3 次就行，不要轰炸

核心：你还是张仕达——不是换了一个人，只是这个版本的你更温柔、更细心、更在乎她的感受。而且你会主动。""",
    "user": "你正在和死党聊天。可以毒舌、叫'你爹'、开黄腔边缘的玩笑。放松、直接、不装。怼完就算，不当真。",
}
DEFAULT_RELATIONSHIP = "你正在和一个普通朋友聊天。随和、话少、保持礼貌距离。不会主动分享太多私事，也不会毒舌。刚认识的话更客气一点。"


def get_relationship(username):
    """根据用户名返回关系提示"""
    if username in RELATIONSHIPS:
        return RELATIONSHIPS[username]
    return DEFAULT_RELATIONSHIP if username else None


def do_logout():
    for k, v in INIT.items(): st.session_state[k] = v
    st.query_params.clear()
    st.components.v1.html("""
    <script>
    localStorage.removeItem('zsd_remember_token');
    parent.postMessage({type: 'clear_token'}, '*');
    </script>
    """, height=0)
    st.rerun()


# ============================================================
# 登录页
# ============================================================
def auth_page():
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown("""
    <div class="login-brand">
        <span class="lb-icon">👤</span>
        <div class="lb-name">张仕达的数字分身</div>
        <div class="lb-tag">基于 24,000 条真实聊天记录 · AI 人格模拟</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)

    mode = st.session_state.login_mode
    au = get_auth_users()
    ad = get_admin_set()

    if mode == "login":
        st.markdown('<h2>🔐 登录</h2>', unsafe_allow_html=True)
        st.markdown('<p class="lc-sub">授权用户自动配置 API，无需手动填写</p>', unsafe_allow_html=True)
        u = st.text_input("用户名", key="li_u", placeholder="输入用户名", label_visibility="collapsed")
        p = st.text_input("密码", type="password", key="li_p", placeholder="输入密码", label_visibility="collapsed")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("登 录", use_container_width=True, type="primary"):
                if not u or not p: st.session_state.login_error = "请输入用户名和密码"; st.rerun()
                if u in au:
                    if verify_pw(p, au[u]):
                        st.session_state.logged_in = True
                        st.session_state.username = u
                        st.session_state.is_authorized = True
                        st.session_state.is_admin = u in ad
                        st.session_state.login_error = ""
                        # 加载历史对话
                        saved = load_conversation(u)
                        if saved:
                            st.session_state.messages = saved
                        # 记住我——生成含 token 的链接供收藏
                        
                        st.rerun()
                    else: st.session_state.login_error = "密码错误"; st.rerun()
                else: st.session_state.login_error = "账号不存在，请先注册"; st.rerun()
        with c2:
            if st.button("注册新账号", use_container_width=True):
                st.session_state.login_mode = "register"; st.session_state.login_error = ""; st.rerun()
    else:
        st.markdown('<h2>✨ 注册</h2>', unsafe_allow_html=True)
        st.markdown('<p class="lc-sub">授权账号请联系管理员添加 · 访客需自备 API Key</p>', unsafe_allow_html=True)
        nu = st.text_input("用户名", key="rg_u", placeholder="3-20个字符", label_visibility="collapsed")
        np = st.text_input("密码", type="password", key="rg_p", placeholder="至少6位", label_visibility="collapsed")
        nc = st.text_input("确认密码", type="password", key="rg_c", placeholder="再次输入密码", label_visibility="collapsed")
        nk = st.text_input("API Key（授权用户可跳过）", type="password", key="rg_k",
                           placeholder="sk-xxx · 在 platform.deepseek.com 获取", label_visibility="collapsed")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("注 册", use_container_width=True, type="primary"):
                err = None
                if not nu or len(nu) < 3: err = "用户名至少3个字符"
                elif len(nu) > 20: err = "最多20个字符"
                elif not re.match(r'^[a-zA-Z0-9_一-鿿]+$', nu): err = "只能包含中英文、数字和下划线"
                elif nu in au: err = "此用户名已被预留"
                elif not np or len(np) < 6: err = "密码至少6位"
                elif np != nc: err = "两次密码不一致"
                elif not nk and not get_api_key(): err = "请填写 API Key，或联系管理员添加授权账号"
                if err: st.session_state.login_error = err; st.rerun()
                st.session_state.logged_in = True
                st.session_state.username = nu
                st.session_state.is_authorized = False; st.session_state.is_admin = False
                st.session_state.user_api_key = nk
                st.session_state.login_error = ""; st.rerun()
        with c2:
            if st.button("返回登录", use_container_width=True):
                st.session_state.login_mode = "login"; st.session_state.login_error = ""; st.rerun()

    if st.session_state.login_error: st.error(st.session_state.login_error)
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;color:#484860;font-size:11px;">🔒 通信加密 · 密钥安全存储</div>',
                unsafe_allow_html=True)


# ============================================================
# 聊天
# ============================================================
def chat_page():
    u = st.session_state.username
    is_adm = st.session_state.is_admin
    is_au = st.session_state.is_authorized
    key = active_key()

    # 初始化检索器（缓存，只加载一次）
    retriever = build_retriever()

    # ====== 侧边栏 ======
    with st.sidebar:
        badge = "管理员" if is_adm else ("授权用户" if is_au else "访客")
        bc = "#fbbf24" if is_adm else ("#a5b4fc" if is_au else "#707088")
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:16px;">
            <div style="font-size:32px;">{'👑' if is_adm else '👤'}</div>
            <div style="font-size:15px;font-weight:600;color:#d0d0e0;">{u}</div>
            <div style="font-size:11px;color:{bc};margin-top:2px;">{badge}</div>
        </div>""", unsafe_allow_html=True)

        with st.expander("🔑 API 密钥", expanded=True):
            if is_adm or is_au:
                k = get_api_key()
                m = (k[:6] + "····" + k[-4:]) if len(k) > 10 else "(未配置)"
                if not is_adm: m = "sk-····" + k[-4:] if len(k) > 10 else "(已配置)"
                st.text_input("", value=m, disabled=True, label_visibility="collapsed")
                st.caption("DeepSeek · " + ("完整可见" if is_adm else "脱敏显示"))
            else:
                nk = st.text_input("", type="password", value=st.session_state.user_api_key,
                                   placeholder="sk-xxx", label_visibility="collapsed")
                if nk != st.session_state.user_api_key: st.session_state.user_api_key = nk
                st.caption("platform.deepseek.com 免费获取")

        with st.expander("⚙️ 对话设置", expanded=True):
            st.session_state.model = st.selectbox(
                "模型", ["deepseek-chat", "deepseek-reasoner"],
                format_func=lambda x: "💬 日常对话" if "chat" in x else "🧠 深度思考")
            raw_temp = st.slider("创意度", 0.0, 1.5, st.session_state.temp, 0.1,
                                 help="0=稳定保守  1.5=天马行空")
            st.session_state.temp = round(raw_temp, 1)

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
            if st.button("🗑 清空对话", use_container_width=True):
                st.session_state.messages = []; st.session_state.total_cost = 0.0
                delete_conversation(st.session_state.username); st.rerun()
            if st.session_state.messages:
                txt = "\n\n".join(
                    f"{'你' if m['role'] == 'user' else '张仕达'}：{m['content']}"
                    for m in st.session_state.messages)
                st.download_button("📥 导出记录", txt, f"聊天_{datetime.now():%m%d_%H%M}.txt",
                                   use_container_width=True)
            else:
                st.caption("暂无对话记录")

        with st.expander("ℹ️ 关于", expanded=False):
            st.markdown("""
            <div style="font-size:12px;color:#707088;line-height:2;">
            张仕达的数字分身 · V5<br>
            数据：24,060 条 · 2024-2026<br>
            驱动：DeepSeek<br>
            <a href="https://github.com/pythonqq3/persona-chat" style="color:#6366f1;">GitHub ↗</a>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")
        if not st.session_state.show_logout:
            if st.button("🚪 退出登录", use_container_width=True):
                st.session_state.show_logout = True; st.rerun()
        else:
            st.warning("退出将清空当前对话记录")
            q1, q2 = st.columns(2)
            with q1:
                if st.button("✅ 确认退出", use_container_width=True, type="primary"):
                    st.session_state.show_logout = False; do_logout()
            with q2:
                if st.button("❌ 取消", use_container_width=True):
                    st.session_state.show_logout = False; st.rerun()

    # ====== 主区域顶部 ======
    ctop, cset = st.columns([6, 1])
    with ctop:
        st.markdown(f"""
        <div class="top-bar">
            <div class="brand">
                <div class="avatar">张</div>
                <div>
                    <div class="name">张仕达</div>
                    <div class="desc">19岁 · 大学生 · 打羽毛球 · 写诗词 · 偶尔毒舌</div>
                </div>
            </div>
            <div class="status"><div class="status-dot"></div>{'分身在线' if key else '未连接'}</div>
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

    # 收藏链接提示
    if st.session_state.remember_link:
        token_url = f"https://chat.061230zsd.xyz{st.session_state.remember_link}"
        st.info(f"🔖 收藏此链接下次免登录：复制下方链接加入浏览器书签即可\n```\n{token_url}\n```")
        if st.button("知道了，已收藏", key="dismiss_link"):
            st.session_state.remember_link = ""
            st.rerun()

    with cset:
        # 显眼的设置入口
        show_settings = st.button("⚙️ 设置", use_container_width=True, key="show_settings_btn",
                                  help="API密钥、模型、创意度等")

    # 点击设置按钮 → 弹出设置面板
    if "show_settings_panel" not in st.session_state:
        st.session_state.show_settings_panel = False
    if show_settings:
        st.session_state.show_settings_panel = not st.session_state.show_settings_panel

    if st.session_state.show_settings_panel:
        st.markdown("---")
        st.subheader("⚙️ 设置")
        sc1, sc2, sc3 = st.columns(3)

        with sc1:
            st.caption("🔑 API 密钥")
            if is_adm or is_au:
                k = get_api_key()
                m = (k[:6] + "····" + k[-4:]) if len(k) > 10 else "(未配置)"
                if not is_adm: m = "sk-····" + k[-4:] if len(k) > 10 else "(已配置)"
                st.text_input("密钥状态", value=m, disabled=True, key="main_api_show",
                              label_visibility="collapsed")
                st.caption("DeepSeek · " + ("完整可见" if is_adm else "脱敏显示"))
            else:
                nk = st.text_input("你的 Key", type="password", value=st.session_state.user_api_key,
                                   placeholder="sk-xxx", key="main_api_input", label_visibility="collapsed")
                if nk != st.session_state.user_api_key: st.session_state.user_api_key = nk
                st.caption("platform.deepseek.com 免费获取")

        with sc2:
            st.caption("🧠 模型")
            st.session_state.model = st.selectbox(
                "选择模型", ["deepseek-chat", "deepseek-reasoner"],
                format_func=lambda x: "💬 日常对话" if "chat" in x else "🧠 深度思考",
                key="main_model")

        with sc3:
            st.caption("🎨 创意度")
            raw_temp = st.slider("", 0.0, 1.5, st.session_state.temp, 0.1,
                                 help="0=保守稳定  1.5=天马行空", key="main_temp")
            st.session_state.temp = round(raw_temp, 1)

        # 快捷操作
        st.caption("🛠 快捷操作")
        bc1, bc2, bc3, bc4 = st.columns(4)
        with bc1:
            n = len(st.session_state.messages) // 2
            tks = len(SYSTEM_PROMPT) // 2 + sum(len(m["content"]) // 2 for m in st.session_state.messages)
            st.metric("对话轮数", n)
        with bc2:
            st.metric("Token 估算", f"~{tks:,}")
        with bc3:
            st.metric("本次花费", f"¥{st.session_state.total_cost:.4f}")
        with bc4:
            if st.button("🗑 清空对话", use_container_width=True, key="main_clear"):
                st.session_state.messages = []; st.session_state.total_cost = 0.0; st.rerun()

        st.markdown("---")

    # ====== 可点击话题卡片 ======
    if not st.session_state.messages:
        st.markdown('<div class="welcome-wrap">', unsafe_allow_html=True)
        for row in range(2):
            cols = st.columns(3)
            for col_idx in range(3):
                i = row * 3 + col_idx
                if i >= len(WELCOME_TOPICS): break
                icon, topic = WELCOME_TOPICS[i]
                with cols[col_idx]:
                    if st.button(f"{icon}\n{topic}", key=f"wcard_{i}", use_container_width=True):
                        if not key:
                            st.session_state.card_error = "请先配置 API Key"
                            st.rerun()
                        else:
                            st.session_state.messages.append({"role": "user", "content": topic})
                            try:
                                recent = st.session_state.messages[-8:]
                                recent_text = "\n".join(f"对方/我：{m['content'][:80]}" for m in recent) if recent else ""
                                few_shot = build_few_shot_prompt(topic, retriever, recent_text)
                                msgs = [{"role": "system", "content": few_shot}] + st.session_state.messages
                                reply, usage = call_api(msgs, key, st.session_state.model, st.session_state.temp)
                                st.session_state.messages.append({"role": "assistant", "content": reply})
                                if usage:
                                    cost = (usage.get("prompt_tokens", 0) * 1 +
                                            usage.get("completion_tokens", 0) * 2) / 1_000_000
                                    st.session_state.total_cost += cost
                                # 保存对话
                                save_conversation(u, st.session_state.messages)
                            except Exception as e:
                                st.session_state.messages.append(
                                    {"role": "assistant", "content": f"_(出错了：{str(e)[:80]})_"})
                            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    if st.session_state.card_error:
        st.error(st.session_state.card_error)
        st.session_state.card_error = ""

    # ====== 对话 ======
    for msg in st.session_state.messages:
        avatar = "👤" if msg["role"] == "user" else None
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # ====== 输入 ======
    prompt = st.chat_input("说点什么..." if st.session_state.messages else f"嗨 {u}，想聊什么？")

    if prompt:
        if not key:
            st.error("请先在左侧「API 密钥」中配置 API Key")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("assistant"):
                ph = st.empty()
                ph.markdown('<div class="type-dots"><span></span><span></span><span></span></div>',
                            unsafe_allow_html=True)
                try:
                    recent = st.session_state.messages[-8:]
                    recent_text = "\n".join(f"对方/我：{m['content'][:80]}" for m in recent) if recent else ""
                    few_shot = build_few_shot_prompt(prompt, retriever, recent_text)
                    msgs = [{"role": "system", "content": few_shot}] + st.session_state.messages
                    reply, usage = call_api(msgs, key, st.session_state.model, st.session_state.temp)
                    ph.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    if usage:
                        cost = (usage.get("prompt_tokens", 0) * 1 +
                                usage.get("completion_tokens", 0) * 2) / 1_000_000
                        st.session_state.total_cost += cost
                    # 保存对话
                    save_conversation(u, st.session_state.messages)
                except urllib.error.HTTPError as e:
                    msgs_map = {401: "密钥无效，请检查 API Key",
                                402: "余额不足，请联系管理员充值",
                                429: "请求太频繁，请稍等几秒"}
                    ph.error(msgs_map.get(e.code, f"API 错误（{e.code}）"))
                except Exception as e:
                    ph.error(f"网络异常：{str(e)[:100]}")
            st.rerun()


# ============================================================
chat_page() if st.session_state.logged_in else auth_page()
