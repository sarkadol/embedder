#!/usr/bin/python3
import os
import json
import glob
import re
import requests
from pathlib import Path
from langchain.text_splitter import MarkdownTextSplitter

# chunksize = 500
# chunkoverlap = 100
chunksize = 1000
chunkoverlap = 200

def process_meta(base_path, lang, current_dir=""):
    # Determine the correct meta filename based on language
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
        # Construct full path for current item
        full_item_path = os.path.join(base_path, current_dir, item)

        # Check for file existence
        if lang == "en":
            file_candidate = f"{full_item_path}.mdx"
        else:
            file_candidate = f"{full_item_path}.cz.mdx"

        if os.path.isfile(file_candidate):
            results.append(os.path.relpath(file_candidate, base_path).replace("\\", "/"))
            continue

        # Handle directory case
        dir_meta_path = os.path.join(full_item_path, "meta.cz.json" if lang == "cz" else "meta.json")
        if os.path.isdir(full_item_path) and os.path.exists(dir_meta_path):
            nested_dir = os.path.join(current_dir, item) if current_dir else item
            results.extend(process_meta(base_path, lang, nested_dir))

    return results

def main():
    #base_dir = "rad"
    base_dir = "kube-docs/content/docs"
    all_files = []
    all_chunks = []

    for meta_path in glob.glob(os.path.join(base_dir, "meta*.json")):
        # Determine language from filename
        filename = os.path.basename(meta_path)
        lang = "cz" if filename == "meta.cz.json" else "en"

        print(f"Process lang {lang}")
        # Process the meta file and its hierarchy
        found_files = process_meta(base_dir, lang)
        all_files.extend(found_files)

    # Remove duplicates and sort
    unique_files = sorted(set(all_files))

    print(f"Unique files: {unique_files}")

    # Print results
    for file_path in unique_files:
        path_obj = Path(os.path.join(base_dir,file_path))
        with open(os.path.join(base_dir,file_path), "r", encoding="utf-8") as f:
            content = f.read()

        filename = file_path.split("/")[-1]
        lang_prefix = "cz" if ".cz.mdx" in filename else "en"
        doc_id = file_path.replace("index.mdx", "").rstrip("/")
        if lang_prefix == "cz":
            metadata_path = "/" + lang_prefix + "/docs/" + doc_id.replace(".cz.mdx", "")
        else:
            metadata_path = "/" + lang_prefix + "/docs/" + doc_id.replace(".mdx", "")

        # Extract title from first # heading
        title = ""
        for line in content.split("\n"):
            if line.startswith("title: "):
                title = line.replace("title: ", "", 1).strip()
                break

        # 2. Preprocess content
        # Convert HTML tags to spaces
        cleaned = re.sub(r"<[^>]+>", " ", content, flags=re.IGNORECASE)
        # Collapse whitespace
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        # 3. Split with MarkdownTextSplitter
        splitter = MarkdownTextSplitter(
            chunk_size=chunksize,
            chunk_overlap=chunkoverlap,
        )
        chunks = splitter.create_documents([cleaned])

        # Add metadata to chunks
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

        # 4. Upload to EMBEDURL
        print("uploading to EMBEDURL...")
        #embed_url = os.environ.get("EMBEDURL")

        # HARDCODED URL FOR TESTING
        embed_url = "https://embedbase-dev.dyn.cloud.e-infra.cz/v1/test"
        if not embed_url:
            embed_url = "https://embedbase.dyn.cloud.e-infra.cz/v1/muni-documentation"
        print(f"EMBEDURL: {embed_url}")
        chunk_count = len(all_chunks)
        batch_size = 500  # Upload 100 chunks per request

        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i + batch_size]
            response = requests.post(
                embed_url,
                json={"documents": batch},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                print(f"Batch {i}-{i + len(batch)} uploaded successfully.")
            else:
                print(f"Batch {i}-{i + len(batch)} FAILED: {response.status_code}")
                print(response.text)
        print(f"Uploaded {chunk_count} chunks")

if __name__ == "__main__":
    main()
