# Issue #298 maintainer-feedback reconciliation

Status: internal design review only. No upstream submission is authorized by this document.

Tracker: `agentrust-io/agent-manifest#298`

Review branch: `review/298-maintainer-feedback-reconciliation`

Frozen implementation baseline: `feat/memory-checkpoint-assessment-298` at `b34bf1b1de0d8a4495572b8f0775085ea12937ac`

Maintainer feedback under review: `agentrust-io/agent-manifest#298`, comment `5418827808` by `imran-siddique`

## Purpose

This document reconciles Imran Siddique's latest maintainer feedback on issue #298 against the current `MemoryCheckpointAssessment/0.1` design and preliminary implementation.

The implementation branch is intentionally frozen while this review is active. This branch records analysis only. It must not be used to smuggle design changes into the implementation before the contract is settled.

The review asks four separate questions:

1. What did the maintainer actually require?
2. Which parts of the current design already satisfy that requirement?
3. Where did the design drift from the accepted boundary?
4. Which questions remain genuinely unresolved and therefore must not be invented locally?

## Controlling maintainer statements

The latest maintainer comment establishes the following points.

### Ownership

The implementation lane is explicitly assigned to `Knapp-Kevin`, subject to reversal if `nikshilov` had already begun private implementation.

### Retriever pinning

The maintainer explicitly endorses pinning the complete retrieval path, including revision, query preprocessing, index configuration, distance metric, top-k, reranking, filtering, and deterministic tie behavior.

### Private-store evidence modes

The maintainer explicitly endorses the proposed modes:

- `public-reproducible`
- `restricted-reproducible`
- `attested-run-only`

The stated reason is that a selected mode carries the evidence limitation in the artifact rather than leaving it as prose that can be ignored.

### Failure consequence

The maintainer rules:

> A failing assessment is a checkpoint the deployer MUST NOT approve, not evidence a relying party may weigh.

The same comment immediately limits the meaning of that requirement:

- a failing assessment is not a verification failure;
- the checkpoint may remain cryptographically sound;
- the consistency proof may still verify;
- historical records may contain an approved checkpoint with a failing assessment attached;
- the binding is on the approval action, not on the evidence.

### Scope sequencing

The maintainer endorses the five-step sequencing already proposed and specifically preserves two boundaries:

- prove the abstraction against more than one independently shaped retrieval implementation before any spec hook;
- keep TRACE and runtime-evidence integration outside this first contribution.

The model judge remains diagnostic only and must never become the source of the deterministic result.

## Reconciliation matrix

| Topic | Maintainer position | Current design | Classification | Required response |
| --- | --- | --- | --- | --- |
| Full retrieval-path pinning | Explicitly endorsed | Current retriever profile binds the relevant path, including tie policy | Aligned | Preserve |
| Behavioral result separate from verification validity | Explicitly required by the statement that a failing assessment is not a verification failure | Current design separates behavioral result from verification mismatch | Aligned | Preserve and sharpen terminology |
| Failing assessment remains evidence | Explicitly required | Current artifact can validly represent `fail` and preserves probe evidence | Aligned | Preserve |
| Failing assessment blocks approval | `MUST NOT approve` | Current design presents fail-closed mapping as an informative relying-party choice | Needs correction | Make `fail` a mandatory approval inadmissibility condition without granting approval authority to the assessment harness |
| Pass grants approval | Not stated and inconsistent with the broader approval pipeline | Current design says `pass` is only eligible for remaining checks | Aligned | Preserve explicitly |
| Historical improper approval remains representable | Explicitly contemplated | Current design does not invalidate historical evidence, but does not yet state governance-violation semantics clearly | Needs clarification in design | State that an approval despite an applicable `fail` is an auditable governance violation, not evidence invalidation |
| Reproducibility modes | Explicitly endorses `public-reproducible`, `restricted-reproducible`, `attested-run-only` | Current design replaced them with `material_access = public/restricted/unavailable_to_verifier` and says `attested-run-only` is intentionally avoided | Needs correction | Reassess as a separate evidence-strength dimension rather than a synonym for material access |
| Material access | Relevant to rerunnability but not named as the maintainer's mode system | Current implementation models it directly | Potentially aligned as a separate axis | Do not delete or rename until the two-dimensional model is tested |
| Attested-run provenance | Maintainer language describes a signer attesting that a run occurred | Current payload deliberately defers signing and carries no signer/provenance field | Needs clarification | Determine whether an existing AgentTrust envelope can supply attributable provenance without inventing a second signature architecture |
| `indeterminate` approval consequence | Not ruled on in the latest maintainer comment | Current informative example treats `indeterminate` as not eligible | Unresolved | Do not promote local fail-closed preference into a maintainer requirement without further basis |
| Assessment required for every checkpoint | Not stated | Initial issue and PR #316 keep assessment external and optional | Unresolved, likely out of scope for 0.1 | Do not infer mandatory universal assessment from the conditional `fail` ruling |
| Model judge | Diagnostic only | Diagnostic only | Aligned | Preserve |
| TRACE/runtime evidence | Separate follow-on | Separate follow-on | Aligned | Preserve |
| Multiple independent retrievers | Required before spec hook | Current hardening tests include table-driven and token-overlap retrievers | Aligned at preliminary engineering level | Preserve and strengthen later |

