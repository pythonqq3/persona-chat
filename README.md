# 微信数字分身（WeChat Persona）

把一个人的微信聊天数据「蒸馏」成 AI 人格技能，让大模型模拟那个人说话。

## 🎯 效果演示

```
你：今天下班吃啥？
🤖 张三：随便 能吃就行 别太远😂
你：火锅？
🤖 张三：可以可以 哪家啊 不好吃我可不认账
```

## 📂 项目结构

```
wechat-persona/
├── data/
│   ├── raw/          # ← 把导出的微信数据放这里
│   └── clean/        # 清洗后的数据（自动生成）
├── scripts/
│   ├── clean_chat.py        # ① 数据清洗脚本
│   ├── persona_analyzer.py  # ② 人格分析脚本
│   └── chat_simulator.py    # ④ 对话模拟脚本
└── output/
    ├── persona_skill_template.md   # ③ SKILL.md 模板
    └── persona-xxx/                 # 最终生成的人格技能
        └── SKILL.md
```

## 🚀 完整流程（四步走）

### 第一步：导出微信数据

使用 [WeChatMsg（留痕）](https://github.com/LC044/WeChatMsg) 导出微信聊天记录：

1. 下载并安装 WeChatMsg
2. 登录后选择你要导出的人和聊天窗口
3. 导出格式选择 **CSV**
4. 将导出的 CSV 文件放入 `data/raw/` 目录

> ⚠️ 所有数据处理都在本地进行，确保隐私安全

### 第二步：清洗数据

```bash
cd wechat-persona

# 假设你导出的文件叫 聊天记录.csv，目标人物叫"张三"
python scripts/clean_chat.py \
    --input data/raw/聊天记录.csv \
    --person "张三" \
    --output data/clean/
```

清洗完会输出统计信息：
```
✅ 清洗完成！统计信息：
   📊 有效消息数：128,500 条
   📝 总字数：1,234,000 字
   📏 平均每条：9.6 字
   📅 时间范围：2024-01-15 ~ 2026-05-28
```

### 第三步：分析人格

**方式一：本地统计（推荐先跑这个）**
```bash
python scripts/persona_analyzer.py \
    --input data/clean/cleaned_messages.json \
    --local
```
会在 `output/` 下生成：
- `persona_analysis.json` — 完整统计数据
- `persona_report.txt` — 人类可读分析报告

**方式二：AI 深度分析（效果更好，需要 API key）**
```bash
export DEEPSEEK_API_KEY="sk-xxx"  # 先设置 API key
python scripts/persona_analyzer.py \
    --input data/clean/cleaned_messages.json \
    --api deepseek
```

### 第四步：生成并加载 SKILL.md

拿到分析报告后，用 `output/persona_skill_template.md` 作为模板，填入分析结果：

1. 复制模板：
   ```bash
   mkdir output/persona-zhangsan
   copy output\persona_skill_template.md output\persona-zhangsan\SKILL.md
   ```

2. 打开 `SKILL.md`，把 `{{...}}` 占位符替换为分析报告中提取出的真实数据

3. 开始对话：
   ```bash
   export DEEPSEEK_API_KEY="sk-xxx"
   python scripts/chat_simulator.py \
       --skill output/persona-zhangsan/SKILL.md \
       --api deepseek
   ```

## 💰 成本估算

| API 服务 | 价格（输入） | 价格（输出） | 每次对话约 |
|---------|------------|------------|----------|
| DeepSeek | ¥1/百万token | ¥2/百万token | ¥0.001 |
| Claude Sonnet | $3/百万token | $15/百万token | $0.01 |

> 推荐用 DeepSeek，国内延迟低、便宜，模拟效果也足够好

## 🔧 依赖

纯 Python 标准库，无需额外安装任何包。

如果想让分词更准，可以装 jieba：
```bash
pip install jieba
```

## ⚠️ 隐私与合规

- 所有数据在本地处理，不上传
- 如果你使用 `--api` 模式，聊天片段会发送到对应 API 服务商
- 本工具仅供**个人学习与娱乐**，请勿用于冒充他人或违法用途
- AI 无法完全复刻真人，请勿将模仿内容当作真实意见

## 📖 相关项目

- [WeChatMsg](https://github.com/LC044/WeChatMsg) — 微信聊天记录导出工具
- [emilkowalski/skill](https://github.com/emilkowalski/skill) — Agent Skill 参考项目
- [Agent Skills 规范](https://agentskills.io) — SKILL.md 官方规范
