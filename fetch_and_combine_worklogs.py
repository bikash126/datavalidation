import json
import requests
import time
import constants

URL = constants.API_URL
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": constants.API_TOKEN
}
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
                return {"total": 0, "totalLoggedHours": 0}
            worklog_response = res_data.get("data", {}).get("listProjectWorkLogs", {})
            worklog_data = worklog_response.get("data", [])
            total_logged_hours = sum(item.get("loggedHour", 0) for item in worklog_data)
            time.sleep(REQUEST_DELAY_SECONDS)
            return {
                "total": worklog_response.get("total", 0),
                "totalLoggedHours": total_logged_hours
            }
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)
                continue
            print(f"💥 Network error fetching worklogs for project {project_id}: {e}")
            return {"total": 0, "totalLoggedHours": 0}
    print(f"💥 Failed fetching worklogs for project {project_id}: {last_error}")
    return {"total": 0, "totalLoggedHours": 0}

def main():
    with open('combined_projects.json', 'r') as f:
        projects = json.load(f)
    updated_projects = []
    for project in projects:
        project_id = project.get('id')
        if project_id is not None:
            worklogs = fetch_project_worklogs(project_id)
            project['worklogsTotal'] = worklogs['total']
            project['totalLoggedHours'] = worklogs['totalLoggedHours']
        updated_projects.append(project)
    with open('combined_projects_with_worklogs.json', 'w') as f:
        json.dump(updated_projects, f, indent=4)
    print(f"Updated {len(updated_projects)} projects with worklog data. Output: combined_projects_with_worklogs.json")

if __name__ == "__main__":
    main()
