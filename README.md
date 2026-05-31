# 张仕达的数字分身 👤

> 把 24,000 条微信聊天记录「蒸馏」成 AI 人格，让大模型完美模仿一个 19 岁大学生说话。

**在线体验**：`https://chat.061230zsd.xyz`

---

## 🎯 效果

```
你：今天好累
🤖：咋了 最近有什么事吗

你：写首诗
🤖：秋风送爽至

你：你觉得自己写的怎么样
🤖：不怎么样 那时候韵律都没搞对 不过当时在网上发了之后有好多陌生人给我投票 还有一个人送了三十块钱

你：你喜欢什么样的女生
🤖：说不好 感觉性格合得来就行 太作的受不了
```

---

## 🧠 人格特征

- **语气**：极短句（平均 9.7 字）、不打句号、口语化
- **口头禅**：奥奥、六六六、不知道、差不多、确实
- **爱好**：羽毛球、跑步(5km PB 18:19)、王者荣耀、写诗词、道家思想
- **性格**：随性慵懒 → 毒舌耍贫嘴 → 有内秀（诗词/编程/道家）→ 情感细腻 → 有原则
- **思维防线**：随和不等于没脑子，该怼就怼

---

## 🔐 多账号模式

| 账号 | 体验 |
|------|------|
| `zsd` | 🪞 自我对话——自嘲、反思、自言自语 |
| `cq` | 💕 喜欢的人——温柔、多问、主动 |
| `user` | 🤝 死党——毒舌、开玩笑、不装 |

---

## 🏗 技术架构

```
24,060 条微信消息 → SKILL.md(412行人格规则) + TF-IDF检索系统
                              ↓
                     DeepSeek API(千亿参数)
                              ↓
                     Streamlit 网页 + GitHub Pages 域名
```

---

## 📂 项目结构

```
wechat-persona/
├── output/persona-me/SKILL.md          ← 人格核心
├── scripts/web_chat.py                 ← 网页主程序
├── scripts/clean_chat.py               ← 数据清洗
├── scripts/persona_analyzer.py         ← 人格分析
├── scripts/prepare_training_data.py    ← 微调数据生成
├── data/                               ← 数据（不公开）
├── docs/                               ← GitHub Pages
├── TRAINING_GUIDE.md                   ← LoRA 训练指南
└── PROJECT_REPORT.md                   ← 完整项目报告
```

---

## 🚀 自己部署

```bash
git clone https://github.com/pythonqq3/persona-chat
cd persona-chat
pip install -r requirements.txt
streamlit run scripts/web_chat.py
```

需在 Streamlit Secrets 中配置：
```toml
DEEPSEEK_API_KEY = "sk-xxx"
authorized_users = "username:password_hash"
admin_users = "admin_username"
```

---

## 📊 项目数据

| 指标 | 数值 |
|------|------|
| 训练数据 | 24,060 条微信消息 |
| 时间跨度 | 2024.08 - 2026.05 |
| 对话窗口 | 6 个 |
| 人格规则 | 412 行 SKILL.md |
| 检索索引 | 21,604 条 |
| 每轮成本 | ~¥0.005 |

---

## 📖 完整报告

详见 [PROJECT_REPORT.md](./PROJECT_REPORT.md)

---

> 📅 2026.05.30 - 05.31 | 🛠 Claude Code + DeepSeek + Streamlit | 🏆 已上线
