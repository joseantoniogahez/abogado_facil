import asyncio
from io import BytesIO
from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError, EndpointConnectionError

from app.core.common.integration import StoreFileCommand
from app.core.config.settings import ObjectStorageSettings
from app.integrations.files import FileNotFoundInStorageError, FileStorageError
from app.integrations.s3 import S3FileStorage
from utils.testing_support.file_storage import FakeFileStorage


def _command(body: bytes = b"legal-document") -> StoreFileCommand:
    return StoreFileCommand(bucket="documents", path="matters/1/file.pdf", content_type="application/pdf", body=body)


async def _collect(storage: object, *, bucket: str = "documents", path: str = "matters/1/file.pdf") -> bytes:
    chunks = [chunk async for chunk in storage.stream(bucket=bucket, path=path)]  # type: ignore[attr-defined]
    return b"".join(chunks)


def _client_error(code: str, operation: str) -> ClientError:
    return ClientError({"Error": {"Code": code, "Message": "provider detail"}}, operation)


def test_fake_storage_put_stream_delete_contract() -> None:
    async def run() -> None:
        storage = FakeFileStorage()
        result = await storage.store(_command())

        assert result.bucket == "documents"
        assert result.etag
        assert await _collect(storage) == b"legal-document"
        assert await storage.delete(bucket="documents", path="matters/1/file.pdf") is True
        assert await storage.delete(bucket="documents", path="matters/1/file.pdf") is False
        with pytest.raises(FileNotFoundInStorageError, match="Object not found"):
            await _collect(storage)

    asyncio.run(run())


def test_s3_storage_put_stream_delete_contract() -> None:
    async def run() -> None:
        client = MagicMock()
        client.put_object.return_value = {"ETag": '"etag"'}
        client.get_object.return_value = {"Body": BytesIO(b"stored-bytes")}
        storage = S3FileStorage(ObjectStorageSettings(), client=client)

        await storage.check(bucket="documents")
        result = await storage.store(_command())
        assert result.etag == '"etag"'
        assert await _collect(storage) == b"stored-bytes"
        assert await storage.delete(bucket="documents", path="matters/1/file.pdf") is True

        client.put_object.assert_called_once()
        client.get_object.assert_called_once_with(Bucket="documents", Key="matters/1/file.pdf")
        client.head_object.assert_called_once_with(Bucket="documents", Key="matters/1/file.pdf")
        client.delete_object.assert_called_once_with(Bucket="documents", Key="matters/1/file.pdf")

    asyncio.run(run())


def test_s3_storage_translates_not_found_and_provider_failures() -> None:
    async def run() -> None:
        client = MagicMock()
        storage = S3FileStorage(ObjectStorageSettings(), client=client)

        client.get_object.side_effect = _client_error("NoSuchKey", "GetObject")
        with pytest.raises(FileNotFoundInStorageError, match="Object not found"):
            await _collect(storage)

        client.get_object.side_effect = _client_error("AccessDenied", "GetObject")
        with pytest.raises(FileStorageError, match="read failed") as exc_info:
            await _collect(storage)
        assert "provider detail" not in str(exc_info.value)

        client.get_object.side_effect = EndpointConnectionError(endpoint_url="secret-host")
        with pytest.raises(FileStorageError, match="read failed"):
            await _collect(storage)

        client.put_object.side_effect = EndpointConnectionError(endpoint_url="secret-host")
        with pytest.raises(FileStorageError, match="write failed") as exc_info:
            await storage.store(_command())
        assert "secret-host" not in str(exc_info.value)

        client.head_bucket.side_effect = _client_error("AccessDenied", "HeadBucket")
        with pytest.raises(FileStorageError, match="health check failed") as exc_info:
            await storage.check(bucket="documents")
        assert "provider detail" not in str(exc_info.value)

        client.head_object.side_effect = _client_error("404", "HeadObject")
        assert await storage.delete(bucket="documents", path="missing") is False

        client.head_object.side_effect = _client_error("AccessDenied", "HeadObject")
        with pytest.raises(FileStorageError, match="delete failed"):
            await storage.delete(bucket="documents", path="denied")

    asyncio.run(run())


def test_s3_storage_translates_stream_and_delete_failures() -> None:
    class FailingBody:
        def read(self, size: int) -> bytes:
            raise OSError("secret stream detail")

        def close(self) -> None:
            self.closed = True

    async def run() -> None:
        client = MagicMock()
        body = FailingBody()
        client.get_object.return_value = {"Body": body}
        storage = S3FileStorage(ObjectStorageSettings(), client=client)

        with pytest.raises(FileStorageError, match="stream failed"):
            await _collect(storage)
        assert body.closed is True

        client.head_object.side_effect = EndpointConnectionError(endpoint_url="secret-host")
        with pytest.raises(FileStorageError, match="delete failed"):
            await storage.delete(bucket="documents", path="file")

        client.head_object.side_effect = None
        client.delete_object.side_effect = _client_error("AccessDenied", "DeleteObject")
        with pytest.raises(FileStorageError, match="delete failed"):
            await storage.delete(bucket="documents", path="file")

    asyncio.run(run())
