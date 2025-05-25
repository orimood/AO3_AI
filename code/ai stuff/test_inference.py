from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch
import os

# === Paths ===
BASE_MODEL = "tiiuae/falcon-rw-1b"
ADAPTER_PATH = os.path.join("../..", "fanfic_model")

# === Load tokenizer and base model ===
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype=torch.float32)

# === Load LoRA adapter ===
model = PeftModel.from_pretrained(model, ADAPTER_PATH)

# === Set pad token if missing ===
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# === Sample prompt ===
prompt = (
    "Fandom: Harry Potter - J. K. Rowling\n"
    "Characters: Harry Potter\n"
    "Tags: Angst, Oral Sex, Anal Sex, Slave\n"
    "Rating: Explicit\n"
    "Relationship: Harry Potter\n"
    "Warning: Graphic Depictions of Violence\n"
    "Language: English\n\n"
    "Write a fanfiction scene:"
)

# === Tokenize with attention mask ===
inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
input_ids = inputs["input_ids"]
attention_mask = inputs["attention_mask"]

# === Generate output ===
model.eval()
with torch.no_grad():
    output_ids = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        max_new_tokens=600,
        temperature=0.9,
        top_p=0.95,
        do_sample=True,
        eos_token_id=tokenizer.eos_token_id
    )

# === Decode and print ===
output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
print("\n📝 Generated Fanfic:\n")
print(output_text)