import json

INPUT_FILE = "sync_results1.json"
OUTPUT_FILE = "sync_errors.json"

def filter_errors(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    errors = [item for item in data if isinstance(item.get("sync_message"), str) and "Error" in item["sync_message"]]
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(errors, f, indent=4)
    print(f"Filtered {len(errors)} error records to {output_file}")

if __name__ == "__main__":
    filter_errors(INPUT_FILE, OUTPUT_FILE)
