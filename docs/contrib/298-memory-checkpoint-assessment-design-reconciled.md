# MemoryCheckpointAssessment/0.1 reconciled design draft

> **Status: internal reconciliation draft for issue #298.** This document incorporates maintainer feedback from issue comment `5418827808` and the internal adversarial review. It does not change Agent Manifest conformance, does not authorize checkpoint promotion, and does not modify the frozen implementation branch.

## Design objective

`MemoryCheckpointAssessment/0.1` is an external evidence artifact and reference harness for evaluating retrieval behavior across a candidate memory checkpoint transition.

Its narrow claim is:

> Under the bound checkpoint states, probe suite, retriever profile, and recorded deterministic procedure, the assessment observed the recorded retrieval behavior and evaluated the declared predicates to the recorded behavioral result.

The artifact is not a certificate that memory is safe, true, complete, authorized, or suitable for deployment. It does not adjudicate model-answer correctness. Agent Manifest continues to establish the checkpoint protocol's integrity, ordering, freshness, and budget properties.

A behavioral assessment composes with those properties rather than replacing them.

## Five concepts that must not collapse

### 1. Evidence validity

Evidence validity answers:

> Is this assessment artifact well-formed, internally consistent, and validly bound to the inputs and observations it claims?

A valid artifact may report:

- `pass`
- `fail`
- `indeterminate`

A behavioral `fail` is not invalid evidence.

Malformed, contradictory, unverifiable, or improperly bound evidence is a separate condition and must not be converted into behavioral `fail` merely because both conditions are undesirable.

### 2. Behavioral outcome

Behavioral outcome answers:

> Did the declared retrieval predicates pass, fail, or remain indeterminate under the bound assessment conditions?

Per-probe and aggregate values are:

- `pass`
- `fail`
- `indeterminate`

The initial aggregate rule remains:

1. any required `fail` produces aggregate `fail`;
2. otherwise any required `indeterminate` produces aggregate `indeterminate`;
3. otherwise aggregate `pass`.

The result is evidence. It does not itself grant approval authority.

### 3. Control applicability

Control applicability answers:

> Is this assessment the evidence that the approval policy required for this candidate checkpoint decision?

The artifact binds what was actually assessed. A separate approval policy identifies what must be assessed.

An approval policy that adopts this control should identify or constrain at least:

- assessment type and version;
- candidate checkpoint digest;
- baseline checkpoint digest or acceptable baseline relation;
- probe-suite digest or approved suite identity;
- retriever-profile digest or approved profile constraints;
- freshness or maximum evidence age when relevant;
- reproducibility/evidence-strength requirement when relevant;
- producer-provenance requirement when relevant.

Applicability is the match between required evidence and presented evidence.

This distinction is load-bearing. A producer must not be able to evade a prior failure by omitting the assessment, substituting a weaker probe suite, using a different retriever profile, or presenting evidence over a different candidate state after the approval policy has already defined what evidence is required.

### 4. Approval admissibility

Approval admissibility answers:

> Given the applicable evidence and all other approval prerequisites, may the deployer approve this candidate checkpoint?

Maintainer feedback settles one rule:

> An applicable behavioral `fail` makes the candidate checkpoint not approvable. The deployer MUST NOT approve it.

This rule binds the approval action, not the validity of the assessment evidence and not the cryptographic validity of the checkpoint.

The inverse does not follow:

- `pass` does not mean approved;
- `pass` means only that this assessment does not supply a disqualifying behavioral failure;
- all other approval prerequisites remain independently necessary.

The harness therefore must not expose `approve_checkpoint()` or another API that grants deployment authority.

When a deployment or relying-party policy adopts this assessment as an approval gate, it must define what valid applicable evidence satisfies that gate. A conservative pass-only form is:

```text
assessment gate satisfied =
    valid assessment evidence
    AND applicable assessment evidence
    AND behavioral result == pass
```

This form naturally leaves `fail`, `indeterminate`, malformed evidence, missing evidence, and inapplicable evidence unable to satisfy the adopted gate without pretending those states are semantically identical.

