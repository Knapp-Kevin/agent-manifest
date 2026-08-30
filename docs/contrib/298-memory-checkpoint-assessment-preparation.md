# MemoryCheckpointAssessment/0.1 preparation record

Status: maintainer-authorized implementation in current-upstream fork validation

Upstream tracker: `agentrust-io/agent-manifest#298`
Current implementation branch: `feat/memory-checkpoint-assessment-298-applicability`
Prior feature branch: `feat/memory-checkpoint-assessment-298`
Fork-only validation PR: `Knapp-Kevin/agent-manifest#2`

## Current upstream boundary

The previous waiting condition is satisfied. Imran confirmed the reconciled five-concept model and explicitly said to change the harness against it:

https://github.com/agentrust-io/agent-manifest/issues/298#issuecomment-5470371301

The implementation may therefore proceed.

We are still intentionally keeping the current changes on the fork until the revised implementation is adversarially reviewed and the repository validation gates are green against current upstream. Maintainer authorization to proceed is not treated as a reason to skip our own evidence boundary.

Do not retarget either fork-only validation PR upstream. A future upstream PR should be newly prepared from the validated implementation state.

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

- `docs/memory-checkpoint-assessment.md`, aligned to the reconciled design;
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

## Current-upstream synchronization

The branch has been merged with `agentrust-io/agent-manifest` main at:

`eb747f5fd610a8d7fa360e52faaea5db578e6b34`

through fork-only integration PR `Knapp-Kevin/agent-manifest#3`.

This matters because current upstream contains 23 commits beyond the prior fork baseline, including security-verifier changes, CLI changes, governance/release changes, and partial corrections to the shared RFC 8785 canonicalizer.

The earlier pre-sync fork validation was green:

- CI run `33327953937` passed all lanes;
- CodeQL run `33327953923` passed;
- Python 3.11 Ubuntu collected 1238 tests: `1229 passed, 6 skipped, 3 xfailed`;
- total coverage 89.61 percent;
- `_memory_assessment.py` coverage 93 percent;
- `_memory_assessment_gate.py` coverage 87 percent.

Those results establish the reconciled implementation was internally sound before the upstream merge. They are not the final submission evidence. Final evidence must come from the post-sync head.

## Important limits still preserved

### Reproducibility/provenance

Earlier maintainer feedback endorsed `public-reproducible`, `restricted-reproducible`, and `attested-run-only` as useful modes. The latest confirmation did not settle the exact serialized 0.1 representation or authenticated producer assertion for `attested-run-only`.

Do not invent that cryptographic provenance mechanism in this slice.

### Completeness/selective disclosure

A standalone assessment proves the presented run. It does not prove that no conflicting assessment was performed and withheld. Strong completeness would require a later registry or transparency mechanism.

### Canonicalization

Agent Manifest issue #322 remains an interoperability dependency, but the dependency has narrowed on current upstream. UTF-16 object-key ordering and exponent normalization are now corrected on `main` and are ordinary passing assessment-boundary tests. U+2028 over-escaping remains unresolved, so one strict expected-failure test retains that live defect.

Do not claim independent cross-implementation RFC 8785 portability for assessment inputs exercising the unresolved escaping axis until #322 is fully resolved.

### TRACE/runtime scope

TRACE and runtime-evidence integration remain separate follow-on work. They must not expand this first contribution.

## Validation sequence before upstream submission

1. run focused memory-assessment and applicability tests after the current-upstream merge;
2. run Ruff, strict mypy, Bandit, pip-audit, build/twine, AGT governance, and the supported Python/OS test matrix;
3. require CodeQL to pass;
4. preserve the one live strict #322 expected-failure guard and require the two resolved guards to pass normally;
5. inspect documentation/schema diffs for unintended normative scope growth;
6. only then prepare a narrow upstream PR.

A future upstream PR should state `Spec impact: none` unless maintainers explicitly ask for a specification hook.