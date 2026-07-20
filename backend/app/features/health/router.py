import asyncio
from http import HTTPStatus
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.authorization.dependencies import PublicReadAccessDependency
from app.core.config.settings import ApiSettings
from app.core.setup.dependencies import DbSessionDependency, FileStorageDependency, ObjectStorageSettingsDependency
from app.features.health.openapi import HEALTH_DOC, READINESS_DOC

router = APIRouter(tags=["health"])


@router.get("/health", **HEALTH_DOC)
async def health(_read_access: PublicReadAccessDependency) -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readiness", response_model=None, **READINESS_DOC)
async def readiness(
    _read_access: PublicReadAccessDependency,
    session: DbSessionDependency,
    storage: FileStorageDependency,
    storage_settings: ObjectStorageSettingsDependency,
) -> dict[str, Any] | JSONResponse:
    checks: dict[str, str] = {"database": "unavailable", "object_storage": "unavailable"}
    timeout = ApiSettings().READINESS_TIMEOUT_SECONDS

    async def check_database() -> None:
        await session.execute(text("SELECT 1"))

    async def check_storage() -> None:
        await storage.check(bucket=storage_settings.S3_BUCKET)

    async def run_check(name: str, check: Any) -> None:
        try:
            async with asyncio.timeout(timeout):
                await check()
        except Exception:
            return
        checks[name] = "ok"

    await asyncio.gather(
        run_check("database", check_database),
        run_check("object_storage", check_storage),
    )
    ready = all(value == "ok" for value in checks.values())
    payload = {"status": "ready" if ready else "not_ready", "checks": checks}
    if ready:
        return payload
    return JSONResponse(status_code=HTTPStatus.SERVICE_UNAVAILABLE, content=payload)
