from ai21 import AI21Client


api_key = "oThB3VqcCJnJ7VIRPeUm334FTCcL1exE"
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