The latest maintainer feedback explicitly rules on `fail` but does not explicitly settle whether 0.1 itself should mandate the pass-only form for `indeterminate`. That point remains for maintainer confirmation.

### 5. Historical and audit state

Historical state answers:

> What actually happened, including governance actions that should have been blocked?

The evidence model must be able to represent this combination without contradiction:

```text
checkpoint integrity: valid
checkpoint consistency proof: valid
assessment evidence: valid
assessment result: fail
assessment applicability: applicable
approval action: occurred
approval control: violated
```

An improper approval does not justify deleting or rewriting the failing assessment. The failure is exactly the evidence an auditor needs to understand the control violation.

## Optional external tool versus non-optional adopted gate

The first contribution remains external and non-normative with respect to universal Agent Manifest conformance. It does not establish that every deployment everywhere must use `MemoryCheckpointAssessment/0.1`.

That does not make the result advisory after a deployment or relying-party policy adopts the assessment as an approval control.

The intended distinction is:

```text
control adoption: external policy decision
control execution after adoption: non-advisory
```

Once an approval policy requires an applicable assessment, the operator cannot treat a detected `fail` as a warning and approve anyway.

Likewise, once the gate requires valid applicable assessment evidence, omission or substitution cannot silently satisfy the gate.

A future Agent Manifest specification may choose to require this control more broadly. That is a separate normative decision and is not smuggled into the 0.1 artifact.

## Retriever profile

The retriever profile is content-addressed and binds the retrieval path that can change observed context selection.

The profile includes, where applicable:

- implementation identity and version or source revision;
- adapter version;
- harness version;
- embedding model identity and immutable revision or digest;
- embedding quantization or precision mode;
- tokenizer identity/version;
- query normalization and preprocessing;
- similarity or distance function;
- index implementation and build configuration;
- namespace, tenant, role, project, task, and other filtering rules;
- top-k;
- truncation rules;
- reranker identity/configuration;
- deterministic tie policy;
- deterministic seeds;
- opaque components that cannot be independently inspected.

A profile digest proves which declaration is bound. It does not prove that an opaque remote backend actually ran that declaration.

The maintainer explicitly endorsed full retrieval-path pinning, including deterministic tie behavior.

## State-specific retrieval material

The shared retriever profile describes configuration expected to remain fixed across the baseline/candidate comparison.

State-specific derived retrieval material is bound separately because the candidate is expected to differ from the baseline.

Example:

```yaml
baseline_state:
  checkpoint_digest: sha256:...
  retrieval_state_digest: sha256:...
  indexed_item_count: 120

candidate_state:
  checkpoint_digest: sha256:...
  retrieval_state_digest: sha256:...
  indexed_item_count: 123
```

`retrieval_state_digest` may identify an immutable index snapshot or another adapter-defined retrieval representation.

If load-bearing state changes after assessment, the previous assessment is not applicable to the changed state.

## Deterministic capability and repeatability evidence

The adapter/profile declares whether it can satisfy the 0.1 deterministic path:

- `deterministic`
- `unsupported_or_unknown`

A declaration alone is not proof.

The harness records repeatability evidence for each unique state/request/profile combination. The initial engineering floor remains 20 identical runs.

Example:

```yaml
repeatability:
  trials: 20
  distinct_orderings_observed: 1
  observed_status: stable
  tie_events_observed: null
```

This is engineering evidence of observed repeatability, not proof of mathematical determinism.

A profile is eligible for the deterministic result path only when:

- the adapter declares deterministic capability;
- the profile binds an explicit deterministic tie policy;
- required repeatability trials ran;
- observed ordering remained stable across those trials.

If the backend cannot guarantee deterministic tie resolution, deterministic capability is `unsupported_or_unknown`.

## Stable item identity

The harness does not infer logical memory identity from prose similarity.

Adapters emit stable logical assessment identity plus content/version identity:

```python
class RetrievedItem:
    item_key: str
    item_version_digest: str
    rank: int
    scope_labels: tuple[str, ...]
```

