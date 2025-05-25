from collections import defaultdict, Counter
from extract_utils import iter_jsonl_zst
import json, os

INPUT_FOLDER = "../../ao3_slimmed"
OUTPUT_FILE = "../../files/characters_list.jsonl"

# Count characters per fandom
char_counter = defaultdict(lambda: defaultdict(int))  # char -> fandom -> count

for entry in iter_jsonl_zst(INPUT_FOLDER):
    meta = entry.get("metadata", {})
    chars_raw = meta.get("Characters", "")
    fandom_raw = meta.get("Fandom", "")
    chars = [c.strip() for c in chars_raw.split(",") if c.strip()]
    fandoms = [f.strip() for f in fandom_raw.split(",") if f.strip()]

    for c in chars:
        for f in fandoms:
            char_counter[c][f] += 1

# Save top fandoms (max 2) for each character
with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    for idx, (char, fan_counts) in enumerate(char_counter.items(), 1):
        sorted_fandoms = sorted(fan_counts.items(), key=lambda x: x[1], reverse=True)
        top_fandoms = [sorted_fandoms[0][0]]
        if len(sorted_fandoms) > 1:
            ratio = sorted_fandoms[1][1] / sorted_fandoms[0][1]
            if ratio >= 0.9:
                top_fandoms.append(sorted_fandoms[1][0])
        total_count = sum(fan_counts.values())
        json.dump({"id": idx, "name": char, "fandom": top_fandoms, "count": total_count}, out)
        out.write("\n")

print(f"✅ Saved {len(char_counter)} characters to {OUTPUT_FILE}")
