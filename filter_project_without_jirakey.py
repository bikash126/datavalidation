import json

# Load JSON file
with open("combined_projects1.json", "r") as f:
    data = json.load(f)

# Filter items
filtered_data = [
    item for item in data
    if item.get("jiraProjectKey") is not None
]

# Save filtered JSON
with open("combined_projects1_withJira.json", "w") as f:
    json.dump(filtered_data, f, indent=4)

print(f"Filtered {len(data) - len(filtered_data)} items")