Floating retrieval scores are not load-bearing in 0.1.

Probe references declare whether an item is required in baseline, candidate, or both.

If a transition invariant requires stable identity across both states and the adapter cannot resolve it consistently, the probe is `indeterminate` with reason `id_churn`.

Systems that regenerate all logical identities on reindex cannot support these transition invariants unless they provide a stable external identity mapping.

## Material access and reproducibility mode are separate

### Material access

`material_access` describes whether a verifier can obtain the material needed to rerun the assessment in its current context:

- `public`
- `restricted`
- `unavailable_to_verifier`

Material access does not determine behavioral `pass`, `fail`, or `indeterminate`.

### Reproducibility/evidence-strength mode

`reproducibility_mode` describes the class of claim the assessment makes about rerunnability or producer assertion.

Maintainer-endorsed candidate values are:

- `public-reproducible`
- `restricted-reproducible`
- `attested-run-only`

These modes are not synonyms for material access.

`public-reproducible` means the complete bound material and pinned retrieval path necessary for independent rerun are publicly obtainable.

`restricted-reproducible` means independent rerun is possible for an authorized verifier with access to the required material.

`attested-run-only` means independent rerun is not promised and the load-bearing claim is attributable to the producer that performed the run.

The exact schema relationship between `material_access` and `reproducibility_mode` remains to be finalized. The concepts should remain separate unless maintainer review establishes a reason to combine them.

## Provenance boundary for `attested-run-only`

`attested-run-only` cannot honestly mean merely:

> an unsigned JSON payload says somebody ran this assessment.

The maintainer's formulation is attributable: a signer ran the suite against the checkpoint and obtained the result.

The current Agent Manifest v0.2 COSE envelope cannot simply be reused verbatim. Its protected `typ` and `content type` are explicitly bound to Agent Manifest documents, and its verifier rejects unexpected document types to prevent cross-document reinterpretation.

TRACE provides a separate signed evidence architecture, but TRACE/runtime integration is explicitly out of scope for this first contribution.

Therefore 0.1 must not invent an assessment-specific signature architecture merely to make `attested-run-only` self-contained.

Pending maintainer confirmation, acceptable shapes include:

1. implement public/restricted reproducible modes first and reserve `attested-run-only` until an authenticated envelope is selected;
2. permit `attested-run-only` only when an external authenticated producer assertion accompanies the assessment payload;
3. use a maintainer-selected existing generic signed-statement primitive if one is identified without expanding this PR into TRACE or a new envelope standard.

Until one of those conditions is met, an unsigned payload must not overclaim producer attestation.

## Runtime consistency observations

The artifact may record execution observations that make false profile declarations easier to detect on rerun, such as runtime build identity or embedding dimensionality.

These are consistency observations, not cryptographic attestation.

A later verifier that discovers a profile/runtime mismatch should report a verification mismatch rather than rewriting the original behavioral result to `indeterminate`.

## Probe suite and precommitment

A probe suite is versioned and content-addressed.

The harness freezes the suite before executing a candidate run and prevents in-process mutation after results begin.

A suite digest proves which suite was used. It does not prove that the operator selected the suite before observing candidate behavior.

Likewise, a retriever-profile digest proves which profile was assessed. It does not prove that the producer did not choose the profile opportunistically after seeing another result.

Therefore the approval layer must precommit the assessment identity or acceptable constraints before evaluating gate satisfaction.

This is the mechanism that makes control applicability meaningful and prevents substitute-suite/profile bypass.

## Initial invariant classes

The initial deterministic invariant classes remain:

1. correction precedence;
2. anchor preservation;
3. scope isolation;
4. state-conditioned differentiation.

### Correction precedence

The probe names the superseded item and correcting item and declares the expected inclusion/order rule. The harness does not infer correction semantics from prose.

### Anchor preservation

The probe declares an anchor key and baseline precondition.

If the baseline precondition is not satisfied, the probe is `indeterminate` with reason `baseline_precondition_unmet`.

