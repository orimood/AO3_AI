import json

file_path = "/files/ao3_9900001-10000000.jsonl"

with open(file_path, 'r', encoding='utf-8') as file:
    for i in range(100):
        line = file.readline()
        if not line:
            break  # end of file
        try:
            json_obj = json.loads(line)
            print(json.dumps(json_obj, indent=2))  # pretty-print each object
        except json.JSONDecodeError as e:
            print(f"Error parsing line {i+1}: {e}")
