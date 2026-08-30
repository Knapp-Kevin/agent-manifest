# MemoryCheckpointAssessment/0.1 design

> **Status: non-normative implementation design for issue #298.** Maintainer feedback now explicitly authorizes implementation against the reconciled applicability model. This artifact and its reference gate do not change Agent Manifest conformance and do not grant checkpoint approval.

Detailed reconciliation records live in:

- `docs/contrib/298-maintainer-feedback-reconciliation.md`
- `docs/contrib/298-adversarial-contract-review.md`
- `docs/contrib/298-memory-checkpoint-assessment-design-reconciled.md`
- `docs/contrib/298-reconciliation-verdict.md`
- `docs/contrib/298-maintainer-confirmation-2026-08-30.md`

## Narrow claim

`MemoryCheckpointAssessment/0.1` evaluates retrieval behavior over a candidate memory checkpoint under explicitly bound inputs, probes, and retriever configuration.

It does not prove that stored content is true, that a model answer is correct, that a memory write was authorized, that the producer is honest, that the checkpoint is safe in every sense, or that the checkpoint should be deployed.

The deterministic gating path never uses an LLM judge. A model judge, if attached later, is diagnostic only.

## Five concepts that must remain separate

The design now treats these as distinct:

1. **Evidence validity**: is the assessment artifact well-formed and correctly bound to what it claims?
2. **Behavioral outcome**: did the required probes produce `pass`, `fail`, or `indeterminate`?
3. **Control applicability**: is this the assessment evidence required by the adopted approval policy for the relevant checkpoint, probe suite, retriever profile, retrieval state where required, and evidence window where required?
4. **Approval admissibility**: does this adopted gate permit the approval action to continue?
5. **Historical/audit state**: what actually happened, including an approval that should have been blocked?

A valid behavioral `fail` remains valid evidence. A valid `indeterminate` remains evidence that the relevant behavioral property was not established. Neither result is rewritten into another state merely to express policy consequence.

## Artifact versus policy

The load-bearing split is:

> assessment artifact = what was evaluated and what happened
>
> approval policy = what must have been evaluated before this approval action may occur

The assessment artifact does not contain deployment authority.

The separate reference gate evaluator consumes an explicit policy requirement plus presented assessment artifacts. That evaluator reports only whether this one adopted gate is satisfied. It does not approve a checkpoint.

## Applicability

Applicability exists to prevent silent bypass by:

- omitting the assessment;
- presenting an assessment for another candidate checkpoint;
- presenting an assessment from another probe suite;
- presenting an assessment under another retriever profile;
- presenting another retrieval-state binding when the policy requires an exact one;
- presenting evidence outside a policy-declared assessment window.

When an assessment does not match the adopted gate, it does not become invalid evidence. It simply does not satisfy that gate.

No applicable assessment is therefore a policy failure, not an evidence failure.

## Adopted gate behavior

The reference assessment gate is pass-only:

- one or more applicable `pass` results, with no presented applicable non-pass result, satisfy this gate;
- an applicable `fail` does not satisfy the gate;
- an applicable `indeterminate` does not satisfy the gate;
- no applicable assessment does not satisfy the gate.

`pass` never grants checkpoint approval. It only satisfies this one adopted control. All other approval requirements remain independent.

If multiple applicable assessments are presented, any presented applicable `fail` or `indeterminate` keeps the gate closed. The 0.1 artifact does not prove that no other conflicting assessment was performed and withheld. Completeness or anti-selective-disclosure guarantees require a later registry or transparency mechanism.

## Historical preservation

A control violation must remain auditable.

If a checkpoint is cryptographically sound and an assessment is valid, but an approval occurs despite an applicable non-passing result, the system must remain capable of representing all of those facts. Rewriting the checkpoint or assessment into invalidity would destroy the evidence needed to prove the governance violation.

## Behavioral outcome

Per-probe and aggregate outcomes remain:

- `pass`
- `fail`
- `indeterminate`

`indeterminate` is a placeholder name for a first-class "not established" state. Maintainer feedback explicitly asks us to preserve the semantics while allowing the shared AgentTrust vocabulary to be renamed later.

Material unavailability is not itself a behavioral `indeterminate` reason. A private-store run may still produce a behavioral `pass` or `fail`; material availability affects independent rerun strength.

## Retriever pinning

The retriever profile remains content-addressed and binds the load-bearing retrieval path, including where applicable:

- implementation identity and version/source revision;
- embedding model identity and revision;
- quantization or precision mode;
- tokenizer identity;
- query preprocessing;
- distance metric;
- index implementation and build configuration;
- filtering rules;
- top-k and truncation rules;
- reranker identity/configuration;
- deterministic tie policy;
- deterministic seed;
- adapter and harness version;
- declared opaque components.

A deterministic profile must declare an explicit deterministic tie policy. The harness records repeatability evidence with an engineering floor of 20 trials per unique request/state/profile combination.

## Stable identity and initial probes

The harness uses stable logical item identity and version/content digests rather than semantic similarity to decide whether the same memory item persisted across states.

The initial invariant classes remain:

1. correction precedence;
2. anchor preservation;
3. scope isolation;
4. state-conditioned differentiation.

Scope-isolation failures retain confidentiality severity rather than being flattened into generic behavioral regression.

## Reproducibility and material access

Material access currently records whether rerun material is public, restricted, or unavailable to the verifier. This remains separate from behavioral outcome.

Earlier maintainer feedback explicitly endorsed `public-reproducible`, `restricted-reproducible`, and `attested-run-only` as useful evidence modes. The latest confirmation did not settle the exact 0.1 serialization or authenticated producer-assertion mechanism for those modes. The current implementation therefore does not invent one.

In particular, `attested-run-only` must not be represented as cryptographically attributable until an accepted authenticated wrapper or producer assertion exists.

## Canonicalization dependency

Assessment digests reuse the repository canonicalization primitive rather than inventing a second algorithm. Current upstream `main` has already corrected the UTF-16 object-key ordering and exponent-formatting defects originally tracked by Agent Manifest issue #322, so those assessment-boundary guards are now ordinary passing regression tests.

Issue #322 remains open because the shared canonicalizer still over-escapes U+2028. One strict expected-failure assessment test retains that live interoperability dependency. Until the remaining RFC 8785 defect is resolved, assessment digests must not be described as independently portable across conformant implementations for inputs that exercise the unresolved escaping axis.

## First contribution boundary

The intended first contribution remains external and non-normative. It may include:

- typed assessment evidence models;
- deterministic retriever adapter protocol;
- deterministic reference harness;
- public positive and negative vectors;
- independently shaped retriever fixtures;
- the separate reference applicability gate and its tests;
- documentation of known limitations and unresolved provenance questions.

It must not:

- modify `spec/` unless maintainers explicitly request it;
- add an `approve_checkpoint()` or deployment-authority API;
- turn `pass` into approval;
- turn `fail` into invalid evidence;
- turn `indeterminate` into `fail`;
- add TRACE/runtime integration to this PR;
- invent a second signature/envelope architecture.

## Current implementation sequence

1. implement the confirmed applicability contract on the fork;
2. run focused adversarial tests;
3. run full repository validation against current upstream;
4. review schema and documentation diffs for unintended scope growth;
5. prepare a narrow upstream PR only after the fork evidence is clean.