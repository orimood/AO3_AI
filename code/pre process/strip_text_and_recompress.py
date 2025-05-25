import os
import zstandard as zstd
import json

INPUT_DIR = "../../ao3"
OUTPUT_DIR = "../../ao3_slimmed"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def strip_text_and_save(input_path, output_path):
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
                    if "text" in obj:
                        del obj["text"]
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
        print(f"🧹 Stripping text from {filename}...")
        strip_text_and_save(input_path, output_path)

print(f"✅ Done. Cleaned files saved to: {OUTPUT_DIR}")
