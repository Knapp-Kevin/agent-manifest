from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

import agent_manifest._memory_assessment_gate as gate_module
from agent_manifest._memory_assessment import (
    BehavioralResult,
    Coverage,
    IndeterminateReason,
    MaterialAccess,
    MemoryCheckpointAssessment,
    ProbeResult,
    SecurityFlags,
    SeverityClass,
    StateReference,
)
from agent_manifest._memory_assessment_gate import (
    ApplicabilityMismatch,
    AssessmentGatePolicy,
    GateFailureReason,
    evaluate_assessment_gate,
)


def _hash(char: str) -> str:
    return "sha256:" + char * 64


def _assessment(
    result: BehavioralResult = BehavioralResult.pass_,
    *,
    baseline_checkpoint: str | None = None,
    candidate_checkpoint: str | None = None,
    baseline_retrieval_state: str | None = None,
    candidate_retrieval_state: str | None = None,
    probe_suite: str | None = None,
    retriever_profile: str | None = None,
    assessed_at: datetime | None = None,
) -> MemoryCheckpointAssessment:
    reasons = (
        (IndeterminateReason.repeatability_unstable,)
        if result is BehavioralResult.indeterminate
        else ()
    )
    violations = ("required behavioral predicate failed",) if result is BehavioralResult.fail else ()
    return MemoryCheckpointAssessment(
        baseline_state=StateReference(
            checkpoint_digest=baseline_checkpoint or _hash("a"),
            retrieval_state_digest=baseline_retrieval_state or _hash("b"),
            indexed_item_count=3,
        ),
        candidate_state=StateReference(
            checkpoint_digest=candidate_checkpoint or _hash("c"),
            retrieval_state_digest=candidate_retrieval_state or _hash("d"),
            indexed_item_count=4,
        ),
        probe_suite_digest=probe_suite or _hash("e"),
        retriever_profile_digest=retriever_profile or _hash("f"),
        assessed_at=assessed_at or datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc),
        material_access=MaterialAccess.public,
        invocation_evidence=(),
        probe_results=(
            ProbeResult(
                probe_id="p1",
                required=True,
                result=result,
                severity=SeverityClass.behavioral,
                reasons=reasons,
                violations=violations,
            ),
        ),
        coverage=Coverage(
            required_probe_count=1,
            passed=int(result is BehavioralResult.pass_),
            failed=int(result is BehavioralResult.fail),
            indeterminate=int(result is BehavioralResult.indeterminate),
            indeterminate_rate=(1.0 if result is BehavioralResult.indeterminate else 0.0),
        ),
        security_flags=SecurityFlags(),
        result=result,
    )


def _policy(**overrides: object) -> AssessmentGatePolicy:
    values: dict[str, object] = {
        "baseline_checkpoint_digest": _hash("a"),
        "candidate_checkpoint_digest": _hash("c"),
        "baseline_retrieval_state_digest": _hash("b"),
        "candidate_retrieval_state_digest": _hash("d"),
        "probe_suite_digest": _hash("e"),
        "retriever_profile_digest": _hash("f"),
    }
    values.update(overrides)
    return AssessmentGatePolicy.model_validate(values)


def test_applicable_pass_satisfies_only_this_gate() -> None:
    evaluation = evaluate_assessment_gate(_policy(), [_assessment()])

    assert evaluation.satisfied is True
    assert evaluation.applicable_assessment_count == 1
    assert evaluation.applicable_results == (BehavioralResult.pass_,)
    assert evaluation.reasons == ()
    assert not hasattr(gate_module, "approve_checkpoint")


def test_applicable_fail_blocks_gate_but_remains_valid_evidence() -> None:
    assessment = _assessment(BehavioralResult.fail)
    before = assessment.model_dump_json()

    evaluation = evaluate_assessment_gate(_policy(), [assessment])

    assert evaluation.satisfied is False
    assert evaluation.reasons == (GateFailureReason.applicable_assessment_failed,)
    assert assessment.result is BehavioralResult.fail
    assert assessment.model_dump_json() == before


