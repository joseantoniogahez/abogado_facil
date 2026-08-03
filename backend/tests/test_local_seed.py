import asyncio
import json
import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError
from sqlalchemy import func, select

from app.core.common.matter_types import MatterType
from app.core.db import local_seed
from app.core.db.database import Base
from app.core.db.local_seed import (
    LocalSeedFixture,
    LocalSeedReport,
    load_fixture,
    require_local_environment,
    seed_local_data,
)
from app.features.auth.models import Firm, User
from app.features.clients.models import Client
from app.features.matter_notes.models import MatterNote
from app.features.matters.models import Matter
from utils.testing_support.database import MockDatabase


async def _count(session, model: type[object]) -> int:
    return int(await session.scalar(select(func.count()).select_from(model)))


def test_local_seed_is_complete_idempotent_and_resettable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "local")

    async def run_test() -> None:
        with tempfile.TemporaryDirectory(prefix="backend-local-seed-") as db_tmp_dir:
            database = MockDatabase(path=db_tmp_dir, echo=False)
            await database.setup(Base)
            try:
                fixture = load_fixture()
                first = await seed_local_data(database.Session, fixture=fixture)
                second = await seed_local_data(database.Session, fixture=fixture)

                assert first.users == second.users == 2
                assert first.firms == second.firms == 2
                assert first.clients == second.clients == 4
                assert first.matters == second.matters == 32

                async with database.Session() as session, session.begin():
                    assert await _count(session, Firm) == 2
                    assert await _count(session, User) == 2
                    assert await _count(session, Client) == 4
                    assert await _count(session, Matter) == 32
                    clients = (await session.scalars(select(Client))).all()
                    for client in clients:
                        matters = (await session.scalars(select(Matter).where(Matter.client_id == client.id))).all()
                        assert {matter.matter_type for matter in matters} == {item.value for item in MatterType}
                    first_matter = await session.scalar(select(Matter).limit(1))
                    assert first_matter is not None
                    session.add(
                        MatterNote(firm_id=first_matter.firm_id, matter_id=first_matter.id, content="temporary")
                    )

                reset_report = await seed_local_data(database.Session, fixture=fixture, reset=True)
                assert reset_report.reset is True
                async with database.Session() as session:
                    assert await _count(session, MatterNote) == 0
                    assert await _count(session, User) == 2
                    assert await _count(session, Client) == 4
                    assert await _count(session, Matter) == 32
            finally:
                await database.close()

    asyncio.run(run_test())


@pytest.mark.parametrize("app_env", ["test", "staging", "prod", "production"])
def test_local_seed_rejects_non_local_environments(monkeypatch: pytest.MonkeyPatch, app_env: str) -> None:
    monkeypatch.setenv("APP_ENV", app_env)
    with pytest.raises(ValueError, match="APP_ENV=local"):
        require_local_environment()


def test_fixture_validation_happens_before_persistence(tmp_path: Path) -> None:
    payload = json.loads(Path("backend/app/core/db/local_seed.json").read_text(encoding="utf-8"))
    payload["matter_templates"].pop()
    fixture_path = tmp_path / "invalid.json"
    fixture_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValidationError, match="canonical catalog"):
        load_fixture(fixture_path)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda payload: payload["users"][1].update(email=payload["users"][0]["email"]), "user emails"),
        (lambda payload: payload["users"][1].update(firm_name=payload["users"][0]["firm_name"]), "firm names"),
        (
            lambda payload: payload["users"][1]["clients"][0].update(email=payload["users"][0]["clients"][0]["email"]),
            "client emails",
        ),
        (lambda payload: payload["users"][0].update(email="invalid"), "valid local fixture address"),
        (lambda payload: payload["users"][0]["clients"][0].update(email="invalid"), "valid local fixture address"),
    ],
)
def test_fixture_rejects_duplicate_and_invalid_identifiers(mutation, message: str) -> None:
    payload = json.loads(Path("backend/app/core/db/local_seed.json").read_text(encoding="utf-8"))
    mutation(payload)
    with pytest.raises(ValidationError, match=message):
        LocalSeedFixture.model_validate(payload)


def test_load_fixture_wraps_file_errors(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Could not load local seed fixture"):
        load_fixture(tmp_path / "missing.json")


def test_main_formats_success_and_handles_validation_error(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    monkeypatch.setattr("sys.argv", ["local_seed", "--reset"])
    monkeypatch.setattr(local_seed, "require_local_environment", lambda: None)
    monkeypatch.setattr(local_seed, "load_fixture", lambda path: load_fixture())

    async def successful_seed(*args, **kwargs) -> LocalSeedReport:
        return LocalSeedReport(users=2, firms=2, clients=4, matters=32, reset=True)

    monkeypatch.setattr(local_seed, "seed_local_data", successful_seed)
    assert local_seed.main() == 0
    assert "matters: 32" in capsys.readouterr().out

    monkeypatch.setattr(local_seed, "require_local_environment", lambda: (_ for _ in ()).throw(ValueError("blocked")))
    assert local_seed.main() == 1
    assert "Local seed failed: blocked" in capsys.readouterr().err