If the baseline satisfies the precondition and the candidate violates the declared anchor requirement, the probe is `fail`.

### Scope isolation

The probe declares active scope and forbidden item keys or scope labels.

Retrieving forbidden material is `fail` with severity `confidentiality`.

The aggregate artifact surfaces whether any confidentiality failure occurred, including diagnostic/non-required probes.

### State-conditioned differentiation

The paired-state probe declares explicit item inclusion, exclusion, or rank relations between states.

No opaque semantic-distance threshold is used in the deterministic 0.1 core.

## Indeterminate semantics

Every `indeterminate` result requires an explicit reason.

Initial reasons remain:

- `adapter_unsupported`
- `repeatability_unstable`
- `repeatability_not_run`
- `baseline_precondition_unmet`
- `id_churn`

Material unavailability is not an indeterminate reason. A private store can still produce completed behavioral evidence.

A profile/runtime mismatch discovered during later verification is also not an indeterminate reason. It is a verification problem.

The latest maintainer feedback explicitly makes `fail` approval-blocking. It does not explicitly state whether every `indeterminate` must also block approval.

The reconciled design therefore preserves `indeterminate` as a distinct behavioral state and proposes expressing its operational consequence through gate satisfaction rather than reclassifying it as `fail`.

A pass-only gate would make `indeterminate` unable to satisfy the gate while preserving the distinction. Maintainer confirmation is required before that rule is presented as part of the accepted 0.1 contract.

## Failure evidence and approval control

A behavioral `fail` must remain fully representable and durable.

The artifact itself does not perform approval.

The correct composition is:

```text
assessment artifact:
    reports valid evidence and behavioral result

approval gate:
    checks artifact validity
    checks applicability against precommitted requirements
    enforces that applicable fail cannot approve

approval system:
    evaluates all remaining independent prerequisites
```

This separation prevents two opposite errors:

1. advisory failure, where the signal exists but cannot prevent the action it was designed to control;
2. authority inflation, where a behavioral assessment begins granting deployment permission it does not own.

## Supersession and repeated assessments

Assessment history is append-only evidence for audit purposes.

A later assessment does not mutate an earlier result.

Applicability of a later assessment depends on policy and bound inputs.

Examples:

- a changed candidate checkpoint requires new evidence because the old artifact binds a different candidate;
- an authorized policy change to the required suite/profile may make new evidence applicable, but the earlier result remains historical evidence;
- contradictory outcomes under the same candidate, suite, profile, and deterministic procedure require investigation rather than "latest result wins."

The artifact should not contain a producer-controlled field that unilaterally erases or invalidates an earlier failure.

## Lifecycle and staleness

The artifact records `assessed_at`.

There is no intrinsic TTL in the behavioral artifact.

Evidence remains a statement about its exact bound inputs. It becomes inapplicable when a load-bearing required value changes.

An approval policy may impose maximum evidence age without changing the original artifact's meaning.

## Gaming and visibility

Known public probes can be optimized against. 0.1 does not claim otherwise.

Restricted and held-out operational suites may reduce gaming but reduce public rerunnability.

A producer-selected suite cannot by itself establish that no adverse result exists under another suite. The approval policy must identify the required suite or approved suite constraints before result selection.

Rotated suites, held-out acceptance suites, statistical retrieval systems, and nondeterministic profiles remain future work.

## Signing and envelope boundary

The behavioral payload must not invent a second cryptographic architecture beside AgentTrust's existing direction.

An unsigned assessment payload can carry producer metadata but cannot prove producer provenance.

If an authenticated wrapper is later selected, evidence validity should distinguish payload validity from wrapper/provenance verification rather than converting signature failure into behavioral `fail`.

## Illustrative behavioral artifact

This is a logical shape only. It is not yet an approved wire schema.

