import os, requests, datetime
from datetime import timezone

api_url = os.environ.get("PAPERCLIP_API_URL")
api_key = os.environ.get("PAPERCLIP_API_KEY")
company_id = os.environ.get("PAPERCLIP_COMPANY_ID")

# The location where reports should be saved.
# Defaults to the new documentation repo location as requested by the CEO.
DEFAULT_REPORTS_DIR = "./documentations/ops/reports"
reports_dir = os.environ.get("VISIBLE_PROGRESS_REPORTS_DIR", DEFAULT_REPORTS_DIR)

headers = {"Authorization": f"Bearer {api_key}"}

# Get agents
agents_res = requests.get(f"{api_url}/api/companies/{company_id}/agents", headers=headers)
agents = agents_res.json()
agent_map = {a["id"]: a["name"] for a in agents}

# Get recent issues
now = datetime.datetime.now(timezone.utc)
threshold = now - datetime.timedelta(minutes=30)

issues_res = requests.get(f"{api_url}/api/companies/{company_id}/issues?limit=100", headers=headers)
issues = issues_res.json()

report = "## CEO Visibility Report: Last 30 Minutes\n\n"

agent_work = {a["name"]: [] for a in agents}

for issue in issues:
    updated_at = datetime.datetime.fromisoformat(issue["updatedAt"].replace("Z", "+00:00"))
    if updated_at < threshold:
        continue
        
    assignee_id = issue.get("assigneeAgentId")
    agent_name = agent_map.get(assignee_id, "Unassigned")
    if agent_name not in agent_work:
        agent_work[agent_name] = []
        
    agent_work[agent_name].append({
        "identifier": issue["identifier"],
        "title": issue["title"],
        "status": issue["status"]
    })

for agent_name, tasks in agent_work.items():
    if not tasks:
        report += f"**{agent_name}**: No recent activity.\n"
    else:
        report += f"**{agent_name}**:\n"
        for task in tasks:
            status_icon = "✅" if task["status"] == "done" else ("🚧" if task["status"] in ["blocked", "cancelled"] else ("🔄" if task["status"] in ["in_progress", "in_review"] else "⏳"))
            report += f"- {status_icon} [{task['identifier']}](/SUPAA/issues/{task['identifier']}) {task['title']} (Status: `{task['status']}`)\n"
    report += "\n"

# 1. Save to local report.md for backward compatibility
with open("report.md", "w") as f:
    f.write(report)

# 2. Save to timestamped file in the documentation repo
timestamp = now.strftime("%Y-%m-%d_%H%M")
filename = f"VISIBLE_PROGRESS_REPORT_{timestamp}.md"

if not os.path.exists(reports_dir):
    try:
        os.makedirs(reports_dir, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create reports directory {reports_dir}: {e}")

report_path = os.path.join(reports_dir, filename)
try:
    with open(report_path, "w") as f:
        f.write(report)
    print(f"Report saved to {report_path}")
except Exception as e:
    print(f"Error saving report to {report_path}: {e}")

print(report)
