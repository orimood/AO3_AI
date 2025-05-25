import os
import json
from collections import defaultdict, Counter
import zstandard as zstd

INPUT_DIR = "../../ao3_filtered"
OUTPUT_FILE = "../../files/relationship_cooccurrence.jsonl"
MIN_COUNT = 20

def iter_jsonl_zst(folder_path):
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".jsonl.zst"):
            path = os.path.join(folder_path, filename)
            with open(path, "rb") as compressed:
                dctx = zstd.ZstdDecompressor()
                with dctx.stream_reader(compressed) as reader:
                    buffer = b""
                    while True:
                        chunk = reader.read(65536)
                        if not chunk:
                            break
                        buffer += chunk
                        while b"\n" in buffer:
                            line, buffer = buffer.split(b"\n", 1)
                            try:
                                yield json.loads(line.decode("utf-8"))
                            except json.JSONDecodeError:
                                continue

# Step 1: Count all relationships
rel_counter = Counter()

print("🔍 First pass: Counting relationship frequencies...")
for entry in iter_jsonl_zst(INPUT_DIR):
    rels_raw = entry.get("metadata", {}).get("Relationship", "")
    rels = [r.strip() for r in rels_raw.split(",") if r.strip()]
    rel_counter.update(rels)

# Keep only relationships with > MIN_COUNT occurrences
valid_rels = {rel for rel, count in rel_counter.items() if count > MIN_COUNT}
print(f"✅ Found {len(valid_rels)} relationships with >{MIN_COUNT} occurrences.")

# Step 2: Build co-occurrence counts
co_occurrence = defaultdict(Counter)

print("🔁 Second pass: Building co-occurrence matrix...")
for entry in iter_jsonl_zst(INPUT_DIR):
    rels_raw = entry.get("metadata", {}).get("Relationship", "")
    rels = [r.strip() for r in rels_raw.split(",") if r.strip()]
    rels = [r for r in rels if r in valid_rels]

    for i, r1 in enumerate(rels):
        for j, r2 in enumerate(rels):
            if i != j:
                co_occurrence[r1][r2] += 1

# Step 3: Save to file
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
    for rel, neighbors in co_occurrence.items():
        json.dump({
            "relationship": rel,
            "co_occurs_with": dict(neighbors)
        }, f_out)
        f_out.write("\n")

print(f"📁 Done. Saved co-occurrence data to {OUTPUT_FILE}")
