
import json
import os
import time
import requests
import constants

# 1. Configuration
URL = constants.API_URL
FROM_DATE = "2021-01-01"
INPUT_FILE = "sync_errors_filtered.json"       # Your input file containing the array of projects
OUTPUT_FILE = "sync_results2.json"  # File where sync results will be saved

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": constants.API_TOKEN
}

# 2. GraphQL Payload Framework (Only Sync Mutation)
SPRINT_REPORT_QUERY = """
query GenerateSprintReport($projectId: Int!, $excelSheet: Boolean) {
    generateSprintReportOfProject(projectId: $projectId, excelSheet: $excelSheet)
}
"""

def save_to_json_file(new_record, filename=OUTPUT_FILE):
    """Safely loads, appends, and updates the local JSON output file."""
    file_data = []
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        with open(filename, "r", encoding="utf-8") as file:
            try:
                file_data = json.load(file)
            except json.JSONDecodeError:
                file_data = []
                
    file_data.append(new_record)
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(file_data, file, indent=4)

def run_automation_workflow():
    # Load project configuration inputs
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: Input file '{INPUT_FILE}' not found. Please create it first.")
        return
        
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        target_projects = json.load(file)
        
    print(f"🚀 Found {len(target_projects)} total projects in '{INPUT_FILE}'.")
    print("🎯 Syncing all items...\n")

    for project in target_projects:
        project_id = project["projectId"]
        project_name = project["projectName"]
        
        print(f"--- Syncing: {project_name} (ID: {project_id}) ---")
        
        # Structure the payload for the sync mutation
        sync_payload = {
            "query": SPRINT_REPORT_QUERY,
            "variables": {"projectId": project_id, "from": FROM_DATE}
        }
        
        sync_message = "Failed"
        try:
            sync_res = requests.post(URL, json=sync_payload, headers=HEADERS)
            sync_res.raise_for_status()
            sync_data = sync_res.json()
            
            if "errors" in sync_data:
                print(f"  ❌ Sync Error: {sync_data['errors']}")
                sync_message = f"GraphQL Error: {sync_data['errors']}"
            else:
                sync_message = sync_data["data"]["generateSprintReportOfProject"]["overallScore"]
                print(f"  ✅ Sync Successful Agile Score: {sync_message}")
        except Exception as e:
            print(f"  💥 Sync HTTP request failed: {e}")
            sync_message = f"HTTP Request Error: {e}"

        # Construct log entry with just the sync result info
        log_entry = {
            "projectId": project_id,
            "projectName": project_name,
            "projectStatus": project.get("projectStatus"),
            "sync_message": sync_message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save this entry to your output file
        save_to_json_file(log_entry)
        print(f"  💾 Results logged to {OUTPUT_FILE}.")

        # Rate-limiting cushion
        time.sleep(1)
        print()

    print(f"🏁 Execution finished completely. Outputs logged in '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    run_automation_workflow()

