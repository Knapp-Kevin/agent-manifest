# Issue #298 adversarial contract review

Status: internal review. No implementation or upstream submission is authorized by this document.

Depends on: `docs/contrib/298-maintainer-feedback-reconciliation.md`

Frozen implementation baseline: `feat/memory-checkpoint-assessment-298` at `b34bf1b1de0d8a4495572b8f0775085ea12937ac`

## Executive finding

The maintainer's `MUST NOT approve` ruling is coherent with an external, non-normative assessment artifact only if the design distinguishes two things that the current draft does not yet model explicitly enough:

1. the assessment artifact, which records evidence and a behavioral outcome;
2. an approval-gate contract, which establishes when that evidence is required, which assessment is applicable, and what result satisfies the gate.

Without an applicability contract, the new failure consequence can be bypassed by omission or substitution:

- do not produce an assessment;
- produce one against a different probe suite;
- produce one against a different retriever profile;
- produce one against a different candidate state;
- present an invalid assessment and treat it as though no failure exists;
- rerun under a more permissive profile and present only the favorable result.

A rule that says only "if a failing assessment is present, do not approve" is therefore not a complete control.

The assessment artifact must remain evidence-only, but the approval layer needs enough precommitted policy to identify the evidence that can satisfy the control.

## Refined architecture

The review now distinguishes five concepts.

### 1. Evidence validity

Is the `MemoryCheckpointAssessment/0.1` artifact internally consistent, bound to its declared inputs, and valid under its artifact schema and verification rules?

Possible state examples:

- valid evidence with behavioral `pass`;
- valid evidence with behavioral `fail`;
- valid evidence with behavioral `indeterminate`;
- invalid or malformed evidence.

Behavioral failure must not be confused with invalid evidence.

### 2. Behavioral outcome

What did the assessment observe under the bound checkpoint states, probe suite, retriever profile, and deterministic procedure?

Values remain:

- `pass`
- `fail`
- `indeterminate`

This is descriptive evidence, not deployment authority.

### 3. Control applicability

Does this assessment satisfy the identity and policy requirements of the approval gate that is being evaluated?

At minimum, an approval policy that adopts memory behavioral assessment needs to identify or constrain:

- assessment type and version;
- candidate checkpoint digest;
- baseline checkpoint digest or acceptable baseline relation;
- required probe-suite digest or approved suite identity;
- required retriever-profile digest or approved profile constraints;
- freshness/age policy if one exists;
- evidence-strength/reproducibility requirements if relevant;
- provenance requirements if relevant.

The assessment artifact binds what was actually evaluated. The approval policy states what must have been evaluated. Applicability is the match between those two statements.

This relationship is necessary to prevent an operator from choosing the evidence after seeing the result.

### 4. Approval admissibility

If the assessment control is adopted for this approval decision, the approval gate is satisfied only by applicable evidence meeting the required behavioral condition.

The maintainer has explicitly established that an applicable `fail` cannot satisfy the gate and the checkpoint MUST NOT be approved.

A `pass` does not grant approval. It only satisfies this one gate.

The treatment of `indeterminate` should be expressed as gate satisfaction, not by pretending that `indeterminate` is behavioral `fail`.

A possible conservative rule is:

```text
assessment gate adopted
    + applicable valid assessment
    + result == pass
    = assessment gate satisfied
```

Under that shape, `fail`, `indeterminate`, malformed evidence, missing evidence, or inapplicable evidence all fail to satisfy the adopted gate, but for different reasons. This preserves semantic precision.

Whether 0.1 should mandate that exact pass-only gate or leave some non-fail states to an external policy remains a maintainer-boundary question.

### 5. Historical and audit state

The record of what happened must remain durable even when the approval action violated the gate.

An audit trail can coherently contain:

```text
checkpoint verification: valid
assessment evidence: valid
assessment result: fail
assessment applicability: applicable
approval action: occurred
approval control: violated
```

No component needs to be rewritten into invalidity merely because the combination exposes improper governance.

## Why applicability is load-bearing

Consider an approval policy that says only:

> A checkpoint with a failing assessment MUST NOT be approved.

An operator can avoid the condition by declining to attach any assessment. The control then has no signal and no defined consequence.

Now consider:

