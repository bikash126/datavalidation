import json


def join_projects_with_sync_results(json_file1, json_file2, output_file="joined_projects.json"):
    """
    Joins two JSON files (project list and sync results) on projectId/id and writes the merged result.
    Args:
        json_file1 (str): Path to the main projects JSON file (expects 'id' key).
        json_file2 (str): Path to the sync results JSON file (expects 'projectId' key).
        output_file (str): Path to write the joined output JSON.
    Returns:
        list: The joined list of project dicts.
    """
    with open(json_file1, "r") as f:
        combined_projects = json.load(f)
    with open(json_file2, "r") as f:
        sync_results = json.load(f)
    sync_lookup = {item["projectId"]: item for item in sync_results if "projectId" in item}
    joined = []
    for project in combined_projects:
        pid = project.get("id")
        if pid in sync_lookup:
            sync_data = {k: v for k, v in sync_lookup[pid].items() if k != "projectId"}
            merged = {**project, **sync_data}
            joined.append(merged)
        else:
            joined.append(project)
    with open(output_file, "w") as f:
        json.dump(joined, f, indent=4)
    print(f"Wrote {output_file} with merged data.")
    return joined

# Example usage:
if __name__ == "__main__":
    join_projects_with_sync_results("sync_results2.json", "engineering_emails.json")
import json

