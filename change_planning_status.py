import requests
import constants
import json
import time

URL = constants.API_URL
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": constants.API_TOKEN
}

CHANGE_PLANNING_STATUS_MUTATION = """
mutation ChangePlanningActiveStatus($status: PlanningStatus!, $projectId: Int!, $projectPlanningId: Int!) {
  changePlanningActiveStatus(
    status: $status
    projectId: $projectId
    projectPlanningId: $projectPlanningId
  ) {
    message
  }
}
"""

def change_planning_active_status(project_id, project_planning_id, status):
    payload = {
        "operationName": "ChangePlanningActiveStatus",
        "variables": {
            "projectId": project_id,
            "projectPlanningId": project_planning_id,
            "status": status
        },
        "query": CHANGE_PLANNING_STATUS_MUTATION
    }
    try:
        response = requests.post(URL, json=payload, headers=HEADERS)
        response.raise_for_status()
        res_data = response.json()
        if "errors" in res_data:
            print(f"❌ GraphQL Error: {res_data['errors']}")
            return None
        return res_data["data"]["changePlanningActiveStatus"]["message"]
    except Exception as e:
        print(f"💥 Network error: {e}")
        return None

def main():
    input_file = "combined_projects.json"
    status = "Active"  # or any status you want to set
    with open(input_file, "r", encoding="utf-8") as f:
        projects = json.load(f)
    for project in projects:
        project_id = project.get("id")
        project_name = project.get("name")
        planning_list = project.get("planning", [])
        for planning in planning_list:
            planning_id = planning.get("id")
            print(f"Updating project {project_name} (ID: {project_id}), planning ID: {planning_id} to status: {status}")
            result = change_planning_active_status(project_id, planning_id, status)
            print(f"  Result: {result}")
            time.sleep(0.5)  # To avoid rate limits

if __name__ == "__main__":
    main()
