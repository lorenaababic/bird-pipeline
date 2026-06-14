from confluent_kafka import Consumer, KafkaException
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import Config

class BirdKafkaConsumer:
    def __init__(self):
        self.consumer = Consumer({
            'bootstrap.servers': Config.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': Config.KAFKA_GROUP_ID,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True
        })
        self.consumer.subscribe([Config.KAFKA_TOPIC])
    
    def consume_all_messages(self):
        """
        Konzumira sve trenutne poruke sa Kafke
        Returns: lista poruka
        """
        messages = []
        
        # Poll poruke sa timeout-om
        timeout = 5.0
        while True:
            msg = self.consumer.poll(timeout=timeout)
            
            if msg is None:
                break
            
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                break
            
            # Deserialize JSON
            try:
                value = json.loads(msg.value().decode('utf-8'))
                messages.append(value)
            except json.JSONDecodeError:
                print(f"Failed to decode message: {msg.value()}")
        
        print(f"Konzumirano {len(messages)} poruka sa Kafke")
        return messages
    
    def close(self):
        """Zatvara consumer"""
        self.consumer.close()