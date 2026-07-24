import mimetypes
from pathlib import Path
from uuid import uuid4

import aioboto3
import httpx
from botocore.config import Config
from botocore.exceptions import ClientError
from fastapi import UploadFile
import tempfile

import aiofiles

from app.config import settings


class StorageService:
    _config = Config(
        retries={
            "mode": settings.storage_service_retries_mode,
            "max_attempts": settings.storage_service_retries_attempts
        },
        connect_timeout=settings.storage_service_connection_timeout,
        read_timeout=settings.storage_service_read_timeout,
        max_pool_connections=settings.storage_service_max_pool_connections,
    )

    def __init__(self) -> None:
        self.session = aioboto3.Session()

    def _client(self):
        return self.session.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            config=self._config,
        )

    @staticmethod
    def generate_key(filename: str | None = None, extension: str | None = None, folder: str | None = None) -> str:
        if filename:
            extension = Path(filename).suffix.lower()
        elif extension:
            extension = Path(extension).name
        else:
            raise RuntimeError("No filename or extension provided.")

        key = f"{uuid4().hex}{extension}"

        if folder:
            return f"{folder.rstrip('/')}/{key}"

        return key

    async def upload(self, bucket: str, file: UploadFile, folder: str | None = None) -> str:
        object_key = self.generate_key(filename=file.filename, folder=folder)
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        await file.seek(0)

        async with self._client() as client:
            await client.upload_fileobj(
                Fileobj=file.file, Bucket=bucket, Key=object_key, ExtraArgs={"ContentType": content_type},
            )

        return object_key

    async def download(self, bucket: str, key: str) -> bytes:
        async with self._client() as client:
            response = await client.get_object(Bucket=bucket, Key=key)

            async with response["Body"] as body:
                return await body.read()

    async def delete(self, bucket: str, key: str) -> None:
        async with self._client() as client:
            await client.delete_object(Bucket=bucket, Key=key)

    async def exists(self, bucket: str, key: str) -> bool:
        try:
            async with self._client() as client:
                await client.head_object(Bucket=bucket, Key=key)
                return True

        except ClientError as exc:
            code = exc.response["Error"]["Code"]
            if code in {"404", "NotFound", "NoSuchKey"}:
                return False
            raise

    async def get_presigned_url(self, bucket: str, key: str, expires_in: int = 3600) -> str:

        async with self._client() as client:
            return await client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expires_in,
            )

    def get_public_url(self, bucket: str, key: str) -> str:
        if not settings.S3_PUBLIC_URL:
            raise RuntimeError("S3_PUBLIC_URL is not configured.")

        return f"{settings.S3_PUBLIC_URL}/{bucket}/{key}"

    async def upload_from_url(
            self, bucket: str, url: str, folder: str | None = None, default_extension: str | None = None
    ) -> str:

        async with httpx.AsyncClient(follow_redirects=True, timeout=60) as http_client:
            async with http_client.stream("GET", url) as response:
                response.raise_for_status()

                content_type = response.headers.get("Content-Type") or "application/octet-stream"
                extension = mimetypes.guess_extension(content_type) or default_extension or ""
                object_key = self.generate_key(extension=extension, folder=folder)

                with tempfile.NamedTemporaryFile(mode="w+b") as tmp:
                    async with aiofiles.open(tmp.name, "wb") as f:
                        async for chunk in response.aiter_bytes():
                            await f.write(chunk)

                    tmp.seek(0)

                    async with self._client() as s3_client:
                        await s3_client.upload_fileobj(
                            Fileobj=tmp,
                            Bucket=bucket,
                            Key=object_key,
                            ExtraArgs={"ContentType": content_type},
                        )

        return object_key
