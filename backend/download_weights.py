import os
import sys
import time
import requests

TARGET_DIR = r"C:\Users\Rushikesh\.cache\huggingface\hub\models--Helsinki-NLP--opus-mt-en-mr\snapshots\278873c7c6d7ef71072f8af040c91d1b5422ad88"
TARGET_FILE = os.path.join(TARGET_DIR, "pytorch_model.bin")
URL = "https://huggingface.co/Helsinki-NLP/opus-mt-en-mr/resolve/main/pytorch_model.bin"

os.makedirs(TARGET_DIR, exist_ok=True)

temp_file = TARGET_FILE + ".part"
downloaded_bytes = os.path.getsize(temp_file) if os.path.exists(temp_file) else 0

headers = {}
if downloaded_bytes > 0:
    headers["Range"] = f"bytes={downloaded_bytes}-"
    print(f"Resuming download from byte {downloaded_bytes} ({downloaded_bytes / (1024*1024):.2f} MB)...")
else:
    print("Starting fresh download of pytorch_model.bin (291 MB)...")

try:
    with requests.get(URL, headers=headers, stream=True, timeout=30) as r:
        r.raise_for_status()
        total_size = int(r.headers.get("content-length", 0)) + downloaded_bytes
        mode = "ab" if downloaded_bytes > 0 else "wb"
        start_time = time.time()
        last_log = start_time
        
        with open(temp_file, mode) as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024): # 1MB chunks
                if chunk:
                    f.write(chunk)
                    downloaded_bytes += len(chunk)
                    curr_time = time.time()
                    if curr_time - last_log > 5:
                        mb = downloaded_bytes / (1024 * 1024)
                        total_mb = total_size / (1024 * 1024)
                        pct = (downloaded_bytes / total_size) * 100 if total_size else 0
                        speed = (downloaded_bytes / (curr_time - start_time)) / (1024 * 1024)
                        print(f"Downloaded: {mb:.1f}/{total_mb:.1f} MB ({pct:.1f}%) at {speed:.2f} MB/s", flush=True)
                        last_log = curr_time

    if os.path.exists(TARGET_FILE):
        os.remove(TARGET_FILE)
    os.rename(temp_file, TARGET_FILE)
    print("SUCCESS: pytorch_model.bin downloaded and verified!", flush=True)
except Exception as e:
    print(f"Download interrupted: {e}", flush=True)
    sys.exit(1)
