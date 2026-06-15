import argparse
import pandas as pd
from pathlib import Path
from rapidfuzz import fuzz
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.mongo_client import MongoDBClient
from config.config import Config

def fuzzy_match(query, target, threshold=80):

    return fuzz.partial_ratio(query.lower(), target.lower()) >= threshold

def fetch_bird_statistics(species_filter=None, fuzzy_threshold=80):
    mongo_client = MongoDBClient()

    species_col = mongo_client.get_collection(Config.SPECIES_COLLECTION)
    audio_col = mongo_client.get_collection(Config.AUDIO_FILES_COLLECTION)
    observations_col = mongo_client.get_collection(Config.OBSERVATIONS_COLLECTION)

    all_species = list(species_col.find({}))

    if species_filter:
        print(f"Applying fuzzy filter: '{species_filter}' (threshold={fuzzy_threshold})")
        filtered_species = [
            s for s in all_species
            if fuzzy_match(species_filter, s.get("common_name", ""), fuzzy_threshold) or
               fuzzy_match(species_filter, s.get("scientific_name", ""), fuzzy_threshold)
        ]
        all_species = filtered_species
        print(f"Filtered to {len(all_species)} species")

    report_data = []

    for species in all_species:
        taxonomic_code = species.get("taxonomic_code")
        scientific_name = species.get("scientific_name", "")

        positive_classifications = audio_col.count_documents({
            "linked_taxonomic_codes": taxonomic_code
        })

        if positive_classifications == 0:
            audio_files = audio_col.find({
                "classification_results.results": {"$exists": True},
                "linked_taxonomic_codes": {"$exists": False}
            })
            for audio_file in audio_files:
                results = audio_file.get("classification_results", {}).get("results", [])
                for result in results:
                    if result.get("scientific_name") == scientific_name:
                        if result.get("confidence", 0) >= 0.5:
                            positive_classifications += 1
                            break

        if positive_classifications > 0:
            kafka_observations = observations_col.count_documents({
                "taxonomic_code": taxonomic_code
            })

            row = {
                "taxonomic_code": taxonomic_code,
                "scientific_name": scientific_name,
                "common_name": species.get("common_name", ""),
                "family": species.get("family", ""),
                "classified_observations": positive_classifications,
                "kafka_observations": kafka_observations,
                "total_observations": positive_classifications + kafka_observations
            }

            report_data.append(row)

    mongo_client.close()
    return report_data

def generate_csv_report(output_path, species_filter=None, fuzzy_threshold=80):
    """Generiranje CSV izvješća"""
    print("Generating CSV report...")
    print(f"Fetching bird statistics from MongoDB...")

    report_data = fetch_bird_statistics(species_filter, fuzzy_threshold)

    print(f"Found {len(report_data)} species with positive classifications")

    if not report_data:
        print(" No data to report")
        df = pd.DataFrame(columns=[
            "taxonomic_code", "scientific_name", "common_name",
            "family", "classified_observations", "kafka_observations", "total_observations"
        ])
    else:
        df = pd.DataFrame(report_data)
        df = df.dropna(subset=['taxonomic_code', 'scientific_name'])
        df = df.sort_values(by='total_observations', ascending=False)
        df = df.reset_index(drop=True)

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)

    print(f"  CSV report: {output_file}")
    print(f"  Total species: {len(df)}")
    if len(df) > 0:
        print(f"  Total observations: {df['total_observations'].sum()}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=f"{Config.OUTPUT_DIR}/bird_report.csv")
    parser.add_argument("--species-filter", default=None)
    parser.add_argument("--fuzzy-threshold", type=int, default=80)
    args = parser.parse_args()

    print("Starting Step 4 - Generate Report...")
    print(f"Output file: {args.output}")
    print(f"Species filter: {args.species_filter}")
    print(f"Fuzzy threshold: {args.fuzzy_threshold}")

    try:
        generate_csv_report(args.output, args.species_filter, args.fuzzy_threshold)
        print(" Step 4 completed")
    except Exception as e:
        print(f"ERROR in Step 4: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()