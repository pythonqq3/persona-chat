from llamafactory.train.tuner import export_model
from llamafactory.hparams import get_infer_args
import yaml

config = yaml.safe_load(open('/root/autodl-tmp/train.yaml'))

args = {
    "model_name_or_path": config["model_name_or_path"],
    "adapter_name_or_path": "/root/autodl-tmp/lora_full",
    "template": config.get("template", "qwen"),
    "finetuning_type": "lora",
    "export_dir": "/root/autodl-tmp/merged_model",
    "export_size": 2,
    "export_legacy_format": False,
}

export_model(args)
print("\n合并完成！模型在 /root/autodl-tmp/merged_model/")
