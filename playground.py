from ai21 import AI21Client
import logging
import http.client as http_client
import requests
from dotenv import load_dotenv
import os

load_dotenv()

http_client.HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

api_key = os.getenv("AI21_API_KEY")
client = AI21Client(api_key=api_key)

files_ids = client.library.files.list()

# delete all files
for file_res in files_ids:
    file_id = client.library.files.delete(file_res.file_id)
    print(f"Deleted file {file_id}")

# Upload a file
file_id = client.library.files.create(
  file_path="health-insurance-policy.pdf",
  path="/",
  labels=["health-insurance-policy.pdf"],
)
print(file_id)
file_metadata = client.library.files.get(file_id)

# Wait for file to be processed
while file_metadata.status == "PROCESSING":
  file_metadata = client.library.files.get(file_id)

print(file_metadata.status)

# Ask a question that the file answers
run_result = client.beta.maestro.runs.create_and_poll(
  input="Question that the file answers",
  tools=[{"type": "file_search"}],
)

print(run_result.result)

run_results_id = run_result.id

# Now, use the run_results_id to fetch the execution graph steps
graph_url = f"https://api.ai21.com/studio/v1/execution/{run_results_id}/graph?filtered=true"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get(graph_url, headers=headers)

if response.status_code == 200:
    graph_data = response.json()
    print("Execution Graph Steps:")
    print(graph_data)
else:
    print("Failed to get execution graph. Status code:", response.status_code)

