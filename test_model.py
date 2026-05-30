from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_path = '/root/autodl-tmp/merged_model'

print("加载模型...")
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.bfloat16, device_map='auto')
print("加载完成！")

questions = [
    "你好，今天干嘛了",
    "你跑步怎么样",
    "我喜欢什么样的女生",
    "你觉得人生的意义是什么",
    "写首诗",
    "我好累",
    "你对道家怎么看",
    "你觉得AI能替代人吗",
]

for q in questions:
    messages = [
        {"role": "system", "content": "你是张仕达，19岁大学生，06年12月30日出生。说话要短，口语化，接地气。不要打句号。爱打羽毛球，会写诗词，对道家有共鸣。"},
        {"role": "user", "content": q},
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=80, temperature=0.7, do_sample=True)
    reply = tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True)
    print(f"\n问: {q}")
    print(f"答: {reply}")

print("\n全部测试完成")
