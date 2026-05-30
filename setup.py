import yaml
config = {'model_name_or_path': '/root/autodl-tmp/models/hub/Qwen/Qwen2.5-7B-Instruct', 'stage': 'sft', 'do_train': True, 'finetuning_type': 'lora', 'lora_target': 'all', 'dataset': 'zhangshida_persona', 'dataset_dir': '/root/autodl-tmp', 'template': 'qwen', 'cutoff_len': 1024, 'max_samples': 2000, 'output_dir': '/root/autodl-tmp/lora_test', 'per_device_train_batch_size': 2, 'gradient_accumulation_steps': 8, 'learning_rate': 5e-5, 'num_train_epochs': 3, 'lr_scheduler_type': 'cosine', 'warmup_ratio': 0.1, 'bf16': True, 'logging_steps': 10, 'save_steps': 500, 'overwrite_output_dir': True, 'overwrite_cache': True}
yaml.dump(config, open('/root/autodl-tmp/train.yaml', 'w'))
print('OK')
