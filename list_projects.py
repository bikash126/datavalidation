import json
import time
import requests
import constants

# 1. Base Configuration
URL = constants.API_URL
REQUEST_DELAY_SECONDS = 0.25
MAX_PLANNING_RETRIES = 3

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": constants.API_TOKEN
}

# Explicitly selecting fields including the 'status' field
QUERY_TEMPLATE = """
query ListProjects($filterParams: ProjectFilterParams!, $paginationParams: BasePaginationParams!) {
  listProjects(filterParams: $filterParams, paginationParams: $paginationParams) {
    data {
      id
      name
      isArchive
      developmentStatus
      status
      projType
    }
  }
}
"""

PLANNING_QUERY_TEMPLATE = """
query ListProjectPlanning($projectId: Int!) {
    listProjectPlanning(projectId: $projectId) {
        id
        status
        planningStatus
        resourceApproved
        requestReviewCategory
    }
}
"""

def fetch_projects(filter_params):
    """Helper to query the API for a specific filter payload"""
    payload = {
        "operationName": "ListProjects",
        "variables": {
            "filterParams": filter_params,
            "paginationParams": {
                "order": "desc",
                "orderBy": "createdAt",
                "limit": 400,
                "skip": 0
            }
        },
        "query": QUERY_TEMPLATE
    }
    try:
        response = requests.post(URL, json=payload, headers=HEADERS)
        response.raise_for_status()
        res_data = response.json()
        
        if "errors" in res_data:
            print(f"❌ GraphQL Error for filter {filter_params}: {res_data['errors']}")
            return []
        return res_data["data"]["listProjects"]["data"]
        
    except Exception as e:
        print(f"💥 Network error fetching data for filter {filter_params}: {e}")
        return []


def fetch_project_planning(project_id):
    """Helper to query planning records for a specific project id."""
    payload = {
        "operationName": "ListProjectPlanning",
        "variables": {
            "projectId": int(project_id)
        },
        "query": PLANNING_QUERY_TEMPLATE
    }
    last_error = None

    for attempt in range(1, MAX_PLANNING_RETRIES + 1):
        try:
            response = requests.post(URL, json=payload, headers=HEADERS)
            response.raise_for_status()
            res_data = response.json()

            if "errors" in res_data:
                last_error = res_data["errors"]
                error_text = str(last_error)
                if "Too Many Requests" in error_text and attempt < MAX_PLANNING_RETRIES:
                    time.sleep(2 ** attempt)
                    continue
                print(f"❌ GraphQL Error for project {project_id}: {res_data['errors']}")
                return []

            planning_items = res_data.get("data", {}).get("listProjectPlanning", [])
            time.sleep(REQUEST_DELAY_SECONDS)
            return [
                {
                    "id": item.get("id"),
                    "status": item.get("status"),
                    "planningStatus": item.get("planningStatus"),
                    "resourceApproved": item.get("resourceApproved"),
                    "requestReviewCategory": item.get("requestReviewCategory"),
                }
                for item in planning_items
            ]

        except Exception as e:
            last_error = e
            if attempt < MAX_PLANNING_RETRIES:
                time.sleep(2 ** attempt)
                continue
            print(f"💥 Network error fetching planning for project {project_id}: {e}")
            return []

    print(f"💥 Failed fetching planning for project {project_id}: {last_error}")
    return []

def main():
    # --- QUERY 1: Specific Project Stages ---
    print("📡 Fetching Query 1 (Project Stage Filter)...")
    stage_filter = {
        "isArchive": False, 
        "projectStage": ["1165050018", "1286198928"]
    }
    projects_stage = fetch_projects(stage_filter)
    
    # --- QUERY 2: My Projects Filter ---
    print("📡 Fetching Query 2 (My Projects Filter)...")
    my_projects_filter = {
        "isArchive": False, 
        "myProjects": True
    }
    projects_my = fetch_projects(my_projects_filter)
    
    # --- COMBINE & DE-DUPLICATE RESULTS ---
    combined_dict = {}
    
    for project in (projects_stage + projects_my):
        project_id = project.get("id")
        if project_id and project_id not in combined_dict:
            planning = fetch_project_planning(project_id)
      
            combined_dict[project_id] = {
                "id": project_id,
                "name": project.get("name"),
                "isArchive": project.get("isArchive"),
                "projecType": project.get("projType"),
                "developmentStatus": project.get("developmentStatus"),
                "status": project.get("status"),
                "planning": planning
            }
            
    final_unique_list = list(combined_dict.values())
    
    # --- WRITE DATA OUT TO FILE ---
    output_filename = "combined_projects1.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(final_unique_list, f, indent=4)
        
    print(f"🏁 Done! Saved {len(final_unique_list)} unique projects into '{output_filename}'")

if __name__ == '__main__':
    main()