## Corrected conceptual model

The current design used three questions: behavioral result, rerun/verifiability, and policy consequence. That separation was useful but too coarse for the maintainer's latest ruling.

The proposed reconciliation uses four distinct concepts.

### 1. Evidence validity

Question: Is this a well-formed assessment artifact that truthfully and consistently binds the claimed checkpoint states, probe suite, retriever profile, execution evidence, and behavioral result?

A behavioral `fail` does not make the artifact invalid. In fact, a trustworthy system must be able to produce and preserve valid evidence of failure.

Malformed, contradictory, or unverifiable evidence is a different problem and must not be represented as behavioral `fail` merely because both are undesirable.

### 2. Behavioral outcome

Question: Under the bound inputs, retriever profile, and deterministic procedure, did the declared retrieval predicates pass, fail, or remain indeterminate?

The initial aggregate remains:

1. any required `fail` produces aggregate `fail`;
2. otherwise any required `indeterminate` produces aggregate `indeterminate`;
3. otherwise aggregate `pass`.

This outcome describes observed behavior. It does not itself grant deployment authority.

### 3. Approval admissibility

Question: May a deployer approve the bound candidate checkpoint at this decision boundary?

The maintainer has settled one rule:

- an applicable behavioral `fail` makes the candidate checkpoint not approvable;
- therefore an approval action taken while that `fail` applies violates the control.

The inverse does not follow:

- `pass` does not mean approved;
- `pass` means only that this assessment does not supply a disqualifying failure;
- all other approval prerequisites remain independently necessary.

The assessment harness must therefore remain evidence-producing rather than authority-granting. The approval layer consumes the evidence and enforces the `fail` prohibition.

### 4. Historical and audit state

Question: What actually happened, including actions that should have been blocked?

A historical record must remain able to represent all of the following simultaneously:

- a cryptographically valid candidate checkpoint;
- a valid failing `MemoryCheckpointAssessment`;
- a valid consistency proof;
- an approval action that nevertheless occurred.

That state is not contradictory. It is evidence that the approval control was bypassed or violated.

A governance system that deletes, invalidates, or rewrites the failing assessment after an improper approval would destroy the evidence needed to audit the violation.

## Conditional control, not universal requirement

The latest maintainer ruling is interpreted narrowly:

> If an applicable assessment exists and its behavioral result is `fail`, the deployer MUST NOT approve the bound candidate checkpoint.

This review does not infer the stronger statement:

> Every candidate checkpoint MUST have a `MemoryCheckpointAssessment/0.1` before approval.

The stronger rule is not established by the latest comment, and issue #298 plus PR #316 continue to describe the first assessment artifact as external and non-normative.

If AgentTrust later requires universal assessment, that is a separate normative decision and should be made explicitly.

## Reproducibility and material access

The current draft collapsed a useful distinction by replacing the originally proposed reproducibility modes with a `material_access` enum.

These concepts answer different questions.

### Material access

Question: Can the present verifier obtain the material required to rerun the assessment?

Current values:

- `public`
- `restricted`
- `unavailable_to_verifier`

This can remain useful because access can vary by verifier and authorization context.

### Reproducibility or evidence-strength mode

Question: What class of reproducibility or provenance claim is the artifact entitled to make?

Maintainer-endorsed candidate values:

- `public-reproducible`
- `restricted-reproducible`
- `attested-run-only`

The two axes should not be assumed equivalent.

Example: material may be `restricted` but fully rerunnable by an authorized auditor, which supports `restricted-reproducible`. A different restricted store may not be independently rerunnable by any verifier and could therefore only support an attributable `attested-run-only` claim.

