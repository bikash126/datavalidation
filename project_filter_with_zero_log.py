import json

with open("joined_projects.json", "r") as f:
    projects = json.load(f)

zero_hours = [p for p in projects if p.get("totalLoggedHours", 0) == 0]

with open("projects_with_zero_hours.json", "w") as f:
    json.dump(zero_hours, f, indent=4)

print(f"Saved {len(zero_hours)} projects with totalLoggedHours = 0 to projects_with_zero_hours.json")
