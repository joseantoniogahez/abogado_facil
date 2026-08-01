import asyncio
import logging
import tempfile
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from typing import Any

import pytest
from argon2 import PasswordHasher
from starlette.testclient import TestClient

from app.core.authorization import PERMISSION_SPECS
from app.core.db.database import Base, reset_database_runtime
from app.core.setup.dependencies import get_db_session, get_file_storage
from app.features.ai_assistance.models import AIAssistanceResult
from app.features.ai_insights.models import AIResultFeedback
from app.features.ai_jobs.models import AIJob
from app.features.audit_log.models import AuditLogEntry
from app.features.auth.models import Firm, User
from app.features.clients.models import Client
from app.features.matter_calculations.models import MatterCalculation
from app.features.matter_documents.models import MatterDocument
from app.features.matter_notes.models import MatterNote
from app.features.matter_payments.models import MatterBilling, MatterPayment
from app.features.matter_tasks.models import MatterTask
from app.features.matters.models import Matter
from app.features.outbox.models import OutboxEvent
from app.features.rbac.models import Permission, Role, RoleInheritance, RolePermission, UserRole
from app.integrations.files import FileStoragePort
from app.main import app
from utils.testing_support.database import MockDatabase
from utils.testing_support.file_storage import FakeFileStorage
from utils.testing_support.fixtures import load_mock_data


@pytest.fixture(scope="session", autouse=True)
def set_app_http_logger_to_error() -> None:
    logging.getLogger("app.http").setLevel(logging.ERROR)


@pytest.fixture(scope="session", autouse=True)
def database_environment() -> Generator[None]:
    with (
        tempfile.TemporaryDirectory(prefix="backend-tests-runtime-db-") as db_tmp_dir,
        pytest.MonkeyPatch.context() as monkeypatch,
    ):
        monkeypatch.setenv("DB_TYPE", "sqlite+aiosqlite")
        monkeypatch.setenv("DB_NAME", str(Path(db_tmp_dir) / "app.db"))
        for field_name in ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT"):
            monkeypatch.delenv(field_name, raising=False)
        reset_database_runtime()
        yield
        reset_database_runtime()


@pytest.fixture(scope="session", autouse=True)
def object_storage_environment() -> Generator[None]:
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("S3_ENDPOINT_URL", "http://s3.test")
        monkeypatch.setenv("S3_REGION", "test-region")
        monkeypatch.setenv("S3_BUCKET", "test-bucket")
        monkeypatch.setenv("S3_ACCESS_KEY", "test-access-key")
        monkeypatch.setenv("S3_SECRET_KEY", "test-secret-key")
        yield


@pytest.fixture
def fake_file_storage() -> FakeFileStorage:
    return FakeFileStorage()


@pytest.fixture(scope="module")
def mock_users() -> list[dict[str, Any]]:
    password_hasher = PasswordHasher()
    return [
        {
            "id": 1,
            "email": "admin@example.com",
            "first_name": "Ada",
            "middle_name": None,
            "last_name": "Admin",
            "display_name": "Admin User",
            "hashed_password": password_hasher.hash("admin123"),
            "disabled": False,
            "firm_id": 1,
        },
        {
            "id": 2,
            "email": "disabled@example.com",
            "first_name": "Diana",
            "middle_name": "Inactive",
            "last_name": "User",
            "display_name": "Disabled User",
            "hashed_password": password_hasher.hash("admin123"),
            "disabled": True,
            "firm_id": 2,
        },
        {
            "id": 3,
            "email": "reader@example.com",
            "first_name": "Rita",
            "middle_name": None,
            "last_name": "Reader",
            "display_name": "Reader User",
            "hashed_password": password_hasher.hash("reader123"),
            "disabled": False,
            "firm_id": 3,
        },
    ]


@pytest.fixture(scope="module")
def mock_firms() -> list[dict[str, Any]]:
    return [
        {"id": 1, "name": "Admin Legal"},
        {"id": 2, "name": "Disabled Legal"},
        {"id": 3, "name": "Reader Legal"},
    ]


@pytest.fixture(scope="module")
def mock_roles() -> list[dict[str, Any]]:
    return [
        {"id": 1, "name": "admin_role"},
        {"id": 2, "name": "reader_role"},
    ]


@pytest.fixture(scope="module")
def mock_permissions() -> list[dict[str, Any]]:
    return [{"id": permission_id, "name": permission_name} for permission_id, permission_name in PERMISSION_SPECS]


@pytest.fixture(scope="module")
def mock_user_roles() -> list[dict[str, Any]]:
    return [
        {"user_id": 1, "role_id": 1},
        {"user_id": 3, "role_id": 2},
    ]


@pytest.fixture(scope="module")
def mock_role_permissions() -> list[dict[str, Any]]:
    return [{"role_id": 1, "permission_id": permission_id} for permission_id, _ in PERMISSION_SPECS]


@pytest.fixture(scope="module")
def mock_data(
    mock_firms: list[dict[str, Any]],
    mock_users: list[dict[str, Any]],
    mock_roles: list[dict[str, Any]],
    mock_permissions: list[dict[str, Any]],
    mock_user_roles: list[dict[str, Any]],
    mock_role_permissions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {"class": Firm, "json": mock_firms},
        {"class": User, "json": mock_users},
        {"class": Role, "json": mock_roles},
        {"class": Permission, "json": mock_permissions},
        {"class": UserRole, "json": mock_user_roles},
        {"class": RolePermission, "json": mock_role_permissions},
        {"class": RoleInheritance, "json": []},
        {"class": OutboxEvent, "json": []},
        {"class": AuditLogEntry, "json": []},
        {"class": Client, "json": []},
        {"class": Matter, "json": []},
        {"class": MatterNote, "json": []},
        {"class": MatterTask, "json": []},
        {"class": MatterBilling, "json": []},
        {"class": MatterPayment, "json": []},
        {"class": MatterDocument, "json": []},
        {"class": MatterCalculation, "json": []},
        {"class": AIJob, "json": []},
        {"class": AIAssistanceResult, "json": []},
        {"class": AIResultFeedback, "json": []},
    ]


@pytest.fixture(scope="module")
def mock_database(mock_data: list[dict[str, Any]]) -> Generator[MockDatabase]:
    with tempfile.TemporaryDirectory(prefix="backend-tests-db-") as db_tmp_dir:
        mock_db = MockDatabase(path=db_tmp_dir, echo=False)
        asyncio.run(mock_db.setup(Base))
        asyncio.run(load_mock_data(mock_data, mock_db))

        yield mock_db

        asyncio.run(mock_db.close())


@pytest.fixture
def mock_client(
    mock_database: MockDatabase,
    fake_file_storage: FakeFileStorage,
) -> Generator[TestClient]:
    async def override_db_session() -> AsyncGenerator[Any]:
        async with mock_database.Session() as session:
            yield session

    async def override_file_storage() -> FileStoragePort:
        return fake_file_storage

    app.dependency_overrides[get_db_session] = override_db_session
    app.dependency_overrides[get_file_storage] = override_file_storage
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