No schema change is authorized yet. The next design revision should test whether these are indeed orthogonal fields and define invariants between them.

## Provenance problem for `attested-run-only`

The maintainer's private-store formulation is attributable:

> this signer ran this probe suite against this checkpoint and got this result

That statement requires more than a JSON payload carrying a digest.

The current design correctly refuses to invent a second signature architecture and notes that an unsigned payload cannot prove producer provenance. The current implementation, however, carries no signer or producer provenance field.

Therefore `attested-run-only` cannot safely be adopted as a claim in 0.1 until the design establishes how attribution is supplied.

Preferred order of operations:

1. inspect existing AgentTrust signing and envelope primitives;
2. determine whether `MemoryCheckpointAssessment/0.1` can compose with one of them without changing the artifact's behavioral semantics;
3. if it can, bind producer/signer provenance through that existing primitive;
4. if it cannot, state the 0.1 provenance limitation explicitly rather than inventing bespoke signing.

The existing precommitted kill criterion against requiring a new signature/envelope standard remains in force.

## `indeterminate` remains unresolved

The maintainer explicitly rules on `fail`. The latest comment does not establish the approval consequence of `indeterminate`.

Current reasons include:

- adapter unsupported;
- repeatability unstable;
- repeatability not run;
- baseline precondition unmet;
- identity churn.

A local fail-closed policy may reasonably treat some or all of these states as not eligible for approval. That is an engineering preference, not yet a maintainer ruling.

Before promoting any such rule into the contract, the design must distinguish at least these possibilities:

1. all `indeterminate` results block approval;
2. only selected indeterminate reasons block approval;
3. `indeterminate` remains policy-dependent in external 0.1 tooling;
4. a future normative layer defines the consequence while the artifact remains descriptive.

No implementation change should encode one of these choices until the design boundary is settled.

## Adversarial scenarios

The following scenarios are the minimum reconciliation test set before revising implementation.

### Scenario A: valid checkpoint, valid failing assessment, attempted approval

Expected:

- checkpoint cryptographic verification remains valid;
- assessment evidence remains valid;
- behavioral result remains `fail`;
- approval action must be rejected;
- no evidence is deleted or rewritten.

If the architecture cannot express this cleanly, the design is wrong.

### Scenario B: valid checkpoint, valid failing assessment, approval bypasses the control

Expected:

- historical approval remains observable;
- failing assessment remains observable;
- checkpoint and consistency proof can remain cryptographically valid;
- audit logic can identify that approval occurred despite an applicable `fail`;
- the record is not rewritten to manufacture compliance.

### Scenario C: malformed assessment, otherwise valid checkpoint

Expected:

- malformed assessment is rejected as invalid evidence;
- it is not converted into behavioral `fail`;
- no claim is made that the candidate behavior was assessed successfully or unsuccessfully;
- approval consequence remains a separate question unless another rule requires a valid assessment.

This scenario protects the evidence-validity versus behavioral-outcome boundary.

### Scenario D: `attested-run-only` private assessment with inaccessible material

Expected:

- behavioral `pass` or `fail` may remain a completed run result;
- independent rerun limitation is explicit;
- the artifact does not claim independent reproducibility;
- attributable producer/signer provenance is required before the word `attested` is treated as load-bearing;
- lack of material access alone does not retroactively change `pass` to `indeterminate`.

### Scenario E: valid `indeterminate` due to unstable repeatability

Expected:

- assessment artifact remains valid evidence;
- behavioral result remains `indeterminate` with explicit reason;
- approval consequence is marked unresolved in 0.1 until the contract is settled;
- code does not silently treat it as either pass or fail.

### Scenario F: failing assessment superseded by a legitimate new assessment

Expected:

- the original failing assessment remains durable historical evidence;
- a new assessment must bind the exact new load-bearing inputs;
- the old assessment is not mutated into `pass`;
- approval admissibility depends on the assessment applicable to the candidate state being considered;
- the design must define what makes one assessment applicable or superseded without deleting history.

### Scenario G: passing assessment, another approval prerequisite fails

Expected:

- assessment remains `pass`;
- checkpoint is still not approved;
- no API or documentation implies that assessment pass grants authority;
- the approval system identifies the independent failed prerequisite.

### Scenario H: approved historical checkpoint with contemporaneous failing assessment

Expected:

- relying parties can inspect both facts;
- neither evidence object is invalidated merely because the combination reveals a control violation;
- the system can distinguish "invalid evidence" from "valid evidence of improper governance."