> For this approval, a valid `MemoryCheckpointAssessment/0.1` over candidate `C`, baseline `B`, required probe suite `S`, and required retriever profile `R` is required. An applicable assessment with result `fail` MUST NOT be approved.

The operator can no longer evade the signal merely by choosing different evidence.

This does not make `MemoryCheckpointAssessment/0.1` universally mandatory. It makes the assessment non-optional **inside an approval policy that has adopted this control**.

That distinction reconciles the initial external/non-normative contribution boundary with the maintainer's rejection of advisory behavior.

## Re-evaluation of the eight scenarios

### Scenario A: valid checkpoint, valid failing assessment, attempted approval

Current design outcome: mostly representable, but the fail-closed mapping is documented as informative.

Adversarial result: **blocking design mismatch**.

Required shape:

- verify evidence independently of behavioral outcome;
- establish assessment applicability;
- applicable `fail` makes the adopted assessment gate unsatisfied;
- approval action must be rejected;
- preserve all evidence.

### Scenario B: valid checkpoint, valid failing assessment, approval bypasses the control

Current design outcome: representable because the harness does not own approval, but no explicit control-violation semantics exist.

Adversarial result: **design clarification required**.

Required shape:

- preserve approval record and failing assessment;
- mark or derive that the approval violated the assessment gate;
- do not convert checkpoint or assessment evidence into cryptographic invalidity.

### Scenario C: malformed assessment, otherwise valid checkpoint

Current design outcome: Pydantic rejects malformed evidence. Approval consequence is unspecified.

Adversarial result: **important applicability finding**.

If an approval policy has adopted the assessment gate, malformed evidence cannot satisfy it. Treating malformed evidence as though no assessment requirement existed would create a bypass.

If the deployment has not adopted the assessment gate at all, the external 0.1 artifact does not independently create a universal requirement.

Therefore the correct question is not "does malformed assessment mean fail?" It does not. The correct question is "does the approval policy require valid applicable assessment evidence?"

### Scenario D: `attested-run-only` private assessment with inaccessible material

Current design outcome: completed behavioral pass/fail is allowed, material-access limitation is explicit, but `attested-run-only` was removed and the payload has no cryptographic producer provenance.

Adversarial result: **blocking terminology/provenance mismatch for that mode**.

Repository review shows that the Agent Manifest v0.2 COSE envelope is explicitly type-bound to `application/agent-manifest+json` and `application/agent-manifest+cose`. Its verifier is required to reject an unexpected `typ` specifically to prevent one signed document type from being reinterpreted as another. The manifest envelope therefore cannot simply be reused verbatim for `MemoryCheckpointAssessment` without defining a new signed-document profile.

TRACE provides a separate signed evidence architecture, but the maintainer explicitly directed TRACE/runtime integration to remain a follow-on and out of this first PR.

Conclusion:

- do not invent an assessment-specific signature architecture in 0.1;
- do not claim that the unsigned assessment payload alone proves an attested run;
- retain the maintainer-endorsed mode as a design target only if its provenance precondition is explicit;
- ask whether 0.1 should reserve `attested-run-only` for externally authenticated payloads or defer that mode until an accepted envelope exists.

### Scenario E: valid `indeterminate` due to unstable repeatability

Current design outcome: valid behavioral `indeterminate`; informative example makes it not eligible.

Adversarial result: **semantics can be cleaner than the current framing**.

Do not relabel `indeterminate` as behavioral failure.

If the adopted gate requires an applicable `pass`, `indeterminate` simply does not satisfy the gate. That is distinct from saying the probe failed its predicate.

This shape may resolve the consequence question without adding a second behavioral meaning to `indeterminate`, but maintainer confirmation is still appropriate because the latest comment expressly rules only on `fail`.

### Scenario F: failing assessment superseded by a legitimate new assessment

Current design outcome: bound-input changes invalidate reuse, but there is no explicit applicability/supersession relation.

Adversarial result: **blocking anti-gaming requirement before approval integration**.

A later favorable assessment must not erase an earlier failure. The gate must decide applicability using precommitted required inputs/profile/suite rather than "latest result wins."

Examples:

- candidate state changed: a new assessment is expected because the bound candidate differs;
- required suite/profile changed by an authorized policy update: new evidence may be applicable, but the old failure remains historical evidence;
- same candidate and same required profile/suite: a contradictory later pass needs scrutiny rather than automatic supersession, especially for a deterministic-eligible path.

