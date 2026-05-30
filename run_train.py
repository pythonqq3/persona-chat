import yaml
from llamafactory.train.tuner import run_exp

config = yaml.safe_load(open('/root/autodl-tmp/train.yaml'))
run_exp(config)
print('训练完成！')