## Preliminary implementation impact map

No code changes are authorized by this review document. If the reconciled architecture is accepted, the likely implementation consequences are:

### Design document

`docs/memory-checkpoint-assessment.md`

Likely changes:

- replace the overly broad heading `Behavioral result is not policy` with language that distinguishes evidence from approval authority;
- make `fail` a mandatory approval-admissibility blocker;
- preserve the rule that `pass` does not authorize approval;
- explicitly describe historical governance-violation semantics;
- restore or formally replace the maintainer-endorsed reproducibility mode model;
- document the provenance requirement for any `attested-run-only` claim;
- mark `indeterminate` consequence as unresolved rather than silently normative.

### Artifact model

`python/src/agent_manifest/_memory_assessment.py`

Potential changes after design approval:

- add a separate reproducibility/evidence-strength field if the two-axis model survives review;
- preserve `MaterialAccess` if it remains independently useful;
- add producer/provenance binding only through an accepted existing project primitive or neutral metadata boundary;
- do not add `approve_checkpoint()` or another authority-granting API;
- do not make `fail` invalidate the artifact model;
- do not encode unresolved `indeterminate` approval semantics prematurely.

### Tests and vectors

Potential additions after design approval:

- a valid failing artifact remains structurally valid;
- approval policy fixture rejects `fail` without modifying the assessment;
- `pass` alone never authorizes approval;
- historical improper approval plus `fail` remains representable;
- material-access and reproducibility-mode combinations are validated if modeled separately;
- `attested-run-only` cannot claim more provenance than the surrounding envelope supplies;
- `indeterminate` scenarios remain explicit and non-collapsed.

## Relationship to PR #316

Merged PR #316 intentionally states that the memory checkpoint protocol establishes integrity, ordering, freshness, and budget but not retrieval acceptability.

This reconciliation preserves that separation.

A behavioral assessment failure does not retroactively make the checkpoint protocol's cryptographic claims false. Instead, it supplies an additional decision-relevant fact at the approval boundary.

That is why the following combination is coherent:

```text
checkpoint integrity: valid
checkpoint consistency proof: valid
behavioral assessment evidence: valid
behavioral assessment result: fail
approval admissibility: prohibited
```

The design must not collapse those lines into one status flag.

## Relationship to the cited advisory-control failures

The maintainer cites issue #265 and `agentrust-io/cmcp#371` as precedent for why a meaningful signal cannot remain merely advisory at its decision boundary.

The lesson adopted here is narrow:

- when a control exists specifically to detect a disqualifying condition at the only decision point where that condition can prevent the action, a detected failure must actually prevent that action;
- making the failure actionable does not require redefining the underlying evidence as invalid;
- fail-closed control semantics and evidence preservation are compatible.

This review does not import unrelated attestation or verifier semantics from those issues into `MemoryCheckpointAssessment/0.1`.

## Questions that should remain explicit for maintainer review

After internal adversarial review, the eventual design-boundary response should ask for confirmation only where the text genuinely leaves room for interpretation.

Candidate unresolved questions:

1. Should every aggregate `indeterminate` make a checkpoint not approvable, or is that consequence intentionally left to a later policy layer?
2. Does the maintainer intend the endorsed reproducibility modes to coexist with material-access metadata as separate dimensions?
3. Which existing AgentTrust envelope or signing primitive should carry attributable producer provenance for `attested-run-only`, if any, in the first release?
4. Is the conditional rule correct for 0.1: an applicable `fail` blocks approval, without yet making `MemoryCheckpointAssessment/0.1` mandatory for every checkpoint?

These questions must not be converted into implementation assumptions before the design boundary is reviewed.

## Exit criteria for reconciliation

The implementation branch remains frozen until all of the following are true:

1. the four-layer model can represent evidence validity, behavioral outcome, approval admissibility, and historical audit state without contradiction;
2. all eight adversarial scenarios above have coherent expected outcomes;
3. reproducibility mode and material access are either cleanly separated or intentionally unified with a defensible reason;
4. `attested-run-only` has an honest provenance story or is explicitly deferred;
5. `indeterminate` consequence is either settled by existing evidence or marked for maintainer clarification;
6. the resulting design still requires no new signature architecture, no model judge in deterministic gating, and no TRACE/runtime expansion;
7. no precommitted kill criterion is triggered.

Only after these criteria are met should `docs/memory-checkpoint-assessment.md` be revised. Implementation, vectors, CI, and any upstream design response follow that revision rather than preceding it.
