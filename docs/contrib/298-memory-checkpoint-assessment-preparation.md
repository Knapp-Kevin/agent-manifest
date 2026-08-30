# MemoryCheckpointAssessment/0.1 preparation record

Status: maintainer-authorized implementation in fork validation

Upstream tracker: `agentrust-io/agent-manifest#298`
Current implementation branch: `feat/memory-checkpoint-assessment-298-applicability`
Prior feature branch: `feat/memory-checkpoint-assessment-298`
Fork-only validation PR: `Knapp-Kevin/agent-manifest#1`

## Current upstream boundary

The previous waiting condition is satisfied. Imran confirmed the reconciled five-concept model and explicitly said to change the harness against it:

https://github.com/agentrust-io/agent-manifest/issues/298#issuecomment-5470371301

The implementation may therefore proceed.

We are still intentionally keeping the current changes on the fork until the revised implementation is adversarially reviewed and the repository validation gates are green. Maintainer authorization to proceed is not treated as a reason to skip our own evidence boundary.

Do not retarget the existing fork-only draft PR upstream. It remains a CI surface for the fork. A future upstream PR should be newly prepared from the validated implementation state.

## Confirmed architecture

Keep these separate:

1. evidence validity;
2. behavioral outcome;
3. control applicability;
4. approval admissibility;
5. historical/audit state.

The load-bearing split is:

> assessment artifact = what was evaluated and what happened
>
> approval policy = what must have been evaluated before this approval action may occur

The assessment artifact is evidence. It does not grant deployment authority.

## Adopted assessment gate semantics

When a deployment adopts the reference assessment gate:

- applicable `pass` satisfies this gate only;
- applicable `fail` does not satisfy the gate;
- applicable `indeterminate` does not satisfy the gate;
- absence of applicable evidence does not satisfy the gate.

`fail` remains valid behavioral evidence and does not invalidate an otherwise cryptographically sound checkpoint.

`indeterminate` remains a first-class "not established" state. It is not rewritten to `fail`. Maintainer feedback notes that the shared AgentTrust vocabulary may later rename this state, but its semantics should remain stable.

A `pass` never grants approval. Other approval checks remain independent.

## Applicability bypasses now covered

The reference gate must make these cases visible rather than treating them as successful checks:

- assessment omitted;
- wrong candidate checkpoint;
- wrong probe suite;
- wrong retriever profile;
- wrong retrieval-state binding when the policy requires one;
- assessment outside a policy-declared evidence window.

Those are policy/applicability failures, not evidence-validation failures.

## Current fork implementation

The implementation line contains:

- `docs/memory-checkpoint-assessment.md`, now aligned to the reconciled design;
- `docs/contrib/298-maintainer-feedback-reconciliation.md`;
- `docs/contrib/298-adversarial-contract-review.md`;
- `docs/contrib/298-memory-checkpoint-assessment-design-reconciled.md`;
- `docs/contrib/298-reconciliation-verdict.md`;
- `docs/contrib/298-maintainer-confirmation-2026-08-30.md`;
- `python/src/agent_manifest/_memory_assessment.py`, the evidence models and deterministic reference harness;
- `python/src/agent_manifest/_memory_assessment_gate.py`, the separate non-normative applicability gate;
- focused harness, hardening, artifact-shape, vector, canonicalization-dependency, and gate tests;
- deterministic public reference vectors;
- two independently shaped deterministic retriever fixtures.

## Important limits still preserved

### Reproducibility/provenance

Earlier maintainer feedback endorsed `public-reproducible`, `restricted-reproducible`, and `attested-run-only` as useful modes. The latest confirmation did not settle the exact serialized 0.1 representation or authenticated producer assertion for `attested-run-only`.

Do not invent that cryptographic provenance mechanism in this slice.

### Completeness/selective disclosure

A standalone assessment proves the presented run. It does not prove that no conflicting assessment was performed and withheld. Strong completeness would require a later registry or transparency mechanism.

### Canonicalization

Agent Manifest issue #322 remains an interoperability dependency. The harness reuses the repository canonicalizer and carries strict expected-failure tests for known RFC 8785 divergences. Do not claim independent cross-implementation RFC 8785 portability until #322 is resolved.

### TRACE/runtime scope

TRACE and runtime-evidence integration remain separate follow-on work. They must not expand this first contribution.

## Validation sequence before upstream submission

1. inspect the applicability implementation and focused tests;
2. run focused memory-assessment tests;
3. run Ruff, strict mypy, Bandit, pip-audit, build/twine, and the supported Python/OS test matrix;
4. preserve the strict #322 expected-failure guards;
5. inspect documentation/schema diffs for unintended normative scope growth;
6. only then prepare a narrow upstream PR.

A future upstream PR should state `Spec impact: none` unless maintainers explicitly ask for a specification hook.
