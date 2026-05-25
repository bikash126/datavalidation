import json
import csv

# Read JSON data from file
with open('joined_projects.json', 'r') as f:
    data = json.load(f)

# Define the CSV file name
csv_file = 'joined_projects.csv'

# Flatten planning for CSV (optional: only first planning item or count)
def flatten_project(project):
    flat = project.copy()
    # If planning is a list, flatten to first item or count
    if isinstance(flat.get('planning'), list):
        if flat['planning']:
            # Example: take first planning id
            flat['planning_id'] = flat['planning'][0].get('id', '')
            flat['planning_status'] = flat['planning'][0].get('status', '')
            flat['planningStatus'] = flat['planning'][0].get('planningStatus', '')
            flat['resourceApproved'] = flat['planning'][0].get('resourceApproved', '')
            flat['requestReviewCategory'] = flat['planning'][0].get('requestReviewCategory', '')
        else:
            flat['planning_id'] = ''
            flat['planning_status'] = ''
            flat['planningStatus'] = ''
            flat['resourceApproved'] = ''
            flat['requestReviewCategory'] = ''
        del flat['planning']
    return flat

# Flatten all projects
data_flat = [flatten_project(p) for p in data]

# Get all fieldnames
fieldnames = set()
for item in data_flat:
    fieldnames.update(item.keys())
fieldnames = list(fieldnames)

# Write to CSV
with open(csv_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data_flat)

print(f"Exported to {csv_file}")
