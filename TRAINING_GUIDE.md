# LoRA 微调指南

用 11,448 条对话训练 Qwen2.5-7B，让模型内化张仕达的语言风格。

## 总览

| 步骤 | 做什么 | 时间 | 费用 |
|------|--------|------|------|
| 1 | AutoDL 租 GPU | 5 分钟 | — |
| 2 | 上传数据 + 安装环境 | 10 分钟 | — |
| 3 | 训练 | 1-2 小时 | ¥10-15 |
| 4 | 导出 + 部署 | 10 分钟 | — |

---

## 第一步：租 GPU

1. 打开 https://www.autodl.com
2. 注册 → 充值 ¥20
3. 租一台镜像：选 `LLaMA-Factory` 镜像 + `A100 40G` 或 `RTX 4090`
4. 创建实例，记下 JupyterLab 地址

---

## 第二步：上传数据

在 AutoDL 的 JupyterLab 中：

1. 把 `data/training/training_data.json` 上传到 `/root/autodl-tmp/`
2. 打开终端，确认文件存在：
   ```bash
   ls -lh /root/autodl-tmp/training_data.json
   ```

---

## 第三步：配置并训练

```bash
# 进入 LLaMA-Factory 目录
cd /root/LLaMA-Factory

# 创建配置文件
cat > /root/autodl-tmp/train_config.yaml << 'EOF'
### 模型
model_name_or_path: Qwen/Qwen2.5-7B-Instruct

### 训练方式
stage: sft
do_train: true
finetuning_type: lora
lora_target: all

### 数据集
dataset: zhangshida_persona
dataset_dir: /root/autodl-tmp
template: qwen
cutoff_len: 1024
max_samples: 10000

### 输出
output_dir: /root/autodl-tmp/lora_output
logging_steps: 10
save_steps: 500

### 训练参数
per_device_train_batch_size: 4
gradient_accumulation_steps: 4
learning_rate: 5.0e-5
num_train_epochs: 3.0
lr_scheduler_type: cosine
warmup_ratio: 0.1
bf16: true
ddp_timeout: 180000000

### 其他
overwrite_output_dir: true
overwrite_cache: true
EOF

# 注册数据集
cat > /root/autodl-tmp/dataset_info.json << 'EOF'
{
  "zhangshida_persona": {
    "file_name": "training_data.json"
  }
}
EOF

# 开始训练
llamafactory-cli train /root/autodl-tmp/train_config.yaml
```

训练大约 1-2 小时，完成后 LoRA 权重在 `/root/autodl-tmp/lora_output/`

---

## 第四步：导出合并模型

```bash
# 导出 LoRA 权重
llamafactory-cli export \
  --model_name_or_path Qwen/Qwen2.5-7B-Instruct \
  --adapter_name_or_path /root/autodl-tmp/lora_output \
  --template qwen \
  --finetuning_type lora \
  --export_dir /root/autodl-tmp/final_model \
  --export_size 2 \
  --export_legacy_format false
```

导出的 `/root/autodl-tmp/final_model/` 下载到本地。

---

## 第五步：部署（推荐硅基流动）

1. 打开 https://siliconflow.cn
2. 上传模型或选择一个已部署的 Qwen 端点
3. 获取 API 地址
4. 在你的 `web_chat.py` 里把 `api.deepseek.com` 换成你的端点地址

---

## 成本预估

| 项目 | 费用 |
|------|------|
| AutoDL A100 2小时 | ¥10-15 |
| 下载模型（70GB） | ¥0（内网免流量） |
| 硅基流动部署 | 免费额度 |
| **总计** | **¥10-15** |

---

## 有问题？

- AutoDL 控制台：https://www.autodl.com/console
- LLaMA-Factory 文档：https://github.com/hiyouga/LLaMA-Factory
