import asyncio
import zipfile
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import UploadFile

from app.core.config.settings import MatterDocumentSettings, ObjectStorageSettings
from app.core.errors.services import ConflictError, InternalError, InvalidInputError, NotFoundError
from app.features.auth.principal import CurrentPrincipal
from app.features.matter_documents.repository import MatterDocumentsRepository
from app.features.matter_documents.router import _firm_id
from app.features.matter_documents.schemas.api import DocumentType
from app.features.matter_documents.service import MatterDocumentsService
from app.integrations.files import FileStorageError


def _uow() -> MagicMock:
    unit = MagicMock()
    unit.__aenter__ = AsyncMock()
    unit.__aexit__ = AsyncMock(return_value=False)
    return unit


def _service(*, max_size: int = 100, max_count: int = 50):
    repository, matters, storage = AsyncMock(), AsyncMock(), AsyncMock()
    matters.get_for_firm.return_value = object()
    repository.count_for_matter.return_value = 0
    return (
        MatterDocumentsService(
            repository,
            matters,
            _uow(),
            storage,
            ObjectStorageSettings(),
            MatterDocumentSettings(
                MATTER_DOCUMENT_MAX_SIZE_BYTES=max_size,
                MATTER_DOCUMENT_MAX_PER_MATTER=max_count,
            ),
        ),
        repository,
        matters,
        storage,
    )


def _upload(name: str | None, body: bytes) -> UploadFile:
    return UploadFile(filename=name, file=BytesIO(body))


def _docx(*, complete: bool = True) -> bytes:
    output = BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("[Content_Types].xml", "types")
        if complete:
            archive.writestr("word/document.xml", "document")
    return output.getvalue()


def test_spooling_validates_supported_file_content_and_limits() -> None:
    async def run() -> None:
        service, _, _, _ = _service(max_size=20)
        for upload, message in (
            (_upload("bad.exe", b"x"), "Only PDF"),
            (_upload("empty.txt", b""), "cannot be empty"),
            (_upload("large.txt", b"x" * 21), "size limit"),
            (_upload("bad.docx", b"not zip"), "does not match DOCX"),
            (_upload("null.txt", b"a\x00b"), "null bytes"),
            (_upload("binary.txt", b"\xff"), "UTF-8"),
        ):
            with pytest.raises(InvalidInputError, match=message):
                await service._spool(upload)

        docx_service, _, _, _ = _service(max_size=1000)
        with pytest.raises(InvalidInputError, match="does not match DOCX"):
            await docx_service._spool(_upload("incomplete.docx", _docx(complete=False)))
        body, size, filename, media_type = await docx_service._spool(_upload("valid.docx", _docx()))
        assert size > 0 and filename == "valid.docx"
        assert media_type.endswith("wordprocessingml.document")
        body.close()
        assert service._filename(None) == "document"
        assert service._filename("... ") == "document"

    asyncio.run(run())


def test_service_reports_scope_quota_and_storage_failures() -> None:
    async def run() -> None:
        service, repository, matters, storage = _service()
        matters.get_for_firm.return_value = None
        with pytest.raises(NotFoundError, match="Matter not found"):
            await service.list(firm_id=1, matter_id=2)

        matters.get_for_firm.return_value = object()
        repository.count_for_matter.return_value = 50
        with pytest.raises(ConflictError, match="limit reached"):
            await service.upload(
                firm_id=1, matter_id=2, document_type=DocumentType.OTHER, file=_upload("ok.txt", b"ok")
            )

        repository.count_for_matter.return_value = 0
        storage.store.side_effect = FileStorageError("provider secret")
        with pytest.raises(InternalError, match="storage operation failed"):
            await service.upload(
                firm_id=1, matter_id=2, document_type=DocumentType.OTHER, file=_upload("ok.txt", b"ok")
            )

        repository.get_for_matter.return_value = None
        with pytest.raises(NotFoundError, match="document not found"):
            await service.download(firm_id=1, matter_id=2, document_id="missing")

        repository.get_for_matter.return_value = SimpleNamespace(id="doc", storage_key="private")
        storage.delete.side_effect = FileStorageError("provider secret")
        with pytest.raises(InternalError, match="storage operation failed"):
            await service.delete(firm_id=1, matter_id=2, document_id="doc")

    asyncio.run(run())


def test_upload_compensates_when_metadata_write_fails() -> None:
    async def run() -> None:
        service, repository, _, storage = _service()
        repository.create.side_effect = RuntimeError("db failed")
        with pytest.raises(RuntimeError, match="db failed"):
            await service.upload(
                firm_id=1, matter_id=2, document_type=DocumentType.RECORD, file=_upload("ok.pdf", b"%PDF-1")
            )
        storage.delete.assert_awaited_once()

    asyncio.run(run())


def test_document_router_requires_a_firm() -> None:
    principal = CurrentPrincipal(
        id=1,
        email="none@example.com",
        first_name="N",
        last_name="O",
        display_name="N O",
        disabled=False,
        firm_id=None,
    )
    with pytest.raises(ValueError, match="must belong to a firm"):
        _firm_id(principal)


def test_repository_quota_lock_is_postgresql_only() -> None:
    async def run() -> None:
        session = MagicMock()
        session.execute = AsyncMock()
        session.get_bind.return_value.dialect.name = "sqlite"
        repository = MatterDocumentsRepository(session)
        await repository.lock_quota(firm_id=1, matter_id=2)
        session.execute.assert_not_awaited()

        session.get_bind.return_value.dialect.name = "postgresql"
        await repository.lock_quota(firm_id=1, matter_id=2)
        statement, parameters = session.execute.await_args.args
        assert "pg_advisory_xact_lock" in str(statement)
        assert parameters == {"lock_key": (1 << 32) | 2}

    asyncio.run(run())
