import re
from pathlib import Path

from app.core.setup.routers import ROUTER_MODULES
from utils.testing_support.docs import (
    BACKEND_DIR,
    BACKEND_PLAYBOOK_PATH,
    CODE_CHANGE_REQUEST_TEMPLATE_PATH,
    DOCS_DIR,
    FEATURE_REQUEST_TEMPLATE_PATH,
    INTEGRATION_REQUEST_TEMPLATE_PATH,
)

REPO_DIR = BACKEND_DIR.parent
PRODUCT_PLANS_DIR = REPO_DIR / "docs" / "product" / "plans"
PRODUCT_CAPABILITIES_DIR = REPO_DIR / "docs" / "product" / "capabilities"
PRODUCT_BACKLOG_PATH = REPO_DIR / "docs" / "product" / "BACKLOG_ABOGADO_FACIL.md"
BACKEND_ARCHITECTURE_DIR = DOCS_DIR / "architecture"
MARKDOWN_LINK_TARGET_PATTERN = re.compile(r"\[[^\]]*\]\((?P<target>[^)#]+)(?:#[^)]+)?\)")
BACKLOG_IN_PROGRESS_PATTERN = re.compile(
    r"^\|\s*(?P<ticket>[A-Z]+-\d+[A-Z]?)\s*\|.*\|\s*En progreso\s*\|",
    re.MULTILINE,
)
PYTHON_PATH_TOKEN_PATTERN = re.compile(r"`((?:app|utils)/[A-Za-z0-9_./-]+\.py)`")
PLAYBOOK_SECTION_PATTERN_TEMPLATE = r"^## {heading}\s*$"
ROUTER_MODULE_BULLET_PATTERN = re.compile(r"^\-\s+`(?P<module>app\.[A-Za-z0-9_.]+)`\s*$")

REQUIRED_PLAYBOOK_SECTIONS: tuple[str, ...] = (
    "Architecture Map",
    "Router Inventory",
    "Non-Negotiable Engineering Rules",
    "Add a New Feature Workflow",
    "Add a New Integration Workflow",
    "AI Operating Protocol",
    "Reviewer Approval Checklist",
)

REQUIRED_TEMPLATE_SECTIONS: tuple[str, ...] = (
    "Problem and Goal",
    "Scope (In / Out)",
    "API, Data, and Authorization Implications",
    "Observability and Error Handling",
    "Acceptance Criteria",
    "Required Tests",
    "Reviewer Validation Checklist",
)


def _iter_markdown_files(root: Path) -> list[Path]:
    return sorted(root.rglob("*.md"))


def _read_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_section(markdown: str, heading: str) -> str:
    section_pattern = re.compile(
        rf"^## {re.escape(heading)}\n(?P<section>[\s\S]*?)(?=^## |\Z)",
        re.MULTILINE,
    )
    section_match = section_pattern.search(markdown)
    assert section_match is not None, f"Section '## {heading}' not found"
    return section_match.group("section")


def test_backend_docs_python_path_references_exist() -> None:
    missing_references: list[str] = []

    for markdown_path in _iter_markdown_files(DOCS_DIR):
        markdown = _read_markdown(markdown_path)
        tokens = {match.group(1) for match in PYTHON_PATH_TOKEN_PATTERN.finditer(markdown)}
        for token in sorted(tokens):
            if "<" in token or ">" in token:
                continue

            resolved_path = BACKEND_DIR / token
            if resolved_path.exists():
                continue

            relative_markdown_path = markdown_path.relative_to(BACKEND_DIR).as_posix()
            missing_references.append(f"{relative_markdown_path} -> {token}")

    assert missing_references == []


def test_backend_playbook_exists_and_has_required_sections() -> None:
    assert BACKEND_PLAYBOOK_PATH.exists()
    markdown = _read_markdown(BACKEND_PLAYBOOK_PATH)

    missing_headings = [
        heading
        for heading in REQUIRED_PLAYBOOK_SECTIONS
        if re.search(PLAYBOOK_SECTION_PATTERN_TEMPLATE.format(heading=re.escape(heading)), markdown, re.MULTILINE)
        is None
    ]
    assert missing_headings == []


def test_backend_playbook_router_inventory_matches_router_catalog() -> None:
    markdown = _read_markdown(BACKEND_PLAYBOOK_PATH)
    router_inventory_section = _extract_section(markdown, "Router Inventory")

    documented_modules = tuple(
        match.group("module")
        for line in router_inventory_section.splitlines()
        for match in [ROUTER_MODULE_BULLET_PATTERN.match(line.strip())]
        if match is not None
    )

    assert documented_modules == ROUTER_MODULES