```yaml
type: MemoryCheckpointAssessment
version: "0.1"

baseline_state:
  checkpoint_digest: sha256:...
  retrieval_state_digest: sha256:...
  indexed_item_count: 8

candidate_state:
  checkpoint_digest: sha256:...
  retrieval_state_digest: sha256:...
  indexed_item_count: 9

probe_suite_digest: sha256:...
retriever_profile_digest: sha256:...
assessed_at: "2026-08-27T00:00:00Z"

material_access: restricted
reproducibility_mode: restricted-reproducible

coverage:
  required_probe_count: 4
  passed: 4
  failed: 0
  indeterminate: 0
  indeterminate_rate: 0.0

security_flags:
  contains_confidentiality_failure: false

result: pass
```

Approval policy requirements are intentionally not embedded in this artifact. The artifact records what happened. The gate records what had to happen before approval.

## Illustrative external approval requirement

This shape exists only to make the composition concrete. It is not proposed as an Agent Manifest field in the first PR.

```yaml
memory_checkpoint_assessment_requirement:
  assessment_type: MemoryCheckpointAssessment
  assessment_version: "0.1"
  candidate_checkpoint_digest: sha256:...
  baseline_checkpoint_digest: sha256:...
  probe_suite_digest: sha256:...
  retriever_profile_digest: sha256:...
  required_result: pass
  maximum_age_seconds: 3600
```

The relationship is:

```text
assessment artifact = what was evaluated
approval requirement = what must be evaluated
```

## First implementation boundary after reconciliation

No implementation change should be made until this reconciled design receives an internal scenario pass and the unresolved maintainer questions are prepared clearly.

If accepted, the implementation should continue to include:

- typed Pydantic evidence models;
- deterministic adapter protocol;
- public deterministic fixture adapter;
- repository-shared canonical digests;
- positive and negative vectors for the four initial invariants;
- multiple independently shaped retrieval implementations in validation;
- explicit evidence-validity checks;
- no model judge in deterministic gating;
- no SDK approval/promotion function;
- no TRACE/runtime integration;
- no new signature/envelope standard.

Likely revisions after design confirmation include:

- separate reproducibility mode from material access;
- formalize applicability inputs in documentation and test fixtures without granting the artifact authority;
- make the mandatory consequence of applicable `fail` explicit;
- preserve `indeterminate` as distinct from `fail`;
- add tests that valid failing evidence remains valid;
- add tests that substitute suite/profile evidence cannot satisfy a precommitted gate example;
- add tests that pass never grants approval by itself;
- add tests that historical control violations remain representable.

## Maintainer questions that remain after reconciliation

The eventual design-boundary response should keep questions narrow and avoid re-litigating points already settled.

1. **Indeterminate:** Is the intended 0.1 gate pass-only, so an applicable `indeterminate` cannot satisfy approval, while remaining distinct from behavioral `fail`?
2. **Reproducibility dimensions:** Should the endorsed `public-reproducible`, `restricted-reproducible`, and `attested-run-only` modes coexist with `material_access` as separate dimensions?
3. **Attested-run provenance:** Should `attested-run-only` be reserved until an accepted authenticated wrapper exists, or may 0.1 define it as requiring an external authenticated producer assertion without standardizing that wrapper?
4. **Control adoption:** Is the intended first-release boundary that adoption of the assessment gate remains external/non-normative, but once adopted a required applicable assessment is non-advisory and an applicable `fail` prohibits approval?

## Precommitted kill criteria

The existing kill criteria remain active.

Redesign or abandon the wedge if:

1. the artifact necessarily duplicates an existing AgentTrust normative primitive;
2. framework-neutral stable assessment identity cannot support the four initial invariants without semantic/LLM inference;
3. evidence cannot be separated from approval policy in actual code;
4. the first release requires a new signature/envelope standard;
5. deterministic 0.1 cannot support at least two independently shaped retrievers without framework semantics dominating it;
6. repository/layer placement destroys the artifact boundary rather than merely moving code;
7. a candidate can obtain `pass` while violating a declared invariant under the same bound inputs/profile.

The reconciliation introduces an additional practical stop condition:

8. if approval applicability cannot be defined tightly enough to prevent omission or substitute-evidence bypass, the design is not a meaningful control and must not be presented as one.
