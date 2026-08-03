from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.common.matter_types import MatterType
from app.core.db.database import Base, get_async_session_factory
from app.core.security.service import Argon2PasswordService
from app.features.ai_assistance.models import AIAssistanceResult  # noqa: F401
from app.features.ai_credentials.models import AiCredential  # noqa: F401
from app.features.ai_insights.models import AIResultFeedback  # noqa: F401
from app.features.ai_jobs.models import AIJob  # noqa: F401
from app.features.audit_log.models import AuditLogEntry  # noqa: F401
from app.features.auth.models import Firm, User
from app.features.clients.models import Client
from app.features.matter_calculations.models import MatterCalculation  # noqa: F401
from app.features.matter_checklists.models import MatterChecklistItem  # noqa: F401
from app.features.matter_documents.models import MatterDocument  # noqa: F401
from app.features.matter_notes.models import MatterNote  # noqa: F401
from app.features.matter_payments.models import MatterBilling, MatterPayment  # noqa: F401
from app.features.matter_tasks.models import MatterTask  # noqa: F401
from app.features.matters.models import Matter
from app.features.outbox.models import OutboxEvent  # noqa: F401
from app.features.rbac.models import Role, UserRole

FIXTURE_PATH = Path(__file__).with_name("local_seed.json")
PRESERVED_RESET_TABLES = {"permissions", "roles", "role_permissions", "role_inheritances"}


class MatterTemplate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    matter_type: MatterType
    title_suffix: str = Field(min_length=1, max_length=255)
    status: str = Field(pattern="^(active|pending|closed)$")
    counterparty: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    next_action: str = Field(min_length=1, max_length=500)
    next_action_date: date


