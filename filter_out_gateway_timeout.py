import json

INPUT_FILE = "sync_errors.json"
OUTPUT_FILE = "sync_errors_filtered.json"

FILTER_STRING = "HTTP Request Error: 504 Server Error: Gateway Time-out for url: https://ebplanner-api.ebpearls.com/api"

def filter_out_gateway_timeout(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    filtered = [item for item in data if item.get("sync_message") == FILTER_STRING]
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=4)
    print(f"Filtered out {len(data) - len(filtered)} records. Remaining: {len(filtered)}. Saved to {output_file}")

if __name__ == "__main__":
    filter_out_gateway_timeout(INPUT_FILE, OUTPUT_FILE)
