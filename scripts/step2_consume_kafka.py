import argparse
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.kafka_consumer import BirdKafkaConsumer
from utils.mongo_client import MongoDBClient
from config.config import Config

def normalize_observation(raw_message):

    taxonomic_code = raw_message.get("taxonomic_code")
    if not taxonomic_code:
        print(f"  ⚠ Preskačem poruku bez taxonomic_code: {raw_message}")
        return None

    if "location" in raw_message:
        location = raw_message["location"]
    elif "latitude" in raw_message and "longitude" in raw_message:
        location = {
            "latitude": raw_message["latitude"],
            "longitude": raw_message["longitude"]
        }
    else:
        print(f"  ⚠ Poruka bez lokacije, postavljam default: {taxonomic_code}")
        location = {"latitude": None, "longitude": None}

    normalized = {
        "source": "kafka",
        "taxonomic_code": taxonomic_code,
        "location": location,
        "observed_at": raw_message.get("observed_at", datetime.now().isoformat()),
        "received_at": datetime.now()
    }

    additional_data = raw_message.get("additional_data", {})
    if additional_data:
        normalized["biological_data"] = additional_data

    known_fields = {"taxonomic_code", "latitude", "longitude", "location",
                    "observed_at", "additional_data"}
    extra_fields = {k: v for k, v in raw_message.items() if k not in known_fields}
    if extra_fields:
        normalized.update(extra_fields)

    return normalized

def store_observations(observations):
    """Normalizira i pohranjuje opažanja u MongoDB"""
    print(f"Storing {len(observations)} observations...")
    mongo_client = MongoDBClient()
    collection = mongo_client.get_collection(Config.OBSERVATIONS_COLLECTION)

    normalized_observations = []
    skipped = 0

    for raw_msg in observations:
        normalized = normalize_observation(raw_msg)
        if normalized:
            normalized_observations.append(normalized)
        else:
            skipped += 1

    if normalized_observations:
        try:
            result = collection.insert_many(normalized_observations)
            print(f"✓ Stored {len(result.inserted_ids)} observations in MongoDB")
            if skipped > 0:
                print(f"⚠ Skipped {skipped} invalid observations")
        except Exception as e:
            print(f"✗ Error storing observations: {e}")
    else:
        print("No valid observations to store")

    mongo_client.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="kafka_consumed")
    args = parser.parse_args()

    print("Consuming Kafka messages...")
    kafka_consumer = BirdKafkaConsumer()

    try:
        print("Polling messages...")
        messages = kafka_consumer.consume_all_messages()
        print(f"Got {len(messages)} messages")

        if messages:
            print("Calling store_observations...")
            store_observations(messages)
            print("✓ Step 2 completed")
        else:
            print("⚠ No messages on Kafka")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Closing consumer...")
        kafka_consumer.close()
        print("Done")

if __name__ == "__main__":
    main()