def test_request_templates_exist_and_have_required_sections() -> None:
    template_paths = (
        FEATURE_REQUEST_TEMPLATE_PATH,
        INTEGRATION_REQUEST_TEMPLATE_PATH,
        CODE_CHANGE_REQUEST_TEMPLATE_PATH,
    )

    missing_files = [path.as_posix() for path in template_paths if not path.exists()]
    assert missing_files == []

    missing_sections: list[str] = []
    for template_path in template_paths:
        markdown = _read_markdown(template_path)
        for heading in REQUIRED_TEMPLATE_SECTIONS:
            if re.search(PLAYBOOK_SECTION_PATTERN_TEMPLATE.format(heading=re.escape(heading)), markdown, re.MULTILINE):
                continue

            missing_sections.append(f"{template_path.relative_to(BACKEND_DIR).as_posix()} -> {heading}")

    assert missing_sections == []


def _indexed_local_markdown_filenames(index_path: Path) -> set[str]:
    markdown = _read_markdown(index_path)
    return {
        match.group("target")
        for match in MARKDOWN_LINK_TARGET_PATTERN.finditer(markdown)
        if match.group("target").endswith(".md")
        and "/" not in match.group("target")
        and "\\" not in match.group("target")
    }


def test_product_plan_indexes_match_plan_directories() -> None:
    for status_dir_name in ("pending", "implemented"):
        status_dir = PRODUCT_PLANS_DIR / status_dir_name
        actual_plans = {path.name for path in status_dir.glob("*.md") if path.name != "README.md"}
        indexed_plans = _indexed_local_markdown_filenames(status_dir / "README.md")

        assert indexed_plans == actual_plans


def test_product_capability_index_matches_capability_directory() -> None:
    actual_capabilities = {path.name for path in PRODUCT_CAPABILITIES_DIR.glob("*.md") if path.name != "README.md"}
    indexed_capabilities = _indexed_local_markdown_filenames(PRODUCT_CAPABILITIES_DIR / "README.md")

    assert indexed_capabilities == actual_capabilities


def test_in_progress_backlog_items_have_pending_plans() -> None:
    backlog = _read_markdown(PRODUCT_BACKLOG_PATH)
    in_progress_tickets = {match.group("ticket") for match in BACKLOG_IN_PROGRESS_PATTERN.finditer(backlog)}
    pending_plan_tickets = {
        path.name.split("_", maxsplit=1)[0]
        for path in (PRODUCT_PLANS_DIR / "pending").glob("*.md")
        if path.name != "README.md"
    }

    assert in_progress_tickets <= pending_plan_tickets


def test_backend_architecture_feature_inventory_matches_feature_packages() -> None:
    architecture_doc = _read_markdown(BACKEND_ARCHITECTURE_DIR / "clean_architecture_ports_adapters.md")
    inventory = architecture_doc.split("Current features:", maxsplit=1)[1].split(
        "`outbox`, `ai_execution`, and `ai_jobs`", maxsplit=1
    )[0]
    documented_features = {match.group(1) for match in re.finditer(r"^- `([a-z][a-z0-9_]*)`$", inventory, re.MULTILINE)}
    actual_features = {
        path.name
        for path in (BACKEND_DIR / "app" / "features").iterdir()
        if path.is_dir() and path.name != "__pycache__"
    }

    assert documented_features == actual_features


def test_ai_credential_encryption_key_is_documented_and_wired_for_compose() -> None:
    required_paths = (
        REPO_DIR / ".env_examples",
        REPO_DIR / "compose.yaml",
        REPO_DIR / "compose.prod.yaml",
        REPO_DIR / "README.md",
        BACKEND_DIR / "README.md",
    )

    missing = [
        path.relative_to(REPO_DIR).as_posix()
        for path in required_paths
        if "AI_CREDENTIAL_ENCRYPTION_KEY" not in path.read_text(encoding="utf-8")
    ]

    assert missing == []


def test_rate_limiting_docs_distinguish_direct_and_compose_defaults() -> None:
    markdown = _read_markdown(DOCS_DIR / "operations" / "rate_limiting.md")
    compose = (REPO_DIR / "compose.yaml").read_text(encoding="utf-8")

    assert "Direct backend execution" in markdown
    assert "Compose profile" in markdown
    assert 'RATE_LIMIT_ENABLED: "${RATE_LIMIT_ENABLED:-true}"' in compose
    assert 'RATE_LIMIT_STORAGE: "${RATE_LIMIT_STORAGE:-redis}"' in compose
