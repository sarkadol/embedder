import requests

api_key = open("utils/api_key.txt").read().strip()
openwebui_url = "https://chat.ai.e-infra.cz"
knowledge_id = "4d2fcbeb-da01-4b36-9577-b57cf671fe77"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Accept": "application/json"
}

# Step 1: Get all uploaded files
response = requests.get(f"{openwebui_url}/api/v1/files/", headers=headers)
if response.status_code != 200:
    print("❌ Failed to list files:", response.text)
    exit()

files = response.json()
print(f"🔍 Found {len(files)} uploaded files.")

# Step 2: Attach each file to the knowledge base
for file in files:
    file_id = file["id"]
    filename = file["filename"]
    print(f"📎 Attaching {filename}...")

    attach = requests.post(
        f"{openwebui_url}/api/v1/knowledge/{knowledge_id}/file/add",
        headers={**headers, "Content-Type": "application/json"},
        json={"file_id": file_id}
    )

    if attach.status_code == 200:
        print(f"✅ {filename} added to KB.")
    else:
        print(f"❌ Failed to add {filename}: {attach.text}")
