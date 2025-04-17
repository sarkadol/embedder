
#!/usr/bin/python3
import os
import json
import glob
import requests
from pathlib import Path

def process_meta(base_path, lang, current_dir=""):
    meta_file = "meta.cz.json" if lang == "cz" else "meta.json"
    meta_path = os.path.join(base_path, current_dir, meta_file)

    if not os.path.exists(meta_path):
        print("meta not exists")
        return []

    try:
        with open(meta_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print("Json error")
        return []

    results = []
    for item in data.get("pages", []):
        full_item_path = os.path.join(base_path, current_dir, item)

        if lang == "en":
            file_candidate = f"{full_item_path}.mdx"
        else:
            file_candidate = f"{full_item_path}.cz.mdx"

        if os.path.isfile(file_candidate):
            results.append(os.path.relpath(file_candidate, base_path).replace("\\", "/"))
            continue

        dir_meta_path = os.path.join(full_item_path, "meta.cz.json" if lang == "cz" else "meta.json")
        if os.path.isdir(full_item_path) and os.path.exists(dir_meta_path):
            nested_dir = os.path.join(current_dir, item) if current_dir else item
            results.extend(process_meta(base_path, lang, nested_dir))

    return results

def main():
    base_dir = "kube-docs/content/docs"
    knowledge_id = "4d2fcbeb-da01-4b36-9577-b57cf671fe77"
    openwebui_url = "https://chat.ai.e-infra.cz"
    with open("utils/api_key.txt", "r", encoding="utf-8") as file:
        api_key = file.read().strip()

    if not api_key:
        print("❌ Please set the OPENWEBUI_API_KEY environment variable.")
        return

    # Check server connectivity by listing models
    print("🔍 Checking server connectivity and API key...")
    model_url = f"{openwebui_url}/api/models"
    model_response = requests.get(model_url, headers={"Authorization": f"Bearer {api_key}"})

    if model_response.status_code == 200:
        model_data = model_response.json()
        model_names = [m["id"] for m in model_data.get("data", [])]
        print(f"✅ Connected! Models available: {model_names}")
    else:
        print(f"❌ Failed to connect or authenticate! Status {model_response.status_code}: {model_response.text}")
        return


    all_files = []

    for meta_path in glob.glob(os.path.join(base_dir, "meta*.json")):
        filename = os.path.basename(meta_path)
        lang = "cz" if filename == "meta.cz.json" else "en"
        print(f"Processing language: {lang}")
        found_files = process_meta(base_dir, lang)
        all_files.extend(found_files)

    unique_files = sorted(set(all_files))
    print(f"Found {len(unique_files)} unique .mdx files")

    for file_path in unique_files:
        full_path = os.path.join(base_dir, file_path)
        filename = Path(file_path).name
        #filename = Path(file_path).name.replace(".mdx", ".md")

        #print(f"\nUploading: {filename}")
        with open(full_path, "rb") as f:
            print(f"\nUploading: {filename}, type {type(f)}")
            response = requests.post(
                f"{openwebui_url}/api/v1/files/",
                headers={"Authorization": f"Bearer {api_key}",
                         'Accept': 'application/json'},
                files={"file": f}
            )
            try:
                msg = response.json()["detail"][0]["msg"]
            except Exception:
                msg = response.text  # fallback if JSON parsing fails
            print(f"{filename} → {response.status_code}: {msg}")

if __name__ == "__main__":
    main()
