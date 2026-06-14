import boto3
from botocore.exceptions import ClientError
import uuid
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import Config

class MinIOClient:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url=f"http://{Config.MINIO_ENDPOINT}",
            aws_access_key_id=Config.MINIO_ACCESS_KEY,
            aws_secret_access_key=Config.MINIO_SECRET_KEY,
        )
        self.bucket = Config.MINIO_BUCKET
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Kreira bucket ako ne postoji"""
        try:
            self.s3.head_bucket(Bucket=self.bucket)
        except ClientError:
            self.s3.create_bucket(Bucket=self.bucket)
            print(f"Kreiran MinIO bucket: {self.bucket}")
    
    def upload_file(self, filepath, metadata=None):
        """
        Upload datoteke na MinIO
        Returns: unique file_id
        """
        file_id = str(uuid.uuid4())
        
        extra_args = {}
        if metadata:
            extra_args['Metadata'] = metadata
        
        try:
            self.s3.upload_file(filepath, self.bucket, file_id, ExtraArgs=extra_args)
            print(f"Uploaded: {filepath} -> {file_id}")
            return file_id
        except ClientError as e:
            print(f"Error uploading {filepath}: {e}")
            return None
    
    def upload_json_log(self, json_data, log_name=None):
        """Upload JSON loga na MinIO"""
        import json
        from io import BytesIO
        
        log_id = log_name or str(uuid.uuid4())
        json_bytes = json.dumps(json_data, indent=2).encode('utf-8')
        
        try:
            self.s3.upload_fileobj(
                BytesIO(json_bytes),
                self.bucket,
                log_id
            )
            print(f"Uploaded log: {log_id}")
            return log_id
        except ClientError as e:
            print(f"Error uploading log: {e}")
            return None
    
    def download_file(self, file_id, destination):
        """Download datoteke s MinIO"""
        try:
            self.s3.download_file(self.bucket, file_id, destination)
            print(f"Downloaded: {file_id} -> {destination}")
            return True
        except ClientError as e:
            print(f"Error downloading {file_id}: {e}")
            return False