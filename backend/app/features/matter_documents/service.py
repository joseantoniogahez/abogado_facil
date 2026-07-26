import logging
import re
import tempfile
import uuid
import zipfile
from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import BinaryIO, Protocol, cast

from fastapi import UploadFile

from app.core.common.integration import StoreFileCommand
from app.core.config.settings import MatterDocumentSettings, ObjectStorageSettings
from app.core.db.ports import UnitOfWorkPort
from app.core.errors.services import ConflictError, InternalError, InvalidInputError, NotFoundError
from app.features.matter_documents.models import MatterDocument
from app.features.matter_documents.repository import MatterDocumentsRepository
from app.features.matter_documents.schemas.api import DocumentType
from app.integrations.files import FileStorageError, FileStoragePort
from app.integrations.pdf_text import PdfTextExtractionError, PdfTextExtractorPort

logger = logging.getLogger("app.matter_documents")
_CHUNK_SIZE = 64 * 1024
_MEDIA_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".txt": "text/plain",
}


class MatterLookupPort(Protocol):
    async def get_for_firm(self, *, matter_id: int, firm_id: int): ...


class MatterDocumentsServicePort(Protocol):
    async def upload(
        self, *, firm_id: int, matter_id: int, document_type: DocumentType, file: UploadFile
    ) -> MatterDocument: ...
    async def list(self, *, firm_id: int, matter_id: int) -> tuple[list[MatterDocument], int]: ...
    async def download(
        self, *, firm_id: int, matter_id: int, document_id: str
    ) -> tuple[MatterDocument, AsyncIterator[bytes]]: ...
    async def delete(self, *, firm_id: int, matter_id: int, document_id: str) -> None: ...


