from __future__ import annotations

from datetime import datetime, timezone

from agent_manifest._memory_assessment import (
    BehavioralResult,
    Coverage,
    InvocationEvidence,
    MaterialAccess,
    MemoryCheckpointAssessment,
    ObservedStatus,
    RepeatabilityEvidence,
    SecurityFlags,
    StateReference,
)


def _hash(char: str) -> str:
    return "sha256:" + char * 64


def _artifact() -> MemoryCheckpointAssessment:
    return MemoryCheckpointAssessment(
        baseline_state=StateReference(
            checkpoint_digest=_hash("a"),
            retrieval_state_digest=_hash("b"),
            indexed_item_count=3,
        ),
        candidate_state=StateReference(
            checkpoint_digest=_hash("c"),
            retrieval_state_digest=_hash("d"),
            indexed_item_count=4,
        ),
        probe_suite_digest=_hash("e"),
        retriever_profile_digest=_hash("f"),
        assessed_at=datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc),
        material_access=MaterialAccess.public,
        invocation_evidence=(
            InvocationEvidence(
                state_name="candidate",
                request_digest=_hash("1"),
                repeatability=RepeatabilityEvidence(
                    trials=20,
                    distinct_orderings_observed=1,
                    observed_status=ObservedStatus.stable,
                ),
            ),
        ),
        probe_results=(),
        coverage=Coverage(
            required_probe_count=1,
            passed=1,
            failed=0,
            indeterminate=0,
            indeterminate_rate=0.0,
        ),
        security_flags=SecurityFlags(),
        result=BehavioralResult.pass_,
    )


def test_artifact_json_round_trip_is_lossless() -> None:
    artifact = _artifact()
    encoded = artifact.model_dump_json(exclude_none=True)
    assert MemoryCheckpointAssessment.model_validate_json(encoded) == artifact


def test_artifact_json_schema_is_closed_and_versioned() -> None:
    schema = MemoryCheckpointAssessment.model_json_schema()

    assert schema["additionalProperties"] is False
    assert schema["properties"]["type"]["const"] == "MemoryCheckpointAssessment"
    assert schema["properties"]["version"]["const"] == "0.1"
    assert schema["properties"]["assessed_at"]["format"] == "date-time"

    required = set(schema["required"])
    assert {
        "baseline_state",
        "candidate_state",
        "probe_suite_digest",
        "retriever_profile_digest",
        "assessed_at",
        "material_access",
        "invocation_evidence",
        "probe_results",
        "coverage",
        "security_flags",
        "result",
    }.issubset(required)

    for definition in (
        "Coverage",
        "InvocationEvidence",
        "MemoryCheckpointAssessment",
        "ProbeResult",
        "RepeatabilityEvidence",
        "RuntimeObservation",
        "SecurityFlags",
        "StateReference",
    ):
        if definition == "MemoryCheckpointAssessment":
            model_schema = schema
        else:
            model_schema = schema["$defs"][definition]
        assert model_schema["additionalProperties"] is False


def test_behavioral_result_schema_has_only_three_outcomes() -> None:
    schema = MemoryCheckpointAssessment.model_json_schema()
    assert set(schema["$defs"]["BehavioralResult"]["enum"]) == {
        "pass",
        "fail",
        "indeterminate",
    }