The artifact should not contain a self-authorizing `supersedes` field that lets the producer erase a failure. Supersession/applicability belongs to the policy and audit layer.

### Scenario G: passing assessment, another approval prerequisite fails

Current design outcome: aligned.

Adversarial result: **pass**.

Required statement:

- `pass` satisfies at most the adopted assessment gate;
- it never grants checkpoint approval;
- other integrity, freshness, authorization, HITL, deployment, or governance prerequisites remain independent.

### Scenario H: approved historical checkpoint with contemporaneous failing assessment

Current design outcome: representable but underdocumented.

Adversarial result: **pass with required clarification**.

The architecture must support valid evidence of improper governance. This is a feature, not a contradiction.

## Additional adversarial scenarios discovered

### Scenario I: assessment omitted after control adoption

Attack:

The approval policy intends memory behavioral assessment to protect the checkpoint boundary, but the operator submits no assessment.

Unsafe interpretation:

- no `fail` exists, therefore approval proceeds.

Required interpretation:

- the adopted assessment gate lacks required valid applicable evidence;
- the gate is unsatisfied;
- absence is not behavioral `fail`, but it cannot silently become approval eligibility.

This scenario is why a conditional fail rule alone is insufficient.

### Scenario J: favorable assessment under substitute suite

Attack:

A candidate fails required suite `S1`. The operator runs easier suite `S2`, obtains `pass`, and presents only `S2`.

Required interpretation:

- assessment under `S2` may be perfectly valid evidence;
- it is not applicable to a gate requiring `S1`;
- the old `S1` failure remains historical evidence;
- approval gate remains unsatisfied.

### Scenario K: favorable assessment under substitute retriever profile

Attack:

Candidate fails under production retriever profile `R1`. Operator assesses under `R2` with different top-k, filtering, reranking, or tie behavior and obtains `pass`.

Required interpretation:

- the `R2` artifact is valid evidence of `R2` behavior;
- it does not satisfy a gate requiring `R1`;
- full retriever pinning is therefore necessary but not sufficient. The gate must also identify which pinned profile matters.

### Scenario L: valid fail hidden while valid pass is presented

Attack:

Multiple valid assessments exist for the same candidate under different suites/profiles. Producer selectively presents only the favorable one.

Required interpretation:

- approval cannot be based on producer-selected evidence identity;
- the gate must precommit the required assessment identity or constraints;
- transparency/audit mechanisms may later help prove completeness, but 0.1 must at least avoid claiming that a digest alone proves no adverse assessment exists elsewhere.

### Scenario M: assessment passes, then load-bearing retrieval state changes before approval

Attack:

Assessment is run against candidate retrieval state digest `D1`, then the index or derived retrieval representation changes to `D2` before approval while the checkpoint digest remains superficially related.

Required interpretation:

- the old assessment is not applicable if a load-bearing bound state changed;
- approval gate requires evidence over the actual state it is approving;
- current state-specific retrieval-state digests are therefore important and should remain.

## Provenance review

### Agent Manifest COSE envelope

ADR-0011 and the v0.2 envelope define a strong COSE document profile, but it is intentionally specific to Agent Manifest.

Load-bearing protected headers include:

- `content type = application/agent-manifest+json`
- `typ = application/agent-manifest+cose`

The verifier MUST reject an unexpected `typ` to prevent cross-document reinterpretation.

Therefore wrapping a `MemoryCheckpointAssessment` in the manifest COSE profile without a new type/profile would violate the envelope's own domain-separation rule.

### TRACE

TRACE has a signed evidence record architecture and explicit provenance/origin concepts. It is relevant future prior art, but using TRACE as the 0.1 assessment envelope would violate the maintainer's sequencing instruction to keep TRACE/runtime integration out of the first contribution.

### 0.1 consequence

The first contribution should not invent a bespoke signature envelope merely to make `attested-run-only` immediately self-contained.

A safe 0.1 boundary is one of:

1. public and restricted reproducible modes are implemented now, while `attested-run-only` is reserved/documented pending an accepted authenticated envelope;
2. `attested-run-only` is permitted only when the assessment payload is accompanied by an externally authenticated producer assertion whose mechanism is outside this artifact;
3. maintainers explicitly select an existing primitive or approve a small generic signed-statement profile.

