import yaml
c = yaml.safe_load(open('/root/autodl-tmp/train.yaml'))
# 删除 max_samples（用全部数据）
if 'max_samples' in c:
    del c['max_samples']
# 5 轮训练
c['num_train_epochs'] = 5
# 新输出目录
c['output_dir'] = '/root/autodl-tmp/lora_full'
yaml.dump(c, open('/root/autodl-tmp/train.yaml', 'w'))
print('OK - 全量训练 5 轮，输出到 lora_full')
