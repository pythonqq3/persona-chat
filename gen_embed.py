import json, numpy as np
from modelscope import snapshot_download

# 先用 ModelScope 下载
print("从 ModelScope 下载 embedding 模型...")
model_dir = snapshot_download('BAAI/bge-small-zh-v1.5', cache_dir='/root/autodl-tmp/models')
print(f"模型路径: {model_dir}")

from sentence_transformers import SentenceTransformer
model = SentenceTransformer(model_dir, device='cuda')

with open('cleaned_messages.json', 'r') as f:
    messages = json.load(f)
texts = [m['content'] for m in messages if len(m['content']) >= 3]
print(f'共 {len(texts)} 条')

embeddings = model.encode(texts, batch_size=256, show_progress_bar=True, normalize_embeddings=True)
np.save('embeddings.npy', embeddings)
with open('texts_for_embed.json', 'w') as f:
    json.dump(texts, f, ensure_ascii=False)
print(f'完成! embeddings: {embeddings.shape}, {embeddings.nbytes/1024/1024:.1f}MB')
