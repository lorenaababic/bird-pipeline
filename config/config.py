import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # MinIO Configuration
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
    MINIO_BUCKET = os.getenv("MINIO_BUCKET", "bird-audio-files")
    MINIO_SECURE = False
    
    # MongoDB Configuration
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:admin123@localhost:27017")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "bird_observation_db")
    
    # Collections
    SPECIES_COLLECTION = "species"
    OBSERVATIONS_COLLECTION = "observations"
    AUDIO_FILES_COLLECTION = "audio_files"
    
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "bird-observations")
    KAFKA_GROUP_ID = "bird-pipeline-consumer"
    
    # API Configuration
    SPECIES_DATA_URL = os.getenv("SPECIES_DATA_URL", "https://aves.regoch.net")
    BIRD_CLASSIFICATION_API = os.getenv("BIRD_CLASSIFICATION_API", "https://aves.regoch.net/api/classify")
    
    # Directories
    AUDIO_DIR = "audio_files"
    OUTPUT_DIR = "output"