Option 3 should not be assumed locally because it changes contribution scope.

## Reproducibility mode versus material access

The adversarial review supports treating these as separate dimensions.

`material_access` answers a verifier-context question:

> Can this verifier obtain the material now?

`reproducibility_mode` answers an evidence-claim question:

> What form of reproducibility or producer assertion does this assessment claim?

Suggested conceptual combinations:

| Reproducibility mode | Typical material access | Meaning |
| --- | --- | --- |
| `public-reproducible` | `public` | complete public inputs and pinned retrieval path permit independent rerun |
| `restricted-reproducible` | `restricted` | independently rerunnable by an authorized verifier with access |
| `attested-run-only` | often `unavailable_to_verifier` or restricted | independent rerun is not promised; attributable producer assertion is load-bearing |

The mapping should not be assumed one-to-one. For example, an authorized verifier may have restricted access while an unauthorized verifier does not. The mode describes the claim class, while access describes the verifier's current ability to obtain material.

## Recommended approval-gate contract shape

This is a design shape, not an implementation authorization.

```yaml
memory_checkpoint_assessment_requirement:
  assessment_type: MemoryCheckpointAssessment
  assessment_version: "0.1"
  candidate_checkpoint_digest: sha256:...
  baseline_checkpoint_digest: sha256:...
  probe_suite_digest: sha256:...
  retriever_profile_digest: sha256:...
  required_result: pass
  maximum_age_seconds: optional
  minimum_reproducibility_mode: optional
  provenance_requirement: optional
```

This object is illustrative only. It should not be added to Agent Manifest or the SDK as part of the first PR without maintainer direction.

Its purpose is to demonstrate that artifact evidence and decision policy can remain separate while still producing a non-advisory control.

The important semantic relation is:

```text
assessment artifact says: this is what was evaluated and what happened
approval gate says: this is what must be evaluated before this action may occur
```

## Findings by severity

### Blocking before design response

1. Current documentation makes fail-closed approval merely informative, conflicting with the maintainer ruling.
2. Current design lacks an explicit applicability model, permitting omission or substitute-evidence bypass if the assessment is ever used as a control.
3. Current implementation replaced maintainer-endorsed reproducibility modes with material-access states that answer a different question.
4. `attested-run-only` currently lacks an honest attributable provenance mechanism, and the manifest-specific COSE profile cannot simply be reused without violating its type binding.

### Must remain explicitly unresolved

1. Whether the 0.1 approval gate requires `pass` or has some other treatment for `indeterminate`.
2. Whether the initial contribution should implement `attested-run-only`, reserve it, or require an external authenticated wrapper.
3. Whether maintainers want a concrete approval-gate example in the first contribution or only contract prose.
4. Whether adoption of the assessment control remains optional per deployment/policy, as the external non-normative boundary suggests.

### Aligned and should not be disturbed

1. Behavioral result is distinct from evidence validity.
2. Private-store material unavailability does not retroactively change behavioral pass/fail.
3. Full retrieval-path pinning is necessary.
4. Stable item identity and explicit id-churn handling remain appropriate.
5. Model judge stays outside deterministic gating.
6. TRACE/runtime integration stays follow-on.
7. Assessment `pass` does not grant deployment authority.
8. Historical failures and improper approvals remain durable audit evidence.
9. The harness should not expose `approve_checkpoint()`.
10. No new signature architecture should be invented in the first contribution without explicit maintainer direction.

## Recommendation after adversarial review

The current implementation branch should remain frozen.

The next internal artifact should be a revised design draft on this review branch, not a code patch. That revision should:

1. introduce explicit evidence validity, behavioral outcome, control applicability, approval admissibility, and historical/audit semantics;
2. replace optional advisory language for `fail` with the maintainer's mandatory approval consequence;
3. make applicability/precommitment load-bearing so fail cannot be bypassed by omission or substitute evidence after a deployment adopts the gate;
4. restore reproducibility mode as a concept distinct from material access;
5. state the provenance precondition for `attested-run-only` without inventing an envelope;
6. preserve `indeterminate` as a distinct behavioral state and present its gate consequence as an explicit maintainer question;
7. keep the first artifact non-authorizing and keep TRACE out of scope.

Only after that revised design survives another scenario pass should a concise design-boundary response be prepared for issue #298.
