#!/usr/bin/env python3
"""
make_light_character_graph.py
─────────────────────────────
Read files/character_cooccurrence.jsonl and produce a smaller sub‑graph
for Gephi by filtering on character frequency, edge weight, and capping
node degree.

Outputs:
  • files/character_light.graphml
  • files/character_light_nodes.csv
  • files/character_light_edges.csv
"""

import os, json, csv
from collections import defaultdict
import networkx as nx

# ─── Tunable parameters ─────────────────────────────────────────────────────
MIN_APPEARANCES = 100   # keep characters that appear ≥ this many works
MIN_EDGE_W      = 10    # keep edges with weight ≥ this many works
DEGREE_CAP      = 20    # keep at most this many strongest edges per node
# ────────────────────────────────────────────────────────────────────────────

BASE_DIR     = os.path.join("..", "..")
COOC_FILE    = os.path.join(BASE_DIR, "files", "character_cooccurrence.jsonl")
CHAR_LIST    = os.path.join(BASE_DIR, "files", "characters_list.jsonl")  # holds counts
GRAPHML_OUT  = os.path.join(BASE_DIR, "files", "character_light.graphml")
NODES_CSV    = os.path.join(BASE_DIR, "files", "character_light_nodes.csv")
EDGES_CSV    = os.path.join(BASE_DIR, "files", "character_light_edges.csv")

# ─── 1. Load character appearance counts ────────────────────────────────────
print("📚  Reading character counts …")
appears = {}   # char → works count
with open(CHAR_LIST, encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        appears[obj["name"]] = obj["count"]

# keep characters above threshold
popular = {c for c, n in appears.items() if n >= MIN_APPEARANCES}
print(f"✅  {len(popular):,} characters appear ≥ {MIN_APPEARANCES} times.")

# ─── 2. Build filtered graph ────────────────────────────────────────────────
print("🔗  Building filtered graph …")
G = nx.Graph()

with open(COOC_FILE, encoding="utf-8") as f:
    for line in f:
        obj  = json.loads(line)
        src  = obj["character"]
        if src not in popular:
            continue
        for tgt, w in obj["co_occurs_with"].items():
            if w < MIN_EDGE_W or tgt not in popular:
                continue
            G.add_edge(src, tgt, weight=w)

print(f"   After weight & popularity filters: "
      f"{G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges.")

# ─── 3. Cap each node’s degree to top‑k edges ───────────────────────────────
def cap_degree(graph: nx.Graph, k: int) -> nx.Graph:
    keep = set()
    for node in graph.nodes():
        incident = sorted(
            ((node, nbr, d["weight"]) for nbr, d in graph[node].items()),
            key=lambda x: x[2], reverse=True
        )
        for u, v, _ in incident[:k]:
            keep.add(tuple(sorted((u, v))))
    H = nx.Graph()
    for u, v in keep:
        H.add_edge(u, v, weight=graph[u][v]["weight"])
    return H

G = cap_degree(G, DEGREE_CAP)
print(f"✂️  After capping degree ({DEGREE_CAP}): "
      f"{G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges.")

if not G:
    raise SystemExit("Graph is empty — relax thresholds and try again.")

# ─── 4. Save GraphML ────────────────────────────────────────────────────────
nx.write_graphml(G, GRAPHML_OUT)
print(f"🗂️  Saved GraphML → {GRAPHML_OUT}")

# ─── 5. Also save Gephi‑friendly CSVs (optional) ────────────────────────────
with open(NODES_CSV, "w", newline="", encoding="utf-8") as f_nodes:
    writer = csv.writer(f_nodes)
    writer.writerow(["id", "label", "count"])
    for n in G.nodes():
        writer.writerow([n, n, appears.get(n, "")])

with open(EDGES_CSV, "w", newline="", encoding="utf-8") as f_edges:
    writer = csv.writer(f_edges)
    writer.writerow(["Source", "Target", "Weight"])
    for u, v, d in G.edges(data=True):
        writer.writerow([u, v, d["weight"]])

print(f"📄  CSVs saved → {NODES_CSV}, {EDGES_CSV}")
print("Done!")
