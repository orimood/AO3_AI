import json
import os

# === File paths ===
# INPUT_PATH = os.path.join("..", "files", "ao3_9900001-10000000.jsonl")
# OUTPUT_PATH = os.path.join("..", "files", "train_data.jsonl")
INPUT_PATH = os.path.join("../..", "files", "hp_mature_explicit.jsonl")
OUTPUT_PATH = os.path.join("../..", "files", "hp_train_data.jsonl")


def convert_to_prompt_response(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f_in, open(output_file, "w", encoding="utf-8") as f_out:
        printed = False  # Print only one sample

        for line in f_in:
            entry = json.loads(line)
            meta = entry.get("metadata", {})

            # === Extract relevant metadata fields ===
            fandom = meta.get("Fandom", "Unknown")
            characters = meta.get("Characters", "Unknown")
            tags = meta.get("Additional Tags", "")
            rating = meta.get("Rating", "Unknown")
            relationship = meta.get("Relationship", "None")
            warning = meta.get("Archive Warning", "")
            language = meta.get("Language", "English")

            # === Build the prompt ===
            prompt = (
                f"Fandom: {fandom}\n"
                f"Characters: {characters}\n"
                f"Tags: {tags}\n"
                f"Rating: {rating}\n"
                f"Relationship: {relationship}\n"
                f"Warning: {warning}\n"
                f"Language: {language}\n\n"
                "Write a fanfiction scene:"
            )

            response = entry.get("text", "").strip()

            if response:
                formatted = {
                    "prompt": prompt,
                    "response": response
                }

                # ✅ Print first example for verification
                if not printed:
                    print("🔍 Sample Prompt-Response Pair:")
                    print(json.dumps(formatted, indent=2))
                    print("-" * 80)
                    printed = True

                f_out.write(json.dumps(formatted) + "\n")

    print(f"✅ Done. Converted dataset saved to: {output_file}")

if __name__ == "__main__":
    convert_to_prompt_response(INPUT_PATH, OUTPUT_PATH)
