from collections import defaultdict
from extract_utils import iter_jsonl_zst
import json, os

INPUT_FOLDER = "../../ao3_slimmed"
OUTPUT_FILE = "../../files/relationships_list.jsonl"

rel_counter = defaultdict(lambda: defaultdict(int))  # rel -> fandom -> count

for entry in iter_jsonl_zst(INPUT_FOLDER):
    meta = entry.get("metadata", {})
    rel_raw = meta.get("Relationship", "")
    fandom_raw = meta.get("Fandom", "")
    rels = [r.strip() for r in rel_raw.split(",") if r.strip()]
    fandoms = [f.strip() for f in fandom_raw.split(",") if f.strip()]

    for r in rels:
        for f in fandoms:
            rel_counter[r][f] += 1

# Save top fandoms (max 2) for each relationship
with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    for idx, (rel, fan_counts) in enumerate(rel_counter.items(), 1):
        sorted_fandoms = sorted(fan_counts.items(), key=lambda x: x[1], reverse=True)
        top_fandoms = [sorted_fandoms[0][0]]
        if len(sorted_fandoms) > 1:
            ratio = sorted_fandoms[1][1] / sorted_fandoms[0][1]
            if ratio >= 0.9:
                top_fandoms.append(sorted_fandoms[1][0])
        total_count = sum(fan_counts.values())
        json.dump({"id": idx, "name": rel, "fandom": top_fandoms, "count": total_count}, out)
        out.write("\n")

print(f"✅ Saved {len(rel_counter)} relationships to {OUTPUT_FILE}")
