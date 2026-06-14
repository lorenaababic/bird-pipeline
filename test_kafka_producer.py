from confluent_kafka import Producer
import json

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()}')

producer = Producer({'bootstrap.servers': 'localhost:9092'})

# Test poruke - opažanja ptica
observations = [
    {
        "taxonomic_code": "gutpuc",
        "latitude": 45.8150,
        "longitude": 15.9819,
        "observed_at": "2025-02-10T10:30:00Z",
        "additional_data": {
            "body_size": "medium",
            "migration_status": "resident"
        }
    },
    {
        "taxonomic_code": "gutedu",
        "latitude": 45.8050,
        "longitude": 15.9700,
        "observed_at": "2025-02-10T11:00:00Z",
        "additional_data": {
            "habitat": "urban",
            "flight_pattern": "direct"
        }
    },
    {
        "taxonomic_code": "gutplu",
        "latitude": 45.8100,
        "longitude": 15.9800,
        "observed_at": "2025-02-10T12:00:00Z",
        "additional_data": {
            "habitat": "forest",
            "migration_status": "migrant"
        }
    }
]

for obs in observations:
    producer.produce(
        'bird-observations',
        value=json.dumps(obs).encode('utf-8'),
        callback=delivery_report
    )

producer.flush()
print("✓ Test messages sent to Kafka!")