# MemoryCheckpointAssessment/0.1 preparation record

Status: private/fork preparation only

Upstream tracker: agentrust-io/agent-manifest#298
Working branch: `feat/memory-checkpoint-assessment-298`

## Submission boundary

This branch is preparatory work only. Do not open an upstream pull request, request review, or post implementation updates to AgentTrust until a maintainer explicitly indicates that the contribution is welcome.

The upstream issue already contains an ownership claim for the implementation lane. Silence after that claim is not treated as approval to submit.

## Intended contribution boundary

`MemoryCheckpointAssessment/0.1` is an external, optional, non-normative behavioral assessment artifact and reference harness for candidate memory checkpoints.

It evaluates retrieval behavior at the checkpoint transition boundary. It does not certify model correctness, memory truth, deployment safety, or Agent Manifest conformance.

The initial invariants are:

1. correction precedence;
2. anchor preservation;
3. scope isolation;
4. state-conditioned differentiation.

The deterministic assessment result is separate from relying-party promotion policy. A model judge, if ever attached, is diagnostic only and cannot be the source of the deterministic result.

## Maintainer questions already incorporated

The design must preserve three requirements raised on #298:

1. Retriever pinning includes the embedding model and quantization, not merely a library version.
2. Private-store evidence must distinguish identity/provenance from independent rerunnability.
3. Assessment result and relying-party consequence must be separate, so the first external tool does not silently become a new conformance requirement.

## Current fork implementation

The branch currently contains:

- the design record in `docs/memory-checkpoint-assessment.md`;
- preliminary Pydantic artifact and adapter models in `python/src/agent_manifest/_memory_assessment.py`;
- a deterministic reference harness;
- focused tests in `python/tests/test_memory_assessment.py`.

Known implementation commits before this preparation record:

- `40dc171424f977fdb4811948465e44cec169ba47` design draft;
- `1c7176c55c41c965d6608f6181219fc38136e03a` result/verifiability separation;
- `cefb7951c779b0e38685ec014901faf97863497c` preliminary harness;
- `c1210d73548193a8f1c5a1773c162fde6cae8a7e` preliminary focused tests.

## Hardening backlog before submission

The next implementation pass should address all of the following before an upstream PR is considered:

- freeze Pydantic evidence inputs against mutation during a run;
- allow unsupported/unknown adapters to omit a deterministic tie policy while still requiring one for deterministic eligibility;
- require timezone-aware `assessed_at` values;
- include scope labels in repeatability identity because they are load-bearing for confidentiality isolation;
- pass deep-copied retrieval requests to adapters so an adapter cannot mutate later trials;
- surface confidentiality failures even when the probe is diagnostic/non-required;
- add negative tests for correction, anchor, scope, and state-conditioned failures;
- add tests for profile/configuration digest changes and retrieval-state digest changes;
- add mutation-resistance tests;
- add a second independently shaped deterministic retriever adapter;
- add deterministic public reference vectors;
- run the repository's complete validation gates in a proper repository/CI environment.

## Canonicalization dependency

Agent Manifest issue #322 reports that the repository's shared canonicalization implementation is not fully RFC 8785 conformant. The preliminary assessment harness currently reuses the repository canonicalizer for content-addressed assessment inputs.

Until #322 is resolved, the assessment work must treat canonicalization as an explicit interoperability dependency rather than assuming the current helper is a standards-grade primitive.

Before submission, add cross-implementation canonicalization vectors around every assessment digest that is intended to be portable. Do not create a second canonicalization algorithm inside the assessment harness.

## Vector discipline

Use the independence principle described in trace-spec#124: a rule should not be considered robustly covered merely because one fixture names it. Where practical, provide at least two vectors that can fail under different implementation defects.

The first public vector set remains reference assessment vectors, not AgentTrust conformance vectors, unless maintainers explicitly decide otherwise.

## Precommitted redesign/stop criteria

Materially redesign or stop this contribution if any of the following is demonstrated:

1. the artifact necessarily duplicates an AgentTrust normative primitive instead of composing with it;
2. stable framework-neutral assessment identity cannot support the four invariants without semantic or LLM inference;
3. evidence cannot remain structurally separate from deployment policy;
4. the first release requires a new signature/envelope standard;
5. deterministic 0.1 cannot support at least two independently shaped retrieval implementations without framework-specific semantics dominating;
6. maintainers move the work to another layer/repository and the artifact boundary cannot survive that move;
7. a concrete counterexample receives `pass` while violating a declared invariant under the same bound inputs and retriever profile.

## Validation status

Do not claim full repository validation yet. Focused preliminary tests have passed in an isolated environment, but the full upstream gate set has not been executed against this branch in a complete repository runner.

Required before submission:

- `pytest -v`;
- `mypy src/agent_manifest`;
- `ruff check src/ tests/`;
- `bandit -r src/agent_manifest`.

## Eventual upstream PR boundary

If and only if a maintainer explicitly welcomes the contribution and the preparation gates above are satisfied, prepare a narrow PR with:

- What;
- Why;
- Spec impact: none;
- Test plan;
- DCO.

Link #298, but do not automatically close it unless maintainers indicate the artifact/harness work completes the tracker.

Signed-off-by: Kevin Knapp <krknapp@gmail.com>
