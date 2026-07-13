import asyncio
from collections.abc import AsyncIterator
from typing import Any

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from app.core.common.integration import StoredFileResult, StoreFileCommand
from app.core.config.settings import ObjectStorageSettings
from app.integrations.files import FileNotFoundInStorageError, FileStorageError


class S3FileStorage:
    def __init__(self, settings: ObjectStorageSettings | None = None, *, client: Any | None = None) -> None:
        self.settings = settings or ObjectStorageSettings()
        self._client = client or boto3.client(
            "s3",
            endpoint_url=self.settings.S3_ENDPOINT_URL,
            region_name=self.settings.S3_REGION,
            aws_access_key_id=self.settings.S3_ACCESS_KEY,
            aws_secret_access_key=self.settings.S3_SECRET_KEY.get_secret_value(),
            config=Config(
                connect_timeout=self.settings.S3_CONNECT_TIMEOUT_SECONDS,
                read_timeout=self.settings.S3_READ_TIMEOUT_SECONDS,
                retries={"max_attempts": 2, "mode": "standard"},
                s3={"addressing_style": "path" if self.settings.S3_PATH_STYLE else "virtual"},
            ),
        )

    async def store(self, command: StoreFileCommand) -> StoredFileResult:
        try:
            response = await asyncio.to_thread(
                self._client.put_object,
                Bucket=command.bucket,
                Key=command.path,
                Body=command.body,
                ContentType=command.content_type,
            )
        except (BotoCoreError, ClientError) as exc:
            raise FileStorageError("Object storage write failed.") from exc
        return StoredFileResult(bucket=command.bucket, path=command.path, etag=response.get("ETag"))

    async def stream(self, *, bucket: str, path: str) -> AsyncIterator[bytes]:
        try:
            response = await asyncio.to_thread(self._client.get_object, Bucket=bucket, Key=path)
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in {"NoSuchKey", "404", "NotFound"}:
                raise FileNotFoundInStorageError("Object not found.") from exc
            raise FileStorageError("Object storage read failed.") from exc
        except BotoCoreError as exc:
            raise FileStorageError("Object storage read failed.") from exc

        body = response["Body"]
        try:
            while chunk := await asyncio.to_thread(body.read, 64 * 1024):
                yield chunk
        except (BotoCoreError, ClientError, OSError) as exc:
            raise FileStorageError("Object storage stream failed.") from exc
        finally:
            body.close()

    async def delete(self, *, bucket: str, path: str) -> bool:
        try:
            await asyncio.to_thread(self._client.head_object, Bucket=bucket, Key=path)
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in {"NoSuchKey", "404", "NotFound"}:
                return False
            raise FileStorageError("Object storage delete failed.") from exc
        except BotoCoreError as exc:
            raise FileStorageError("Object storage delete failed.") from exc
        try:
            await asyncio.to_thread(self._client.delete_object, Bucket=bucket, Key=path)
        except (BotoCoreError, ClientError) as exc:
            raise FileStorageError("Object storage delete failed.") from exc
        return True
