from pymongo import MongoClient
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import Config

class MongoDBClient:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.MONGO_DB_NAME]
    
    def get_collection(self, collection_name):
        """Dohvaća MongoDB kolekciju"""
        return self.db[collection_name]
    
    def close(self):
        """Zatvara konekciju"""
        self.client.close()
    
    def collection_exists(self, collection_name):
        """Provjerava postoji li kolekcija"""
        return collection_name in self.db.list_collection_names()