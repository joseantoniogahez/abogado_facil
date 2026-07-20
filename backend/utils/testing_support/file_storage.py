from collections.abc import AsyncIterator
from hashlib import md5

from app.core.common.integration import StoredFileResult, StoreFileCommand
from app.integrations.files import FileNotFoundInStorageError


class FakeFileStorage:
    def __init__(self) -> None:
        self.objects: dict[tuple[str, str], bytes] = {}

    async def check(self, *, bucket: str) -> None:
        return None

    async def store(self, command: StoreFileCommand) -> StoredFileResult:
        body = command.body if isinstance(command.body, bytes) else command.body.read()
        self.objects[(command.bucket, command.path)] = body
        etag = md5(body, usedforsecurity=False).hexdigest()
        return StoredFileResult(bucket=command.bucket, path=command.path, etag=etag)

    async def stream(self, *, bucket: str, path: str) -> AsyncIterator[bytes]:
        try:
            body = self.objects[(bucket, path)]
        except KeyError as exc:
            raise FileNotFoundInStorageError("Object not found.") from exc
        yield body

    async def delete(self, *, bucket: str, path: str) -> bool:
        return self.objects.pop((bucket, path), None) is not None
