import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

print("加载 embedding 模型...")
model = SentenceTransformer("BAAI/bge-small-zh-v1.5", device="cuda")
print("模型加载完成")

print("加载聊天数据...")
with open("data/clean/cleaned_messages.json", "r", encoding="utf-8") as f:
    messages = json.load(f)

texts = [m["content"] for m in messages if len(m["content"]) >= 3]
print(f"共 {len(texts)} 条消息")

print("生成 embedding（批量处理，每批 256 条）...")
embeddings = model.encode(
    texts,
    batch_size=256,
    show_progress_bar=True,
    normalize_embeddings=True,
)

print(f"Embedding 形状: {embeddings.shape}")
print(f"大小: {embeddings.nbytes / 1024 / 1024:.1f} MB")

output_dir = Path("data/embeddings")
output_dir.mkdir(parents=True, exist_ok=True)

np.save(output_dir / "embeddings.npy", embeddings)
with open(output_dir / "texts.json", "w", encoding="utf-8") as f:
    json.dump(texts, f, ensure_ascii=False)

print(f"已保存:")
print(f"  {output_dir / 'embeddings.npy'} ({embeddings.nbytes / 1024 / 1024:.1f} MB)")
print(f"  {output_dir / 'texts.json'}")
print("完成！")
