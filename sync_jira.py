import json
import time
import requests
import constants


# 1. Configuration
URL = constants.API_URL

PROJECTS_FILE = "combined_projects.json"

# 2. Setup Headers (Make sure to update your token if it expires)
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": constants.API_TOKEN
}

# 3. Define both GraphQL Mutations
MUTATION_UPDATE_PLANNING = """
mutation UpdateProjectPlanning($projectPlanningId: Int!, $updateProjectPlanningInput: UpdateProjectPlanningInput!) {
  updateProjectPlanning(
    projectPlanningId: $projectPlanningId
    updateProjectPlanningInput: $updateProjectPlanningInput
  ) {
    message
  }
}
"""

MUTATION_SYNC_PROJECT = """
mutation SyncJiraProject($projectId: Int!, $projectPlanningId: Int!) {
  syncJiraProject(projectId: $projectId, projectPlanningId: $projectPlanningId) {
    message
  }
}
"""

def execute_graphql(payload, action_name, pid):
    """Helper function to post GraphQL requests and handle errors"""
    try:
        response = requests.post(URL, json=payload, headers=HEADERS)
        response.raise_for_status()
        response_data = response.json()
        
        if "errors" in response_data:
            print(f"  ❌ {action_name} Error for Project {pid}: {response_data['errors']}")
            return False
        else:
            # Dynamically extract the message based on which mutation was run
            data_key = list(response_data["data"].keys())[0]
            msg = response_data["data"][data_key]["message"]
            print(f"  ✅ {action_name} Success: {msg}")
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"  💥 HTTP Request failed during {action_name} for Project {pid}: {e}")
        return False


def load_projects_list(filename=PROJECTS_FILE):
    """Build the project/planning ID list from combined_projects.json."""
    with open(filename, "r", encoding="utf-8") as f:
        projects = json.load(f)

    project_pairs = []

    for project in projects:
        project_id = project.get("id")
        planning_items = project.get("planning") or []

        if not project_id or not planning_items:
            continue

        for planning in planning_items:
            planning_id = planning.get("id")
            if planning_id is None:
                continue

            project_pairs.append(
                {
                    "projectId": project_id,
                    "projectPlanningId": planning_id,
                }
            )

    return project_pairs

def sync_all_projects():
    projects_list = load_projects_list()
    print(f"🚀 Starting sequence for {len(projects_list)} projects...\n")
    
    for project in projects_list:
        p_id = project["projectId"]
        pp_id = project["projectPlanningId"]
        
        print(f"🔄 Processing Project ID: {p_id} (Planning ID: {pp_id})")
        
        # --- STEP 1: Update Project Planning ---
        payload_update = {
            "query": MUTATION_UPDATE_PLANNING,
            "variables": {
                "projectPlanningId": pp_id,
                "updateProjectPlanningInput": {
                    "lastSyncedAt": "2021-01-01"
                }
            }
        }
        step1_success = execute_graphql(payload_update, "Step 1 (Update Planning)", p_id)
        
        # Only proceed to step 2 if step 1 succeeded
        if step1_success:
            # --- STEP 2: Sync Jira Project ---
            payload_sync = {
                "query": MUTATION_SYNC_PROJECT,
                "variables": {
                    "projectId": p_id,
                    "projectPlanningId": pp_id
                }
            }
            execute_graphql(payload_sync, "Step 2 (Sync Jira Project)", p_id)
        else:
            print(f"  ⚠️ Skipping Step 2 for Project {p_id} because Step 1 failed.")
            
        print("-" * 50)
        time.sleep(1) # 1-second pause between projects

    print("🏁 Sequential run finished.")

if __name__ == "__main__":
    sync_all_projects()