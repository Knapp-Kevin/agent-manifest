# Memory checkpoint assessment reference vectors

Status: preparatory reference-fixture plan for `MemoryCheckpointAssessment/0.1`

These fixtures are intended to exercise the non-normative memory checkpoint assessment harness tracked by agentrust-io/agent-manifest#298.

They are **reference assessment vectors**, not AgentTrust conformance vectors. Do not describe them as conformance material unless maintainers explicitly adopt that role later.

## Design rules

1. Every vector must be deterministic and self-contained.
2. Every vector must identify the baseline state, candidate state, probe suite, retriever profile, and expected behavioral result.
3. Public fixtures must contain enough material for an independent implementation to reproduce the result.
4. Private-store behavior must not be represented as independently reproducible when the underlying state is unavailable.
5. Model-judge output is excluded from expected deterministic results.
6. Assessment result and deployment/promotion policy remain separate.
7. Where practical, each load-bearing rule receives at least two independent vectors capable of catching different defects, following the independence principle discussed in trace-spec#124.
8. Canonicalization-sensitive digests must have cross-implementation boundary coverage before they are treated as portable evidence.

## Planned state fixtures

The first set should cover:

- `baseline.json`: approved baseline used by transition probes;
- `candidate-pass.json`: preserves all declared invariants;
- `candidate-correction-missing.json`: correction exists in state but is not retrieved;
- `candidate-correction-outranked.json`: correction is retrieved but remains below the superseded fact;
- `candidate-anchor-missing.json`: required anchor disappears from retrieval;
- `candidate-anchor-demoted.json`: anchor remains present but falls below the permitted rank;
- `candidate-scope-key-leak.json`: forbidden item key is retrieved;
- `candidate-scope-label-leak.json`: item identity/order stays stable while a forbidden scope label appears;
- `candidate-differentiation-collapse.json`: two declared contexts return the same ordered identities;
- `candidate-differentiation-required-missing.json`: a state-conditioned required item is not retrieved;
- `candidate-id-churn.json`: logical identity cannot be matched across the transition;
- `candidate-repeatability-unstable.json`: repeated identical requests do not produce a stable identity ordering;
- `candidate-scope-repeatability-unstable.json`: item ids/order remain stable while scope labels vary across trials.

## Planned profile fixtures

Retriever-profile cases should include:

- deterministic profile with explicit total-order/tie policy;
- deterministic profile missing a tie policy, rejected as ineligible;
- unsupported/unknown profile with no tie policy, accepted structurally but producing behavioral indeterminate results;
- profile differing only by embedding model revision;
- profile differing only by quantization;
- profile differing only by query preprocessing;
- profile differing only by index configuration;
- profile differing only by filtering rule;
- profile differing only by top-k;
- profile differing only by reranker configuration.

Each material profile change should change the content-addressed profile digest.

## Planned state-binding fixtures

State reference cases should separately prove that changing any load-bearing state identity changes the assessment binding:

- baseline checkpoint digest;
- candidate checkpoint digest;
- baseline retrieval-state digest;
- candidate retrieval-state digest.

`indexed_item_count` is an observation and should not be silently promoted into a stronger integrity claim than the design assigns it.

## Probe groups

### Correction precedence

At least two independent failures:

1. correction not retrieved at all;
2. correction retrieved but ranked below the superseded fact.

The first catches omission behavior. The second catches precedence behavior.

### Anchor preservation

At least two independent failures:

1. anchor disappears;
2. anchor remains but is demoted below `max_rank`.

### Scope isolation

At least two independent failures:

1. forbidden item identity retrieved;
2. allowed item identity retrieved with a forbidden scope label.

The second case is especially important because repeatability evidence must include scope labels rather than checking ids/order only.

### State-conditioned differentiation

At least two independent failures:

1. contexts collapse to the same ordered item identities;
2. contexts remain different but one misses a required item or retrieves a forbidden item.

## Indeterminate vectors

Explicitly cover:

- `adapter_unsupported`;
- `repeatability_unstable`;
- `repeatability_not_run`;
- `baseline_precondition_unmet`;
- `id_churn`.

Do not introduce `material_unavailable` as a behavioral indeterminate reason. Material access affects rerun/verifiability strength, not whether the completed run observed pass/fail behavior.

## Confidentiality signaling

A scope-isolation failure is a behavioral `fail` with confidentiality severity.

The top-level `security_flags.contains_confidentiality_failure` must remain true for any observed confidentiality failure, including a non-required/diagnostic scope probe. Diagnostic status must not hide a confidentiality alarm.

## Mutation-resistance cases

The harness must be tested against adapters that attempt to mutate:

- the incoming `RetrievalRequest`;
- their exposed `RetrieverProfile` after the run starts;
- the supplied `ProbeSuite` after the run starts.

The emitted assessment must remain bound to the frozen inputs used for the run.

## Timestamp cases

`assessed_at` must be timezone-aware. A naive datetime should be rejected rather than silently interpreted in a local timezone.

## Canonicalization boundary

Agent Manifest issue #322 reports that the sibling repository canonicalizer is not fully RFC 8785-conformant. Before these vectors are used as portable evidence, add canonicalization-boundary cases covering at least:

- UTF-16 code-unit key ordering with supplementary-plane characters;
- nested UTF-16 key ordering;
- exponent formatting boundaries;
- integral-number formatting boundaries relevant to ECMAScript `Number::toString`;
- values outside the interoperable IEEE-754 integer domain;
- characters that must remain literal rather than being over-escaped.

Do not solve this by introducing an assessment-specific canonicalizer. The harness should consume the project-approved standards-conformant primitive once that dependency is settled.

## Second-retriever requirement

Before submission, run the same invariant suite through at least two independently shaped deterministic retriever adapters.

The purpose is not framework marketing. It is to falsify framework-specific semantics in the assessment contract. A simple in-memory ranker and a separately implemented keyword/BM25-like deterministic ranker are sufficient if both expose the same minimal adapter boundary without sharing retrieval implementation logic.

## Full validation gate

Before upstream submission is considered, execute the repository validation commands from CONTRIBUTING in a complete checkout/CI environment:

```text
pytest -v
mypy src/agent_manifest
ruff check src/ tests/
bandit -r src/agent_manifest
```

Until those pass against the actual branch, do not claim full repository validation.

Signed-off-by: Kevin Knapp <krknapp@gmail.com>
