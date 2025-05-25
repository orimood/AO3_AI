import os
import zstandard as zstd
import json

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


def get_top_fandoms(fandoms_file, threshold_ratio=0.9):
    with open(fandoms_file, "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f]

    # Sort by count descending
    lines.sort(key=lambda x: x["count"], reverse=True)

    top_fandoms = [lines[0]["fandom"]]
    if len(lines) > 1 and lines[1]["count"] >= lines[0]["count"] * threshold_ratio:
        top_fandoms.append(lines[1]["fandom"])
    return set(top_fandoms)
