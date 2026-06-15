import re
import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.mongo_client import MongoDBClient
from config.config import Config

def scrape_species_data(url):
    print(f"Fetching species data from: {url}")
    
    headers = {"User-Agent": "BirdPipeline/1.0"}
    
    try:
        json_url = f"{url}/aves.json"
        response = requests.get(json_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        species_list = []
        
        for item in data:
   
            scientific_name = re.sub(r" \(.*?\)", "", item.get("scientificName", "")).strip()            
            parts = scientific_name.split()
            if len(parts) >= 2:
                taxonomic_code = (parts[0][:3] + parts[1][:3]).lower()
            else:
                taxonomic_code = scientific_name[:6].lower().replace(" ", "")
            
            species = {
                "taxonomic_code": taxonomic_code,
                "scientific_name": scientific_name,                
                "common_name": item.get("canonicalName", ""),
                "family": item.get("family", ""),
                "order": item.get("order", ""),
                "rank": item.get("rank", ""),
                "scraped_at": datetime.now()
            }
            species_list.append(species)
        
        print(f"Fetched {len(species_list)} species")
        return species_list
        
    except Exception as e:
        print(f"Error fetching species data: {e}")
        return []

def store_species_in_mongodb(species_list):

    mongo_client = MongoDBClient()
    collection = mongo_client.get_collection(Config.SPECIES_COLLECTION)
    
    inserted, skipped = 0, 0
    for species in species_list:
        if not collection.find_one({"taxonomic_code": species["taxonomic_code"]}):
            collection.insert_one(species)
            inserted += 1
        else:
            skipped += 1
    
    print(f"Inserted: {inserted}, Skipped: {skipped}")
    mongo_client.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="species_scraped")
    args = parser.parse_args()
    
    mongo_client = MongoDBClient()
    collection = mongo_client.get_collection(Config.SPECIES_COLLECTION)
    
    if collection.count_documents({}) > 0:
        print("Data already exists. Skipping.")
        mongo_client.close()
        return
    
    mongo_client.close()
    
    species_data = scrape_species_data(Config.SPECIES_DATA_URL)
    if species_data:
        store_species_in_mongodb(species_data)
        print(" Step 1 completed")

if __name__ == "__main__":
    main()