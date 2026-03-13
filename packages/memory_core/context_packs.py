from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class ContextPackDefinition:
    name: str
    description: str
    keywords: tuple[str, ...]
    search_terms: tuple[str, ...]
    priority_paths: tuple[str, ...]
    distilled_path: str | None = None
    supporting_limit: int = 3


@dataclass(frozen=True)
class ContextTemplateDescriptor:
    path: str
    title: str | None = None
    metadata: dict | None = None


@dataclass(frozen=True)
class ContextTemplateMatch:
    descriptor: ContextTemplateDescriptor
    score: int


AUTH_PACK = ContextPackDefinition(
    name="auth",
    description="Authentication, login, logout, sessions, router guards, auth store, frontend auth flows.",
    keywords=(
        "auth",
        "login",
        "logout",
        "session",
        "sessions",
        "refresh",
        "token",
        "router",
        "guard",
        "pinia",
        "redirect",
        "401",
    ),
    search_terms=(
        "auth login logout session refresh router guards auth store frontend debugging",
    ),
    priority_paths=(
        "project/overview.md",
        "architecture/auth-flow.md",
        "frontend/auth-store.md",
        "frontend/router.md",
        "frontend/logout-flow.md",
        "features/authentication.md",
        "debugging/logout-not-redirecting.md",
        "patterns/debugging-patterns.md",
    ),
    distilled_path="distilled/auth.md",
)

DEPLOYMENT_PACK = ContextPackDefinition(
    name="deployment",
    description="Deployment, infrastructure, Docker, Cloudflare, monitoring, CI/CD, runtime constraints.",
    keywords=("deploy", "deployment", "docker", "cloudflare", "monitoring", "infra", "infrastructure", "ci", "cd"),
    search_terms=(
        "deployment docker cloudflare monitoring ci cd constraints infrastructure",
    ),
    priority_paths=(
        "project/constraints.md",
        "deployment/docker.md",
        "deployment/cloudflare.md",
        "deployment/monitoring.md",
        "deployment/ci-cd.md",
    ),
    distilled_path="distilled/deployment.md",
)

DATABASE_PACK = ContextPackDefinition(
    name="database",
    description="Database schema, migrations, indexing strategy, pgvector, and data-layer decisions.",
    keywords=(
        "database",
        "db",
        "postgres",
        "schema",
        "migration",
        "migrations",
        "pgvector",
        "vector",
        "query",
        "sql",
        "index",
        "indexing",
    ),
    search_terms=(
        "database schema migrations pgvector vector db indexing strategy decisions",
    ),
    priority_paths=(
        "database/schema.md",
        "database/migrations.md",
        "database/indexing-strategy.md",
        "database/pgvector.md",
        "decisions/adr-002-vector-db.md",
    ),
    distilled_path="distilled/database.md",
)

BACKEND_JOBS_PACK = ContextPackDefinition(
    name="backend-jobs",
    description="Background jobs, schedulers, backend patterns, async execution, and operational failures.",
    keywords=(
        "job",
        "jobs",
        "scheduler",
        "scheduled",
        "cron",
        "worker",
        "queue",
        "background",
        "celery",
        "report",
        "reports",
        "task",
    ),
    search_terms=(
        "background jobs scheduler celery reports error handling backend patterns async",
    ),
    priority_paths=(
        "backend/background-jobs.md",
        "backend/error-handling.md",
        "backend/celery.md",
        "patterns/backend-patterns.md",
        "patterns/async-patterns.md",
        "debugging/celery-task-stuck.md",
    ),
    distilled_path="distilled/backend-jobs.md",
)

CALENDAR_PACK = ContextPackDefinition(
    name="calendar",
    description="Calendar completion state, scheduling, daily status aggregation, and date-bound UI flows.",
    keywords=(
        "calendar",
        "schedule",
        "scheduled",
        "date",
        "timezone",
        "completion",
        "completed",
        "daily",
        "week",
        "weekly",
    ),
    search_terms=(
        "calendar scheduling completion daily status meals exercises timezone frontend debugging",
    ),
    priority_paths=(
        "architecture/data-flow.md",
        "frontend/vue-architecture.md",
        "patterns/frontend-patterns.md",
        "patterns/debugging-patterns.md",
        "debugging/calendar-meals-not-completed.md",
    ),
    distilled_path="distilled/calendar.md",
)

