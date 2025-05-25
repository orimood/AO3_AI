#!/usr/bin/env python3
"""
export_gephi_characters.py
──────────────────────────
Convert character_cooccurrence.jsonl into Gephi‑friendly CSV files.

  • character_nodes.csv  (id,label,count)
  • character_edges.csv  (Source,Target,Weight)
"""

import os, json, csv, sys
from collections import defaultdict

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.join("..", "..")
COOC_FILE  = os.path.join(BASE_DIR, "files", "character_cooccurrence.jsonl")
NODES_CSV  = os.path.join(BASE_DIR, "files", "character_nodes.csv")
EDGES_CSV  = os.path.join(BASE_DIR, "files", "character_edges.csv")
MIN_EDGE_W = 5     # skip very weak links (change as you like)

# ─── 1. Gather node counts & edge weights ────────────────────────────────────
print("📚  Loading co‑occurrence data …")
node_count   = {}                 # character → appearance count
edge_weight  = defaultdict(int)   # (u,v) sorted tuple → w

with open(COOC_FILE, encoding="utf-8") as f:
    for line in f:
        obj   = json.loads(line)
        char  = obj["character"]
        coocc = obj["co_occurs_with"]

        node_count[char] = node_count.get(char, 0) + 0  # will fill later

        for tgt, w in coocc.items():
            if w < MIN_EDGE_W:
                continue
            edge = tuple(sorted((char, tgt)))
            edge_weight[edge] += w

# fill missing node counts from characters_list.jsonl if available
CHAR_LIST = os.path.join(BASE_DIR, "files", "characters_list.jsonl")
if os.path.isfile(CHAR_LIST):
    with open(CHAR_LIST, encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            node_count[obj["name"]] = obj["count"]

print(f"✅  {len(node_count):,} nodes, {len(edge_weight):,} edges (w ≥ {MIN_EDGE_W}).")

if not edge_weight:
    sys.exit("⚠️  No edges after filtering – lower MIN_EDGE_W and retry.")

# ─── 2. Write nodes CSV ─────────────────────────────────────────────────────
print("📝  Writing nodes CSV …")
with open(NODES_CSV, "w", newline="", encoding="utf-8") as f_nodes:
    writer = csv.writer(f_nodes)
    writer.writerow(["id", "label", "count"])
    for char, cnt in sorted(node_count.items(), key=lambda x: -x[1]):
        writer.writerow([char, char, cnt])

# ─── 3. Write edges CSV ─────────────────────────────────────────────────────
print("📝  Writing edges CSV …")
with open(EDGES_CSV, "w", newline="", encoding="utf-8") as f_edges:
    writer = csv.writer(f_edges)
    writer.writerow(["Source", "Target", "Weight"])
    for (u, v), w in edge_weight.items():
        writer.writerow([u, v, w])

print("🎉  Done!  Files saved to:")
print(f"      {NODES_CSV}")
print(f"      {EDGES_CSV}")
