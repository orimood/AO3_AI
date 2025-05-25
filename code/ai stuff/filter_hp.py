import json
import os

INPUT_PATH = os.path.join("../..", "files", "ao3_9900001-10000000.jsonl")
OUTPUT_PATH = os.path.join("../..", "files", "hp_mature_explicit.jsonl")

ALLOWED_FANDOMS = {"Harry Potter - Fandom", "Harry Potter - J. K. Rowling"}
ALLOWED_RATINGS = {"Mature", "Explicit"}

def filter_hp_entries(input_file, output_file):
    count = 0

    with open(input_file, "r", encoding="utf-8") as f_in, open(output_file, "w", encoding="utf-8") as f_out:
        for line in f_in:
            try:
                entry = json.loads(line)
                meta = entry.get("metadata", {})
                fandom_raw = meta.get("Fandom", "")
                rating = meta.get("Rating", "")

                # Split and check all fandoms
                fandoms = [f.strip() for f in fandom_raw.split(",")]
                if any(f in ALLOWED_FANDOMS for f in fandoms) and rating in ALLOWED_RATINGS:
                    f_out.write(json.dumps(entry) + "\n")
                    count += 1
            except json.JSONDecodeError:
                continue  # Skip bad lines

    print(f"✅ Saved {count} filtered Harry Potter fanfics to {output_file}")

if __name__ == "__main__":
    filter_hp_entries(INPUT_PATH, OUTPUT_PATH)