MEALS_PACK = ContextPackDefinition(
    name="meals",
    description="Meals, nutrition logs, meal completion state, and frontend/backend mapping issues.",
    keywords=(
        "meal",
        "meals",
        "nutrition",
        "food",
        "meal_log",
        "meal logs",
        "meal-log",
        "meal completion",
    ),
    search_terms=(
        "meals nutrition meal logs meal completion calendar frontend store debugging",
    ),
    priority_paths=(
        "architecture/data-flow.md",
        "frontend/vue-architecture.md",
        "patterns/frontend-patterns.md",
        "patterns/debugging-patterns.md",
        "debugging/calendar-meals-not-completed.md",
    ),
    distilled_path="distilled/meals.md",
)

STATE_PACK = ContextPackDefinition(
    name="state-management",
    description="Frontend store state, cache invalidation, reactive updates, and derived completion logic.",
    keywords=(
        "state",
        "store",
        "stores",
        "pinia",
        "reactive",
        "reactivity",
        "computed",
        "cache",
        "invalidate",
        "sync",
    ),
    search_terms=(
        "frontend store pinia reactive state cache invalidation computed debugging",
    ),
    priority_paths=(
        "frontend/vue-architecture.md",
        "patterns/frontend-patterns.md",
        "patterns/debugging-patterns.md",
    ),
)

ROUTING_PACK = ContextPackDefinition(
    name="routing",
    description="Router guards, navigation state, view transitions, and role-based route behavior.",
    keywords=(
        "route",
        "routes",
        "router",
        "routing",
        "redirect",
        "navigation",
        "guard",
        "guards",
    ),
    search_terms=(
        "router routing redirect navigation guards frontend debugging",
    ),
    priority_paths=(
        "architecture/auth-flow.md",
        "frontend/router.md",
        "frontend/logout-flow.md",
        "patterns/frontend-patterns.md",
    ),
)

UI_PACK = ContextPackDefinition(
    name="ui-rendering",
    description="Rendered state versus source state, component-level display issues, and view synchronization bugs.",
    keywords=(
        "ui",
        "render",
        "rendering",
        "view",
        "component",
        "display",
        "shown",
        "visible",
        "mark",
        "marked",
    ),
    search_terms=(
        "ui rendering component display visible state synchronization frontend debugging",
    ),
    priority_paths=(
        "frontend/ui-patterns.md",
        "frontend/vue-architecture.md",
        "patterns/frontend-patterns.md",
        "patterns/debugging-patterns.md",
    ),
)

GENERAL_PACK = ContextPackDefinition(
    name="general",
    description="General project overview and recent context when the task does not map cleanly to a module.",
    keywords=(),
    search_terms=("project overview architecture recent context",),
    priority_paths=(
        "index/index.md",
        "project/overview.md",
        "architecture/system-overview.md",
        "architecture/service-architecture.md",
    ),
    distilled_path="distilled/general.md",
    supporting_limit=2,
)

CONTEXT_PACKS: tuple[ContextPackDefinition, ...] = (
    AUTH_PACK,
    DEPLOYMENT_PACK,
    DATABASE_PACK,
    BACKEND_JOBS_PACK,
    CALENDAR_PACK,
    MEALS_PACK,
    STATE_PACK,
    ROUTING_PACK,
    UI_PACK,
)

CONTEXT_TEMPLATE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "debug-auth": AUTH_PACK.keywords,
    "debug-calendar": CALENDAR_PACK.keywords + MEALS_PACK.keywords,
    "debug-meals": MEALS_PACK.keywords,
    "debug-state-management": STATE_PACK.keywords,
    "debug-ui-rendering": UI_PACK.keywords,
    "debug-routing": ROUTING_PACK.keywords,
}

TOKEN_RE = re.compile(r"[a-z0-9_/-]+")


