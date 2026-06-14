import argparse
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.kafka_consumer import BirdKafkaConsumer
from utils.mongo_client import MongoDBClient
from config.config import Config

def store_observations(observations):
    """Pohrana opažanja u MongoDB"""
    print(f"Storing {len(observations)} observations...")
    mongo_client = MongoDBClient()
    collection = mongo_client.get_collection(Config.OBSERVATIONS_COLLECTION)
    
    if observations:
        for obs in observations:
            obs['received_at'] = datetime.now()
        
        try:
            result = collection.insert_many(observations)
            print(f"✓ Stored {len(result.inserted_ids)} observations in MongoDB")
        except Exception as e:
            print(f"✗ Error storing observations: {e}")
    else:
        print("No observations to store")
    
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