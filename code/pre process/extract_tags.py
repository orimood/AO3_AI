from collections import Counter
from extract_utils import iter_jsonl_zst  # assuming you put the shared loader above in extract_utils.py
import json, os

INPUT_FOLDER = "../../ao3_slimmed"
OUTPUT_FILE = "../../files/tags_list.jsonl"

tag_counter = Counter()

for entry in iter_jsonl_zst(INPUT_FOLDER):
    tags_raw = entry.get("metadata", {}).get("Additional Tags", "")
    tags = [tag.strip() for tag in tags_raw.split(",") if tag.strip()]
    tag_counter.update(tags)

with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    for idx, (tag, count) in enumerate(tag_counter.items(), 1):
        json.dump({"id": idx, "name": tag, "count": count}, out)
        out.write("\n")

print(f"✅ Saved {len(tag_counter)} tags to {OUTPUT_FILE}")