def infer_context_pack(task: str) -> tuple[ContextPackDefinition, list[str]]:
    normalized = task.lower()
    best_pack = GENERAL_PACK
    best_keywords: list[str] = []
    best_score = 0

    for pack in CONTEXT_PACKS:
        matched = [keyword for keyword in pack.keywords if keyword in normalized]
        score = len(matched)
        if score > best_score:
            best_pack = pack
            best_keywords = matched
            best_score = score

    return best_pack, best_keywords


def match_context_paths(
    task: str,
    available_paths: list[str],
    modules: list[str] | None = None,
) -> list[str]:
    descriptors = [ContextTemplateDescriptor(path=path) for path in available_paths]
    return [descriptor.path for descriptor in match_context_descriptors(task, descriptors, modules=modules)]


def match_context_descriptors(
    task: str,
    descriptors: list[ContextTemplateDescriptor],
    modules: list[str] | None = None,
) -> list[ContextTemplateDescriptor]:
    return [match.descriptor for match in rank_context_descriptors(task, descriptors, modules=modules)]


def rank_context_descriptors(
    task: str,
    descriptors: list[ContextTemplateDescriptor],
    modules: list[str] | None = None,
) -> list[ContextTemplateMatch]:
    normalized = task.lower()
    task_tokens = set(TOKEN_RE.findall(normalized))
    module_set = {module.lower() for module in (modules or [])}
    scored_matches: list[ContextTemplateMatch] = []

    for descriptor in descriptors:
        stem = Path(descriptor.path).stem.lower()
        metadata = descriptor.metadata or {}
        score = _score_context_descriptor(
            normalized=normalized,
            task_tokens=task_tokens,
            stem=stem,
            metadata=metadata,
            module_set=module_set,
        )
        if score <= 0:
            continue
        scored_matches.append(ContextTemplateMatch(descriptor=descriptor, score=score))

    scored_matches.sort(key=lambda item: (-item.score, item.descriptor.path))
    return scored_matches


def _score_context_descriptor(
    *,
    normalized: str,
    task_tokens: set[str],
    stem: str,
    metadata: dict,
    module_set: set[str],
) -> int:
    keywords = _context_keywords(stem, metadata)
    problem_types = _normalize_terms(metadata.get("problem_types"))
    applies_to = _normalize_terms(metadata.get("applies_to"))
    related_distilled = _normalize_terms(metadata.get("related_distilled"))
    priority = metadata.get("priority", 0)
    try:
        priority_value = int(priority)
    except (TypeError, ValueError):
        priority_value = 0

    score = 0
    score += sum(3 for keyword in keywords if keyword in normalized)
    score += sum(2 for keyword in keywords if keyword in task_tokens)
    score += sum(2 for item in problem_types if item in normalized or item in task_tokens)
    score += sum(2 for item in applies_to if item in normalized or item in task_tokens)
    score += sum(1 for item in related_distilled if item in module_set or item in normalized)
    score += sum(1 for item in applies_to if item in module_set)

    if stem.startswith("debug-") and stem.removeprefix("debug-") in normalized:
        score += 2

    score += priority_value
    return score


def _context_keywords(stem: str, metadata: dict) -> set[str]:
    keywords = set(_normalize_terms(metadata.get("keywords")))
    keywords.update(_normalize_terms(metadata.get("problem_types")))
    keywords.update(_normalize_terms(metadata.get("applies_to")))
    keywords.update(_normalize_terms(metadata.get("related_distilled")))

    title = metadata.get("title")
    if isinstance(title, str):
        keywords.update(TOKEN_RE.findall(title.lower()))

    if not keywords:
        fallback = CONTEXT_TEMPLATE_KEYWORDS.get(stem)
        if fallback is not None:
            keywords.update(fallback)
        else:
            keywords.update(token for token in stem.replace("_", "-").split("-") if token and token != "debug")

    return {keyword.lower() for keyword in keywords if keyword}


def _normalize_terms(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [token.lower() for token in TOKEN_RE.findall(value.lower())]
    if isinstance(value, (list, tuple, set)):
        terms: list[str] = []
        for item in value:
            if isinstance(item, str):
                terms.extend(TOKEN_RE.findall(item.lower()))
        return terms
    return []
