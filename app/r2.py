import boto3
import asyncio
from app.config import settings

def get_r2_client():
    return boto3.client(
        's3',
        endpoint_url=f'https://{settings.r2_account_id}.r2.cloudflarestorage.com',
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name='auto',
    )

async def upload_file(file_bytes: bytes, key: str, content_type: str) -> str:
    """Upload bytes to R2 and return the public URL."""
    def _upload():
        client = get_r2_client()
        import io
        client.upload_fileobj(
            io.BytesIO(file_bytes),
            settings.r2_bucket_name,
            key,
            ExtraArgs={"ContentType": content_type}
        )
    await asyncio.to_thread(_upload)
    return f"{settings.r2_public_base_url}/{key}"
