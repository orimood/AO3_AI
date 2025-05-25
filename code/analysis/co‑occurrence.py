#!/usr/bin/env python3
"""
build_character_cooccurrence.py
───────────────────────────────
For every character that appears in > MIN_COUNT works, list every other
character they appear with in the same work and how many works contain the pair.

INPUT  :  ../../ao3_filtered/*.jsonl.zst
COUNTS :  ../../files/characters_list.jsonl
OUTPUT :  ../../files/character_cooccurrence.jsonl
"""

import os, json, zstandard as zstd
from collections import defaultdict

# ─── Config ──────────────────────────────────────────────────────────────────
BASE        = os.path.join("..", "..")                      # repo root
CHAR_LIST   = os.path.join(BASE, "files", "characters_list.jsonl")
INPUT_DIR   = os.path.join(BASE, "ao3_filtered")
OUTPUT_FILE = os.path.join(BASE, "files", "character_cooccurrence.jsonl")
MIN_COUNT   = 20            # “source” character must appear in > 20 works

# ─── 1. Load frequent characters from characters_list.jsonl ──────────────────
print("📚 Loading characters_list.jsonl …")
popular_chars = set()

with open(CHAR_LIST, encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        if obj.get("count", 0) > MIN_COUNT:
            popular_chars.add(obj["name"])

print(f"✅  {len(popular_chars):,} characters have > {MIN_COUNT} works.")

# ─── 2. Helper: iterate through *.jsonl.zst works ────────────────────────────
def iter_jsonl_zst(folder):
    for fname in sorted(os.listdir(folder)):
        if not fname.endswith(".jsonl.zst"):
            continue
        with open(os.path.join(folder, fname), "rb") as fh:
            reader = zstd.ZstdDecompressor().stream_reader(fh)
            buf = b""
            while True:
                chunk = reader.read(65536)
                if not chunk:
                    break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    if not line.strip():
                        continue
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        continue

# ─── 3. Build co‑occurrence counts ───────────────────────────────────────────
print("🔁  Building co‑occurrence matrix …")
cooc = defaultdict(lambda: defaultdict(int))    # char → neighbour → count

for work in iter_jsonl_zst(INPUT_DIR):
    char_raw = work.get("metadata", {}).get("Characters", "")
    chars = [c.strip() for c in char_raw.split(",") if c.strip()]
    # skip single‑character works
    if len(chars) < 2:
        continue

    for c1 in chars:
        if c1 not in popular_chars:
            continue          # only count from “source” popular characters
        for c2 in chars:
            if c2 == c1:
                continue
            cooc[c1][c2] += 1

# ─── 4. Write output ─────────────────────────────────────────────────────────
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as fout:
    for char in sorted(popular_chars):
        json.dump({
            "character":      char,
            "co_occurs_with": dict(cooc[char])   # may be empty
        }, fout)
        fout.write("\n")

print(f"📦  Saved co‑occurrence data → {OUTPUT_FILE}")
