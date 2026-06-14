import argparse
import os
import json
import time
from pathlib import Path
from datetime import datetime
import httpx
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.minio_client import MinIOClient
from utils.mongo_client import MongoDBClient
from config.config import Config

def load_location_metadata(audio_dir):
    """Učitava metadata o lokaciji"""
    metadata_file = Path(audio_dir) / "location_metadata.json"
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            return json.load(f)
    return {"latitude": 45.8150, "longitude": 15.9819, "location_name": "Zagreb"}

def classify_bird_audio(audio_filepath):
    """API zahtjev za klasifikaciju"""
    print(f"Classifying: {audio_filepath}")
    api_url = Config.BIRD_CLASSIFICATION_API
    
    with open(audio_filepath, 'rb') as audio_file:
        files = {'file': audio_file}
        request_log = {
            "timestamp": datetime.now().isoformat(),
            "filename": os.path.basename(audio_filepath),
            "api_url": api_url,
            "status": "pending"
        }
        
        try:
            response = httpx.post(api_url, files=files, timeout=60.0)
            request_log["status_code"] = response.status_code
            
            if response.status_code == 200:
                request_log["status"] = "success"
                print("  ✓ Classification successful")
                return response.json(), request_log
            else:
                request_log["status"] = "failed"
                print(f"  ✗ Failed: {response.status_code}")
                return None, request_log
        except Exception as e:
            request_log["status"] = "error"
            request_log["error"] = str(e)
            print(f"  ✗ Error: {e}")
            return None, request_log

def process_audio_files(audio_dir):
    """Procesira sve audio datoteke"""
    print(f"Processing audio files in: {audio_dir}")
    audio_dir_path = Path(audio_dir)
    print(f"Audio dir path object: {audio_dir_path}")
    
    audio_extensions = ['.mp3', '.wav', '.flac', '.ogg', '.m4a']
    audio_files = []
    
    print(f"Searching for audio files...")
    for ext in audio_extensions:
        found = list(audio_dir_path.glob(f'*{ext}'))
        print(f"  {ext}: found {len(found)} files")
        audio_files.extend(found)
    
    print(f"Total audio files found: {len(audio_files)}")
    
    # ... rest of the code continues
    location_data = load_location_metadata(audio_dir)
    
    minio_client = MinIOClient()
    mongo_client = MongoDBClient()
    collection = mongo_client.get_collection(Config.AUDIO_FILES_COLLECTION)
    
    for audio_file in audio_files:
        print(f"\nProcessing: {audio_file.name}")
        
        file_id = minio_client.upload_file(str(audio_file))
        if not file_id:
            continue
        
        classification_results, api_log = classify_bird_audio(str(audio_file))
        log_id = minio_client.upload_json_log(api_log, f"{file_id}_log.json")
        
        audio_doc = {
            "file_id": file_id,
            "original_filename": audio_file.name,
            "location": location_data,
            "uploaded_at": datetime.now(),
            "classification_log": log_id,
            "classification_results": classification_results
        }
        
        collection.insert_one(audio_doc)
        print("  ✓ Stored in MongoDB")
        time.sleep(1)
    
    print(f"\n✓ Processed {len(audio_files)} files")
    mongo_client.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio-dir", default=Config.AUDIO_DIR)
    parser.add_argument("--output", default="audio_processed")
    args = parser.parse_args()
    
    print(f"Starting Step 3...")
    print(f"Audio directory: {args.audio_dir}")
    
    try:
        process_audio_files(args.audio_dir)
        print("✓ Step 3 completed")
    except Exception as e:
        print(f"ERROR in Step 3: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()