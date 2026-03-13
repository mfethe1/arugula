from __future__ import annotations

import re
from typing import Any

from .projects import PROJECTS

_VALID_PROJECTS = set(PROJECTS)
_CONTROL_SUBJECTS = {
    "arugula.control.heartbeat",
    "arugula.control.health",
    "arugula.control.policy",
}
_SUBJECT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^arugula\.signal\.(?P<project>[a-z0-9_-]+)\.(telemetry|incident|feedback|outcome)$"),
    re.compile(r"^arugula\.hypothesis\.(?P<project>[a-z0-9_-]+)\.proposed$"),
    re.compile(r"^arugula\.mutation\.(?P<project>[a-z0-9_-]+)\.(proposed|accepted)$"),
    re.compile(r"^arugula\.run\.(?P<project>[a-z0-9_-]+)\.(started|completed)$"),
    re.compile(r"^arugula\.score\.(?P<project>[a-z0-9_-]+)\.computed$"),
    re.compile(r"^arugula\.promote\.(?P<project>[a-z0-9_-]+)\.(requested|approved)$"),
    re.compile(r"^arugula\.rollback\.(?P<project>[a-z0-9_-]+)\.(requested|completed)$"),
    re.compile(r"^arugula\.(memory\.write|ledger\.append|backlog\.append)\.(?P<project>[a-z0-9_-]+)$"),
)

_APPROVAL_REQUIRED_SUFFIXES = (
    '.accepted',
    '.approved',
    '.requested',
    '.completed',
)
_APPROVAL_REQUIRED_PREFIXES = (
    'arugula.promote.',
    'arugula.rollback.',
)


def validate_subject(subject: str) -> str:
    if ' ' in subject or '*' in subject or '>' in subject:
        raise ValueError(f'invalid NATS subject: {subject}')
    if subject in _CONTROL_SUBJECTS:
        return subject
    for pattern in _SUBJECT_PATTERNS:
        match = pattern.fullmatch(subject)
        if not match:
            continue
        project = match.groupdict().get('project')
        if project and project not in _VALID_PROJECTS:
            raise ValueError(f'unknown project in subject: {subject}')
        return subject
    raise ValueError(f'unrecognized NATS subject: {subject}')


def requires_approval(subject: str) -> bool:
    if subject.startswith(_APPROVAL_REQUIRED_PREFIXES):
        return True
    return any(subject.endswith(suffix) and '.run.' not in subject for suffix in _APPROVAL_REQUIRED_SUFFIXES)


def validate_payload(subject: str, payload: dict[str, Any]) -> None:
    project = payload.get('project')
    if project is not None and project not in _VALID_PROJECTS:
        raise ValueError(f'unknown project in payload: {project}')
    if 'approval' in payload and not isinstance(payload['approval'], dict):
        raise ValueError('approval must be an object when provided')
    if requires_approval(subject):
        approval = payload.get('approval')
        if not isinstance(approval, dict):
            raise ValueError(f'{subject} requires approval metadata')
        if approval.get('state') not in {'requested', 'approved', 'rejected', 'not_required'}:
            raise ValueError(f'{subject} requires approval.state to be set')
        if not approval.get('actor'):
            raise ValueError(f'{subject} requires approval.actor')
