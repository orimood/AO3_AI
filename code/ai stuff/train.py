from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from peft import get_peft_model, LoraConfig, TaskType
import torch
import os

# === Config === #
MODEL_ID = "tiiuae/falcon-rw-1b"  # Smaller, Mac-friendly model
# DATA_PATH = os.path.join("..", "files", "train_data.jsonl")
DATA_PATH = os.path.join("../..", "files", "hp_train_data.jsonl")


# === Load tokenizer & model === #
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

# Ensure we have a pad token
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float32,
    device_map="auto"
)

# === LoRA config === #
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none"
)
model = get_peft_model(model, lora_config)

# === Load dataset === #
dataset = load_dataset("json", data_files={"train": DATA_PATH})["train"]

def tokenize(example):
    full_text = f"{example['prompt']}\n{example['response']}"
    tokens = tokenizer(full_text, truncation=True, padding="max_length", max_length=512)
    tokens["labels"] = tokens["input_ids"].copy()
    return tokens


tokenized_dataset = dataset.map(tokenize, remove_columns=["prompt", "response"])

# === Training setup === #
training_args = TrainingArguments(
    output_dir="../../fanfic_model",
    per_device_train_batch_size=1,
    num_train_epochs=1,
    logging_steps=5,
    save_steps=50,
    save_total_limit=2,
    logging_dir="../logs",
)

trainer = Trainer(
    model=model,
    tokenizer=tokenizer,
    args=training_args,
    train_dataset=tokenized_dataset,
)

trainer.train()
# === Save LoRA adapter + tokenizer correctly ===
model.save_pretrained("../fanfic_model")
tokenizer.save_pretrained("../fanfic_model")