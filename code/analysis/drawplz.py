#!/usr/bin/env python3
"""
plot_character_graph.py
────────────────────────
Plot AO3 character co-occurrence graph:
- label = character name
- size ∝ appearance count
- color = community
- prevents overlap (via sfdp or adjustText)

Outputs:
  • character_light.png
"""

import os, json, math, random
import networkx as nx
import matplotlib.pyplot as plt

# Optional extras
try:
    from networkx.drawing.nx_agraph import graphviz_layout
    HAVE_PYGRAPHVIZ = True
except ImportError:
    HAVE_PYGRAPHVIZ = False

try:
    import community as community_louvain
    HAVE_LOUVAIN = True
except ImportError:
    HAVE_LOUVAIN = False

try:
    from adjustText import adjust_text
    HAVE_ADJUSTTEXT = True
except ImportError:
    HAVE_ADJUSTTEXT = False

# ─── Config ────────────────────────────────────────────────────────
GRAPHML_PATH = "../../files/character_light.graphml"
CHAR_COUNT_PATH = "../../files/characters_list.jsonl"
PNG_OUT = "../../files/character_light.png"
MAX_NODES = 3000

# ─── Load appearance counts ────────────────────────────────────────
print("📚 Loading appearance counts…")
appearance = {}
with open(CHAR_COUNT_PATH, encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        appearance[obj["name"]] = obj["count"]

# ─── Load graph ────────────────────────────────────────────────────
print("📚 Loading graph…")
G = nx.read_graphml(GRAPHML_PATH)
print(f"   Loaded {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")

# ─── Optional trimming ─────────────────────────────────────────────
if MAX_NODES and G.number_of_nodes() > MAX_NODES:
    top_nodes = sorted(G.degree, key=lambda x: x[1], reverse=True)[:MAX_NODES]
    G = G.subgraph([n for n, _ in top_nodes]).copy()
    print(f"   Trimmed to top {MAX_NODES} nodes by degree.")

# ─── Community detection ───────────────────────────────────────────
print("🧩 Detecting communities…")
if HAVE_LOUVAIN:
    part = community_louvain.best_partition(G)
else:
    comms = nx.algorithms.community.greedy_modularity_communities(G)
    part = {n: idx for idx, c in enumerate(comms) for n in c}

# Assign pastel colors
palette = {}
random.seed(42)
for cid in set(part.values()):
    palette[cid] = (random.random()*0.6+0.4,
                    random.random()*0.6+0.4,
                    random.random()*0.6+0.4)

node_color = [palette[part[n]] for n in G.nodes()]

# ─── Size by appearance count ──────────────────────────────────────
def size_fn(count): return 50 + math.sqrt(count) * 2
node_size = [size_fn(appearance.get(n, 1)) for n in G.nodes()]

# ─── Layout ────────────────────────────────────────────────────────
print("🎨 Computing layout…")
if HAVE_PYGRAPHVIZ:
    pos = graphviz_layout(G, prog="sfdp")
else:
    print("⚠️  pygraphviz not found → using spring_layout")
    pos = nx.spring_layout(G, k=0.15, iterations=100, seed=42)

# ─── Draw PNG ──────────────────────────────────────────────────────
print(f"🖼️  Saving PNG to {PNG_OUT}")
plt.figure(figsize=(18, 14))
nx.draw_networkx_edges(G, pos, width=0.3, alpha=0.3, edge_color="grey")
nx.draw_networkx_nodes(G, pos,
                       node_color=node_color,
                       node_size=node_size,
                       linewidths=0.2,
                       edgecolors="black")

# Labels
labels = {n: n for n in G.nodes()}
texts = nx.draw_networkx_labels(G, pos, labels, font_size=6)

if HAVE_ADJUSTTEXT:
    print("📐 Adjusting label positions to reduce overlap…")
    adjust_text(texts.values(), arrowprops=dict(arrowstyle="-", color='grey', lw=0.2))

plt.axis("off")
plt.tight_layout()
plt.savefig(PNG_OUT, dpi=300)
plt.close()
print("✅ Done.")
