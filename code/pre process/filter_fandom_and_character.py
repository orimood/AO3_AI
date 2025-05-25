import os
import zstandard as zstd
import json

INPUT_DIR = "../../ao3_slimmed"
OUTPUT_DIR = "../../ao3_filtered"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def should_exclude(entry):
    meta = entry.get("metadata", {})
    # Exclude if "Original Work" is one of the fandoms
    fandoms = [f.strip() for f in meta.get("Fandom", "").split(",")]
    if "Original Work" in fandoms:
        return True
    # Exclude if "Reader" is one of the characters
    characters = [c.strip() for c in meta.get("Characters", "").split(",")]
    if "Reader" in characters:
        return True
    return False

def filter_and_save(input_path, output_path):
    with open(input_path, "rb") as fin, open(output_path, "wb") as fout:
        dctx = zstd.ZstdDecompressor()
        reader = dctx.stream_reader(fin)

        cctx = zstd.ZstdCompressor(level=3)
        writer = cctx.stream_writer(fout)

        buffer = b""
        while True:
            chunk = reader.read(65536)
            if not chunk:
                break
            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                try:
                    obj = json.loads(line.decode("utf-8"))
                    if should_exclude(obj):
                        continue
                    json_line = json.dumps(obj, ensure_ascii=False).encode("utf-8") + b"\n"
                    writer.write(json_line)
                except json.JSONDecodeError:
                    continue

        writer.flush(zstd.FLUSH_FRAME)

# === Process all files ===
for filename in sorted(os.listdir(INPUT_DIR)):
    if filename.endswith(".jsonl.zst"):
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        print(f"🚫 Filtering {filename}...")
        filter_and_save(input_path, output_path)

print(f"✅ Done. Filtered files saved to: {OUTPUT_DIR}")
