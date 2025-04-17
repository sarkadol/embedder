#!/usr/bin/python3
import os
import json
import glob
import re
import requests
from pathlib import Path
from langchain.text_splitter import MarkdownTextSplitter

chunksize = 1000
chunkoverlap = 200

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
    openwebui_url = "https://chat.ai.e-infra.cz"
    knowledge_id = "4d2fcbeb-da01-4b36-9577-b57cf671fe77"
    upload_url = f"{openwebui_url}/api/v1/knowledge/{knowledge_id}/file/add"

    with open("utils/api_key.txt", "r", encoding="utf-8") as file:
        api_key = file.read().strip()

    if not api_key:
        print("❌ No API key found.")
        return

    all_files = []
    all_chunks = []

    for meta_path in glob.glob(os.path.join(base_dir, "meta*.json")):
        filename = os.path.basename(meta_path)
        lang = "cz" if filename == "meta.cz.json" else "en"
        print(f"Processing language: {lang}")
        found_files = process_meta(base_dir, lang)
        all_files.extend(found_files)

    unique_files = sorted(set(all_files))
    print(f"Found {len(unique_files)} unique files")

    for file_path in unique_files:
        full_path = os.path.join(base_dir, file_path)
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        filename = Path(file_path).name
        lang_prefix = "cz" if ".cz.mdx" in filename else "en"
        doc_id = file_path.replace("index.mdx", "").rstrip("/")
        metadata_path = f"/{lang_prefix}/docs/" + (doc_id.replace(".cz.mdx", "") if lang_prefix == "cz" else doc_id.replace(".mdx", ""))

        title = ""
        for line in content.split("\n"):
            if line.startswith("title: "):
                title = line.replace("title: ", "", 1).strip()
                break

        cleaned = re.sub(r"<[^>]+>", " ", content, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        splitter = MarkdownTextSplitter(chunk_size=chunksize, chunk_overlap=chunkoverlap)
        chunks = splitter.create_documents([cleaned])

        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "data": chunk.page_content,
                "metadata": {
                    "path": metadata_path,
                    "title": title,
                    "chunknum": i,
                    "lang": lang_prefix
                }
            })

    print(f"Uploading {len(all_chunks)} chunks to OpenWebUI...")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.post(
        upload_url,
        json={"documents": all_chunks},
        headers=headers
    )
    print(f"Response {response.status_code}")
    try:
        print(response.json())
    except Exception:
        print(response.text)

if __name__ == "__main__":
    main()