def test_applicable_indeterminate_is_not_promoted_to_pass_or_fail() -> None:
    assessment = _assessment(BehavioralResult.indeterminate)

    evaluation = evaluate_assessment_gate(_policy(), [assessment])

    assert evaluation.satisfied is False
    assert evaluation.applicable_results == (BehavioralResult.indeterminate,)
    assert evaluation.reasons == (
        GateFailureReason.applicable_assessment_indeterminate,
    )
    assert assessment.result is BehavioralResult.indeterminate


def test_omitted_assessment_is_policy_failure_not_evidence_failure() -> None:
    evaluation = evaluate_assessment_gate(_policy(), [])

    assert evaluation.satisfied is False
    assert evaluation.presented_assessment_count == 0
    assert evaluation.applicable_assessment_count == 0
    assert evaluation.reasons == (GateFailureReason.no_applicable_assessment,)


@pytest.mark.parametrize(
    ("assessment", "expected_mismatch"),
    [
        (
            _assessment(candidate_checkpoint=_hash("1")),
            ApplicabilityMismatch.candidate_checkpoint,
        ),
        (
            _assessment(probe_suite=_hash("2")),
            ApplicabilityMismatch.probe_suite,
        ),
        (
            _assessment(retriever_profile=_hash("3")),
            ApplicabilityMismatch.retriever_profile,
        ),
        (
            _assessment(candidate_retrieval_state=_hash("4")),
            ApplicabilityMismatch.candidate_retrieval_state,
        ),
    ],
)
def test_wrong_bound_evidence_cannot_satisfy_gate(
    assessment: MemoryCheckpointAssessment,
    expected_mismatch: ApplicabilityMismatch,
) -> None:
    evaluation = evaluate_assessment_gate(_policy(), [assessment])

    assert evaluation.satisfied is False
    assert evaluation.applicable_assessment_count == 0
    assert GateFailureReason.no_applicable_assessment in evaluation.reasons
    assert expected_mismatch in evaluation.non_applicable_mismatches


def test_evidence_window_is_load_bearing_when_policy_declares_one() -> None:
    assessed_at = datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc)
    policy = _policy(
        assessed_not_before=assessed_at + timedelta(minutes=1),
        assessed_not_after=assessed_at + timedelta(hours=1),
    )

    evaluation = evaluate_assessment_gate(
        policy,
        [_assessment(assessed_at=assessed_at)],
    )

    assert evaluation.satisfied is False
    assert ApplicabilityMismatch.before_evidence_window in evaluation.non_applicable_mismatches


def test_gate_policy_requires_timezone_aware_window() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        _policy(assessed_not_before=datetime(2026, 8, 30, 12, 0))


def test_gate_policy_rejects_reversed_window() -> None:
    later = datetime(2026, 8, 30, 13, 0, tzinfo=timezone.utc)
    earlier = later - timedelta(hours=1)
    with pytest.raises(ValidationError, match="must not be after"):
        _policy(assessed_not_before=later, assessed_not_after=earlier)


def test_any_presented_applicable_fail_keeps_gate_closed() -> None:
    evaluation = evaluate_assessment_gate(
        _policy(),
        [_assessment(), _assessment(BehavioralResult.fail)],
    )

    assert evaluation.satisfied is False
    assert evaluation.applicable_assessment_count == 2
    assert evaluation.applicable_results == (
        BehavioralResult.pass_,
        BehavioralResult.fail,
    )
    assert GateFailureReason.applicable_assessment_failed in evaluation.reasons


def test_any_presented_applicable_indeterminate_keeps_gate_closed() -> None:
    evaluation = evaluate_assessment_gate(
        _policy(),
        [_assessment(), _assessment(BehavioralResult.indeterminate)],
    )

    assert evaluation.satisfied is False
    assert evaluation.applicable_assessment_count == 2
    assert GateFailureReason.applicable_assessment_indeterminate in evaluation.reasons


def test_non_applicable_failure_does_not_poison_applicable_pass() -> None:
    evaluation = evaluate_assessment_gate(
        _policy(),
        [
            _assessment(BehavioralResult.fail, probe_suite=_hash("9")),
            _assessment(),
        ],
    )

    assert evaluation.satisfied is True
    assert evaluation.applicable_assessment_count == 1
    assert evaluation.applicable_results == (BehavioralResult.pass_,)
    assert ApplicabilityMismatch.probe_suite in evaluation.non_applicable_mismatches
