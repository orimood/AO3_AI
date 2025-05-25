import json
from collections import defaultdict, Counter
import os

CHAR_FILE = os.path.join("..", "..", "files", "characters_list.jsonl")
FANDOM_COUNT_FILE = os.path.join("..", "..", "files", "fandom_counts.jsonl")
TOP_N = 10

def load_top_fandoms(path, top_n):
    fandom_counter = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                fandom_counter.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    sorted_top = sorted(fandom_counter, key=lambda x: x["count"], reverse=True)
    return set(fc["fandom"] for fc in sorted_top[:top_n])

def load_filtered_characters(path, top_fandoms):
    characters = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                char = json.loads(line)
                if any(f in top_fandoms for f in char.get("fandom", [])):
                    characters.append(char)
            except json.JSONDecodeError:
                continue
    return characters

def top_characters_global(characters, n=20):
    sorted_chars = sorted(characters, key=lambda x: x["count"], reverse=True)
    print(f"\n📈 Top {n} Characters (Top Fandoms Only):")
    for i, char in enumerate(sorted_chars[:n], 1):
        print(f"{i:>2}. {char['name']} ({char['count']} works)")

def top_characters_per_fandom(characters, top_n):
    fandom_map = defaultdict(list)
    for char in characters:
        for fandom in char.get("fandom", []):
            fandom_map[fandom].append(char)

    print(f"\n🏆 Top {top_n} Characters Per Top Fandom:")
    for fandom, chars in fandom_map.items():
        top = sorted(chars, key=lambda x: x["count"], reverse=True)[:top_n]
        print(f"\n🔹 {fandom} ({len(chars)} characters):")
        for i, char in enumerate(top, 1):
            print(f"   {i:>2}. {char['name']} ({char['count']} works)")

def cross_fandom_characters(characters):
    print("\n🧭 Cross-Fandom Characters (Top 10 Only):")
    for char in characters:
        if len(char.get("fandom", [])) > 1:
            print(f"- {char['name']} → {char['fandom']}")

if __name__ == "__main__":
    top_fandoms = load_top_fandoms(FANDOM_COUNT_FILE, TOP_N)
    print(f"✅ Loaded Top {TOP_N} Fandoms:\n", *top_fandoms, sep="\n- ")

    characters = load_filtered_characters(CHAR_FILE, top_fandoms)
    print(f"\n📦 Filtered {len(characters)} characters from top fandoms.\n")

    top_characters_global(characters)
    top_characters_per_fandom(characters, top_n=10)
    cross_fandom_characters(characters)
