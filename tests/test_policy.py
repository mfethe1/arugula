from pathlib import Path

from arugula.nats import NatsBus
from arugula.policy import requires_approval, validate_subject


def test_validate_subject_accepts_documented_project_subject() -> None:
    assert validate_subject('arugula.mutation.buildbid.proposed') == 'arugula.mutation.buildbid.proposed'


def test_validate_subject_rejects_wildcards() -> None:
    try:
        validate_subject('arugula.mutation.*.proposed')
    except ValueError as exc:
        assert 'invalid NATS subject' in str(exc)
    else:
        raise AssertionError('wildcard publish should fail')


def test_requires_approval_flags_privileged_subjects() -> None:
    assert requires_approval('arugula.promote.memu.requested') is True
    assert requires_approval('arugula.mutation.rareagent.proposed') is False


def test_publish_requires_approval_metadata_for_privileged_subjects(tmp_path: Path) -> None:
    bus = NatsBus(tmp_path)
    try:
        bus.publish('arugula.promote.memu.requested', {'project': 'memu'})
    except ValueError as exc:
        assert 'requires approval metadata' in str(exc)
    else:
        raise AssertionError('privileged subject should require approval metadata')


def test_publish_wraps_events_in_provenance_envelope(tmp_path: Path) -> None:
    bus = NatsBus(tmp_path)
    event = bus.publish(
        'arugula.mutation.trading.proposed',
        {
            'project': 'trading',
            'title': 'Split orchestration scorer',
            'mutation_target': 'score weights',
        },
    )
    assert event['subject'] == 'arugula.mutation.trading.proposed'
    assert event['payload']['project'] == 'trading'
    assert event['provenance']['transport'] == 'local-ledger'
    assert event['event_id']
