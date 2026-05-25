import json
import time
import requests
import constants

URL = constants.API_URL
HEADERS = constants.HEADERS
REQUEST_DELAY_SECONDS = 0.25
MAX_RETRIES = 3

WORKLOG_QUERY_TEMPLATE = """
query ListProjectWorkLogs($paginationParams: BasePaginationParams!, $projectId: Int!, $projectWorklogFilter: ProjectWorklogFilter) {
  listProjectWorkLogs(
    paginationParams: $paginationParams
    projectId: $projectId
    projectWorklogFilter: $projectWorklogFilter
  ) {
    data {
      id
      jiraAssigneeId
      jiraWorkLogId
      loggedHour
      actualCostSpent
      projectTaskId
      projectTask {
        id
        name
        jiraIssueKey
      }
      employeeId
      employee {
        id
        name
      }
      startedAt
      comment
    }
    total
    hasNextPage
  }
}
"""

def fetch_project_worklogs(project_id):
    payload = {
        "operationName": "ListProjectWorkLogs",
        "variables": {
            "projectId": int(project_id),
            "paginationParams": {
                "limit": 15000,
                "skip": 0
            },
            "projectWorklogFilter": {
                "searchText": None,
                "assigneeIds": None
            }
        },
        "query": WORKLOG_QUERY_TEMPLATE
    }
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(URL, json=payload, headers=HEADERS)
            response.raise_for_status()
            res_data = response.json()
            if "errors" in res_data:
                last_error = res_data["errors"]
                error_text = str(last_error)
                if "Too Many Requests" in error_text and attempt < MAX_RETRIES:
                    time.sleep(2 ** attempt)
                    continue
                print(f"❌ GraphQL Error fetching worklogs for project {project_id}: {res_data['errors']}")
                return {"projectId": project_id, "error": res_data["errors"]}
            worklog_response = res_data.get("data", {}).get("listProjectWorkLogs", {})
            worklog_data = worklog_response.get("data", [])
            total_logged_hours = sum(item.get("loggedHour", 0) for item in worklog_data)
            time.sleep(REQUEST_DELAY_SECONDS)
            return {
                "projectId": project_id,
                "total": worklog_response.get("total", 0),
                "totalLoggedHours": total_logged_hours
            }
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)
                continue
            print(f"💥 Network error fetching worklogs for project {project_id}: {e}")
            return {"projectId": project_id, "error": str(e)}
    print(f"💥 Failed fetching worklogs for project {project_id}: {last_error}")
    return {"projectId": project_id, "error": str(last_error)}

def main():
    with open("projects_with_zero_hours.json", "r") as f:
        projects = json.load(f)
    results = []
    for project in projects:
        pid = project.get("id")
        if pid:
            print(f"Fetching worklogs for project {pid}...")
            result = fetch_project_worklogs(pid)
            results.append(result)
    with open("zero_hours_worklogs_results.json", "w") as f:
        json.dump(results, f, indent=4)
    print("Done. Results saved to zero_hours_worklogs_results.json")

if __name__ == "__main__":
    main()
