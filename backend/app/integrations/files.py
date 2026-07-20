from collections.abc import AsyncIterator
from typing import Protocol

from app.core.common.integration import StoredFileResult, StoreFileCommand


class FileStoragePort(Protocol):
    async def check(self, *, bucket: str) -> None: ...

    async def store(self, command: StoreFileCommand) -> StoredFileResult: ...

    async def delete(self, *, bucket: str, path: str) -> bool: ...

    def stream(self, *, bucket: str, path: str) -> AsyncIterator[bytes]: ...


class FileStorageError(RuntimeError):
    """Provider-neutral object storage failure with no credential details."""


class FileNotFoundInStorageError(FileStorageError):
    """Requested object does not exist."""
