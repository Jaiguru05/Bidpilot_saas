import boto3
import hashlib
import logging
from datetime import timedelta
from botocore.exceptions import ClientError
from app.config import settings

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME
    
    async def upload_tender_pdf(self, org_id: str, tender_id: str, file_path: str, file_size: int) -> dict:
        """Upload PDF to S3"""
        s3_key = f"organizations/{org_id}/tenders/{tender_id}/original.pdf"
        file_hash = self.compute_file_hash(file_path)
        
        try:
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    "ServerSideEncryption": "AES256",
                    "Metadata": {
                        "org_id": org_id,
                        "tender_id": tender_id,
                        "file_hash": file_hash
                    }
                }
            )
            logger.info(f"Uploaded {s3_key}")
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise
        
        return {
            "s3_key": s3_key,
            "file_hash": file_hash,
            "file_size": file_size,
            "bucket": self.bucket_name
        }
    
    def generate_signed_url(self, org_id: str, tender_id: str, expiration: int = 3600) -> str:
        """Generate time-limited signed URL"""
        s3_key = f"organizations/{org_id}/tenders/{tender_id}/original.pdf"
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate signed URL: {e}")
            raise
    
    async def download_file(self, org_id: str, tender_id: str) -> bytes:
        """Download PDF from S3"""
        s3_key = f"organizations/{org_id}/tenders/{tender_id}/original.pdf"
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            return response['Body'].read()
        except ClientError as e:
            logger.error(f"S3 download failed: {e}")
            raise
    
    @staticmethod
    def compute_file_hash(file_path: str) -> str:
        """Compute SHA256 hash"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

s3_service = S3Service()