class MatterDocumentsService:
    def __init__(
        self,
        repository: MatterDocumentsRepository,
        matters_repository: MatterLookupPort,
        unit_of_work: UnitOfWorkPort,
        storage: FileStoragePort,
        storage_settings: ObjectStorageSettings,
        settings: MatterDocumentSettings,
        pdf_text_extractor: PdfTextExtractorPort,
    ):
        self.repository = repository
        self.matters_repository = matters_repository
        self.unit_of_work = unit_of_work
        self.storage = storage
        self.bucket = storage_settings.S3_BUCKET
        self.settings = settings
        self.pdf_text_extractor = pdf_text_extractor

    def _extract_text(self, body: BinaryIO, media_type: str) -> tuple[str, str | None]:
        if media_type != "application/pdf":
            return "not_applicable", None
        try:
            extracted_text = self.pdf_text_extractor.extract(body)
        except PdfTextExtractionError:
            logger.warning("event=matter_document_text_extraction_failed")
            return "failed", None
        if not extracted_text:
            return "empty", None
        return "available", extracted_text

    async def _require_matter(self, *, firm_id: int, matter_id: int) -> None:
        if await self.matters_repository.get_for_firm(matter_id=matter_id, firm_id=firm_id) is None:
            raise NotFoundError("Matter not found")

    async def _require_document(self, *, firm_id: int, matter_id: int, document_id: str) -> MatterDocument:
        document = await self.repository.get_for_matter(document_id=document_id, matter_id=matter_id, firm_id=firm_id)
        if document is None:
            raise NotFoundError("Matter document not found")
        return document

    @staticmethod
    def _filename(value: str | None) -> str:
        name = Path(value or "document").name
        name = re.sub(r"[^\w.() -]", "_", name, flags=re.UNICODE).strip(" .")
        return (name or "document")[:255]

    @asynccontextmanager
    async def _spool(self, file: UploadFile) -> AsyncGenerator[tuple[BinaryIO, int, str, str]]:
        filename = self._filename(file.filename)
        suffix = Path(filename).suffix.lower()
        media_type = _MEDIA_TYPES.get(suffix)
        if media_type is None:
            raise InvalidInputError("Only PDF, DOCX and TXT files are supported")
        with tempfile.SpooledTemporaryFile(
            max_size=min(self.settings.MATTER_DOCUMENT_MAX_SIZE_BYTES, 1024 * 1024)
        ) as temporary_file:
            spool = cast(BinaryIO, temporary_file)
            size = 0
            while chunk := await file.read(_CHUNK_SIZE):
                size += len(chunk)
                if size > self.settings.MATTER_DOCUMENT_MAX_SIZE_BYTES:
                    raise InvalidInputError("File exceeds the configured size limit")
                spool.write(chunk)
            if size == 0:
                raise InvalidInputError("File cannot be empty")
            spool.seek(0)
            self._validate_content(spool, suffix)
            spool.seek(0)
            yield spool, size, filename, media_type

    @staticmethod
    def _validate_content(body: BinaryIO, suffix: str) -> None:
        if suffix == ".pdf" and body.read(5) != b"%PDF-":
            raise InvalidInputError("File content does not match PDF")
        if suffix == ".docx":
            try:
                with zipfile.ZipFile(body) as archive:
                    if "[Content_Types].xml" not in archive.namelist() or "word/document.xml" not in archive.namelist():
                        raise InvalidInputError("File content does not match DOCX")
            except zipfile.BadZipFile as exc:
                raise InvalidInputError("File content does not match DOCX") from exc
        if suffix == ".txt":
            try:
                for chunk in iter(lambda: body.read(_CHUNK_SIZE), b""):
                    if b"\x00" in chunk:
                        raise InvalidInputError("TXT files cannot contain null bytes")
                    chunk.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise InvalidInputError("TXT files must use UTF-8") from exc

    async def upload(
        self, *, firm_id: int, matter_id: int, document_type: DocumentType, file: UploadFile
    ) -> MatterDocument:
        async with self._spool(file) as (body, size, filename, media_type):
            text_extraction_status, extracted_text = self._extract_text(body, media_type)
            document_id = str(uuid.uuid4())
            storage_key = f"firms/{firm_id}/matters/{matter_id}/{document_id}"
            stored = False
            try:
                async with self.unit_of_work:
                    await self._require_matter(firm_id=firm_id, matter_id=matter_id)
                    await self.repository.lock_quota(firm_id=firm_id, matter_id=matter_id)
                    if (
                        await self.repository.count_for_matter(matter_id=matter_id, firm_id=firm_id)
                        >= self.settings.MATTER_DOCUMENT_MAX_PER_MATTER
                    ):
                        raise ConflictError("Matter document limit reached")
                    await self.storage.store(
                        StoreFileCommand(
                            bucket=self.bucket,
                            path=storage_key,
                            content_type=media_type,
                            body=body,
                        )
                    )
                    stored = True
                    return await self.repository.create(
                        id=document_id,
                        firm_id=firm_id,
                        matter_id=matter_id,
                        original_filename=filename,
                        document_type=document_type.value,
                        media_type=media_type,
                        size_bytes=size,
                        storage_key=storage_key,
                        text_extraction_status=text_extraction_status,
                        extracted_text=extracted_text,
                    )
            except Exception as exc:
                if stored:
                    await self.storage.delete(bucket=self.bucket, path=storage_key)
                if isinstance(exc, FileStorageError):
                    raise InternalError("Document storage operation failed") from exc
                raise

    async def list(self, *, firm_id: int, matter_id: int) -> tuple[list[MatterDocument], int]:
        await self._require_matter(firm_id=firm_id, matter_id=matter_id)
        return (
            await self.repository.list_for_matter(matter_id=matter_id, firm_id=firm_id),
            await self.repository.count_for_matter(matter_id=matter_id, firm_id=firm_id),
        )

    async def download(
        self, *, firm_id: int, matter_id: int, document_id: str
    ) -> tuple[MatterDocument, AsyncIterator[bytes]]:
        document = await self._require_document(firm_id=firm_id, matter_id=matter_id, document_id=document_id)
        return document, self.storage.stream(bucket=self.bucket, path=document.storage_key)

    async def delete(self, *, firm_id: int, matter_id: int, document_id: str) -> None:
        document = await self._require_document(firm_id=firm_id, matter_id=matter_id, document_id=document_id)
        try:
            await self.storage.delete(bucket=self.bucket, path=document.storage_key)
        except FileStorageError as exc:
            raise InternalError("Document storage operation failed") from exc
        async with self.unit_of_work:
            await self.repository.delete(document.id)
