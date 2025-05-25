import os
import zstandard as zstd
import json
from collections import Counter

INPUT_DIR = "../../ao3_slimmed"
OUTPUT_FILE = "../../files/fandom_counts.jsonl"

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

def count_fandoms():
    counter = Counter()
    for entry in iter_jsonl_zst(INPUT_DIR):
        fandom_raw = entry.get("metadata", {}).get("Fandom", "")
        fandoms = [f.strip() for f in fandom_raw.split(",") if f.strip()]
        for fandom in fandoms:
            counter[fandom] += 1
    return counter

if __name__ == "__main__":
    print("🔍 Counting fandoms in ao3_slimmed...")
    fandom_counts = count_fandoms()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        for idx, (fandom, count) in enumerate(fandom_counts.items(), 1):
            json.dump({"id": idx, "fandom": fandom, "count": count}, f_out)
            f_out.write("\n")

    print(f"✅ Done. Saved {len(fandom_counts)} fandoms to {OUTPUT_FILE}")
