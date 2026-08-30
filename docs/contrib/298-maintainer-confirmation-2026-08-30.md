# Issue #298 maintainer confirmation - 2026-08-30

Upstream tracker: `agentrust-io/agent-manifest#298`

Maintainer response: https://github.com/agentrust-io/agent-manifest/issues/298#issuecomment-5470371301

Status: implementation changes are authorized. Continue on the fork, validate the revised boundary, then decide whether the implementation is ready for an upstream pull request.

## Confirmed contract

Imran confirmed the five-concept reading developed during the reconciliation pass:

1. **Evidence validity**: whether an assessment artifact is well-formed and correctly bound to what it claims.
2. **Behavioral outcome**: whether the bound probes produced `pass`, `fail`, or `indeterminate`.
3. **Control applicability**: whether the presented assessment is the assessment required by the adopted approval policy for the relevant checkpoint, probe suite, retriever profile, and evidence window.
4. **Approval admissibility**: whether the approval action may proceed after evaluating the applicable evidence.
5. **Historical/audit state**: what actually happened, including an approval that should have been blocked.

These concepts must not be collapsed into one verification result.

## Applicability is load-bearing

The maintainer explicitly confirmed three bypass shapes:

- omit the assessment;
- present an assessment from a different probe suite;
- assess under a different retriever profile.

Those are control failures, not evidence failures. The artifact may remain perfectly valid evidence of a different assessment while failing to satisfy the adopted approval gate.

The implementation therefore keeps this split:

> assessment artifact = what was evaluated and what happened
>
> approval policy = what must have been evaluated before this approval action may occur

The reference gate evaluator must treat absence of applicable evidence as a policy failure. It must not silently convert an omitted check into a passed check.

## Behavioral outcomes at an adopted gate

The gate is pass-only:

- applicable `pass` satisfies this gate only;
- applicable `fail` does not satisfy the gate;
- applicable `indeterminate` does not satisfy the gate;
- no applicable assessment does not satisfy the gate.

`pass` does not grant checkpoint approval. Other approval requirements remain independent.

`fail` and `indeterminate` remain distinct evidence outcomes. The implementation must not rewrite `indeterminate` into `fail` merely to achieve fail-closed operation.

Imran asked us to keep `indeterminate` with its current semantics while expecting the vocabulary may later be unified across AgentTrust. Its semantic meaning is first-class "not established" evidence, not a verdict.

## Historical preservation

A control violation must not rewrite historical evidence into invalidity.

If a checkpoint was cryptographically sound, an assessment was valid, and an approval occurred despite an applicable non-passing assessment, the historical record must remain capable of showing all of those facts. That preserved contradiction is what makes the governance violation auditable.

## Implementation consequence

The fork implementation now adds a separate non-normative applicability gate module rather than adding deployment authority to the assessment harness.

The gate evaluator:

- consumes an explicit `AssessmentGatePolicy` plus presented `MemoryCheckpointAssessment` artifacts;
- checks checkpoint, probe-suite, retriever-profile, optional retrieval-state, and optional evidence-window applicability;
- reports `no_applicable_assessment` explicitly;
- keeps `fail` and `indeterminate` distinct while allowing neither to satisfy an adopted gate;
- never exposes `approve_checkpoint()` or another deployment-authority API;
- never mutates the assessment artifact or checkpoint evidence.

## Still unresolved

The latest maintainer response did not answer the third question from the reconciliation comment concerning the exact 0.1 treatment of:

- keeping reproducibility mode distinct from `material_access` in the serialized artifact;
- authenticated provenance for `attested-run-only`.

Earlier maintainer feedback explicitly endorsed `public-reproducible`, `restricted-reproducible`, and `attested-run-only` as useful modes. However, the authenticated producer assertion for `attested-run-only` is not yet settled, and this implementation slice does not invent one.

Agent Manifest issue #322 also remains a portability dependency for repository-canonical digests. Do not claim independent RFC 8785 interoperability for assessment digests until that issue is resolved.

## Submission boundary

The previous "wait for maintainer welcome" gate is satisfied. The maintainer explicitly said to change the harness against the reconciled model.

That does not mean the current fork branch should be submitted blindly. The next sequence is:

1. implement the confirmed applicability contract on the fork;
2. run focused adversarial tests;
3. run the repository validation gates against the revised branch;
4. inspect the resulting artifact/schema diff and documentation for unintended scope growth;
5. only then prepare a narrow upstream pull request for review.

No TRACE/runtime integration belongs in this implementation slice.