class ClientFixture(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str = Field(min_length=1, max_length=255)
    phone_country_code: str = Field(pattern="^52$")
    phone: str = Field(pattern="^[0-9]{10}$")
    email: str = Field(min_length=3, max_length=320)
    address: str = Field(min_length=1)
    notes: str = Field(min_length=1)
    matter_title_prefix: str = Field(min_length=1, max_length=200)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if value.count("@") != 1 or "." not in value.rsplit("@", 1)[1]:
            raise ValueError("email must be a valid local fixture address")
        return value.lower()


class UserFixture(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: str = Field(min_length=3, max_length=320)
    login_phrase: str = Field(min_length=8, max_length=255)
    first_name: str = Field(min_length=1, max_length=100)
    middle_name: str | None = Field(max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    display_name: str = Field(min_length=1, max_length=255)
    disabled: bool
    firm_name: str = Field(min_length=1, max_length=255)
    clients: list[ClientFixture] = Field(min_length=2, max_length=2)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if value.count("@") != 1 or "." not in value.rsplit("@", 1)[1]:
            raise ValueError("email must be a valid local fixture address")
        return value.lower()


class LocalSeedFixture(BaseModel):
    users: list[UserFixture] = Field(min_length=2, max_length=2)
    matter_templates: list[MatterTemplate]

    @model_validator(mode="after")
    def validate_dataset_contract(self) -> LocalSeedFixture:
        expected_types = set(MatterType)
        actual_types = {template.matter_type for template in self.matter_templates}
        if len(self.matter_templates) != len(expected_types) or actual_types != expected_types:
            missing = sorted(item.value for item in expected_types - actual_types)
            extra = sorted(item.value for item in actual_types - expected_types)
            raise ValueError(f"matter_templates must match the canonical catalog; missing={missing}, extra={extra}")

        user_emails = [str(user.email).lower() for user in self.users]
        firm_names = [user.firm_name for user in self.users]
        client_emails = [str(client.email).lower() for user in self.users for client in user.clients]
        if len(set(user_emails)) != len(user_emails):
            raise ValueError("user emails must be unique")
        if len(set(firm_names)) != len(firm_names):
            raise ValueError("firm names must be unique")
        if len(set(client_emails)) != len(client_emails):
            raise ValueError("client emails must be unique")
        return self


@dataclass(frozen=True)
class LocalSeedReport:
    users: int
    firms: int
    clients: int
    matters: int
    reset: bool


def require_local_environment() -> None:
    if os.getenv("APP_ENV", "local").strip().lower() != "local":
        raise ValueError("Local seed is disabled unless APP_ENV=local.")


def load_fixture(path: Path = FIXTURE_PATH) -> LocalSeedFixture:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not load local seed fixture {path}: {exc}") from exc
    return LocalSeedFixture.model_validate(payload)


async def _reset_application_data(session: AsyncSession) -> None:
    # Models are registered by imports throughout the application before this utility runs.
    for table in reversed(Base.metadata.sorted_tables):
        if table.name not in PRESERVED_RESET_TABLES:
            await session.execute(delete(table))


async def _get_or_create_firm(session: AsyncSession, name: str) -> Firm:
    firm = await session.scalar(select(Firm).where(Firm.name == name).limit(1))
    if firm is None:
        firm = Firm(name=name)
        session.add(firm)
        await session.flush()
    return firm


async def _upsert_user(session: AsyncSession, fixture: UserFixture, firm: Firm) -> User:
    email = str(fixture.email).lower()
    user = await session.scalar(select(User).where(User.email == email).limit(1))
    if user is None:
        user = User(email=email, hashed_password="pending")
        session.add(user)
    user.hashed_password = Argon2PasswordService().hash_password(fixture.login_phrase)
    user.first_name = fixture.first_name
    user.middle_name = fixture.middle_name
    user.last_name = fixture.last_name
    user.display_name = fixture.display_name
    user.disabled = fixture.disabled
    user.firm_id = firm.id
    await session.flush()
    return user


async def _ensure_account_owner(session: AsyncSession, user: User) -> None:
    role = await session.scalar(select(Role).where(Role.name == "account_owner").limit(1))
    if role is None:
        role = Role(name="account_owner")
        session.add(role)
        await session.flush()
    assignment = await session.scalar(
        select(UserRole).where(UserRole.user_id == user.id, UserRole.role_id == role.id).limit(1)
    )
    if assignment is None:
        session.add(UserRole(user_id=user.id, role_id=role.id))


async def _upsert_client(session: AsyncSession, fixture: ClientFixture, firm: Firm) -> Client:
    email = str(fixture.email).lower()
    client = await session.scalar(select(Client).where(Client.firm_id == firm.id, Client.email == email).limit(1))
    if client is None:
        client = Client(firm_id=firm.id, email=email)
        session.add(client)
    client.full_name = fixture.full_name
    client.phone_country_code = fixture.phone_country_code
    client.phone = fixture.phone
    client.address = fixture.address
    client.notes = fixture.notes
    await session.flush()
    return client


async def _upsert_matter(
    session: AsyncSession,
    *,
    client: Client,
    firm: Firm,
    client_fixture: ClientFixture,
    template: MatterTemplate,
) -> None:
    title = f"{client_fixture.matter_title_prefix} — {template.title_suffix}"
    matter = await session.scalar(
        select(Matter)
        .where(
            Matter.firm_id == firm.id,
            Matter.client_id == client.id,
            Matter.matter_type == template.matter_type.value,
        )
        .limit(1)
    )
    if matter is None:
        matter = Matter(firm_id=firm.id, client_id=client.id, matter_type=template.matter_type.value, title=title)
        session.add(matter)
    matter.title = title
    matter.status = template.status
    matter.counterparty = template.counterparty
    matter.description = template.description
    matter.next_action = template.next_action
    matter.next_action_date = template.next_action_date


async def seed_local_data(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    fixture: LocalSeedFixture,
    reset: bool = False,
) -> LocalSeedReport:
    require_local_environment()
    async with session_factory() as session, session.begin():
        if reset:
            await _reset_application_data(session)

        for user_fixture in fixture.users:
            firm = await _get_or_create_firm(session, user_fixture.firm_name)
            user = await _upsert_user(session, user_fixture, firm)
            await _ensure_account_owner(session, user)
            for client_fixture in user_fixture.clients:
                client = await _upsert_client(session, client_fixture, firm)
                for template in fixture.matter_templates:
                    await _upsert_matter(
                        session,
                        client=client,
                        firm=firm,
                        client_fixture=client_fixture,
                        template=template,
                    )

    return LocalSeedReport(users=2, firms=2, clients=4, matters=32, reset=reset)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create deterministic local-only demo data.")
    parser.add_argument("--reset", action="store_true", help="Delete local application data before seeding.")
    parser.add_argument("--fixture", type=Path, default=FIXTURE_PATH, help=argparse.SUPPRESS)
    return parser


def _format_report(report: LocalSeedReport) -> str:
    return (
        "Local seed completed.\n"
        f"- reset: {report.reset}\n- firms: {report.firms}\n- users: {report.users}\n"
        f"- clients: {report.clients}\n- matters: {report.matters}"
    )


def main() -> int:
    args = _build_parser().parse_args()
    try:
        require_local_environment()
        fixture = load_fixture(args.fixture)
        report = asyncio.run(seed_local_data(get_async_session_factory(), fixture=fixture, reset=args.reset))
    except ValueError as exc:
        print(f"Local seed failed: {exc}", file=sys.stderr)
        return 1
    print(_format_report(report))
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised through main()
    raise SystemExit(main())
