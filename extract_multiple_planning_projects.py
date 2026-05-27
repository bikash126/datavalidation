import json

INPUT_FILE = "combined_projects.json"
OUTPUT_FILE = "projects_with_multiple_planning.json"

def extract_projects_with_multiple_planning(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    result = [project for project in data if isinstance(project.get("planning"), list) and len(project["planning"]) > 1]
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)
    print(f"Extracted {len(result)} projects with multiple planning entries to {output_file}")

if __name__ == "__main__":
    extract_projects_with_multiple_planning(INPUT_FILE, OUTPUT_FILE)
