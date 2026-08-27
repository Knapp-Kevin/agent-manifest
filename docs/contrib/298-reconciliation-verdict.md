# Issue #298 reconciliation verdict

Status: internal review verdict. No implementation changes are authorized by this document.

Reviewed artifacts:

- `docs/contrib/298-maintainer-feedback-reconciliation.md`
- `docs/contrib/298-adversarial-contract-review.md`
- `docs/contrib/298-memory-checkpoint-assessment-design-reconciled.md`

Frozen implementation baseline:

`feat/memory-checkpoint-assessment-298` at `b34bf1b1de0d8a4495572b8f0775085ea12937ac`

## Verdict

The reconciled contract is coherent enough to take back to the maintainer as a design boundary.

No precommitted kill criterion is currently demonstrated.

The original implementation must remain frozen until the maintainer boundary is confirmed because the current code and original design still differ materially from the reconciled contract.

## Scenario verdicts

| Scenario | Verdict | Notes |
| --- | --- | --- |
| A. Valid checkpoint + valid fail + attempted approval | Coherent | Applicable `fail` blocks the adopted assessment gate without invalidating evidence |
| B. Fail + approval bypass | Coherent | Preserve evidence and identify governance/control violation |
| C. Malformed assessment | Coherent with applicability | Invalid evidence is not behavioral fail; if gate is adopted, invalid evidence cannot satisfy it |
| D. `attested-run-only` private store | Explicitly unresolved | Needs attributable provenance; do not invent a new 0.1 signature architecture |
| E. Valid `indeterminate` | Coherent but maintainer confirmation needed | Preserve semantic state; proposed pass-only gate leaves it unsatisfied without calling it fail |
| F. Later favorable assessment after fail | Coherent with precommitted applicability | New evidence does not erase history; policy determines which evidence is applicable |
| G. Pass + another approval prerequisite fails | Coherent | Pass satisfies at most one gate and grants no authority |
| H. Historical approved checkpoint + fail | Coherent | Valid evidence of improper governance remains representable |
| I. Assessment omitted after gate adoption | Coherent | Missing required applicable evidence leaves the gate unsatisfied |
| J. Substitute probe suite | Coherent | Valid evidence can still be inapplicable |
| K. Substitute retriever profile | Coherent | Full pinning plus precommitted required profile prevents substitution bypass |
| L. Favorable result selectively disclosed | Residual limitation | Standalone artifact cannot prove completeness of all assessments performed |
| M. Retrieval state changes after assessment | Coherent | Bound retrieval-state change makes old evidence inapplicable |

## Residual limitation: selective disclosure

`MemoryCheckpointAssessment/0.1` can prove what a presented artifact says about a bound run. It cannot prove that the producer did not perform and withhold another conflicting assessment.

This matters most when two apparently applicable artifacts exist for the same candidate, suite, and retriever profile.

The deterministic repeatability evidence reduces accidental within-run variability but does not establish global completeness of every run ever performed.

Preventing selective disclosure would require an additional mechanism such as:

- append-only assessment registry;
- transparency log;
- designated evidence store with completeness guarantees;
- policy-controlled run orchestration that records every attempt.

Those mechanisms are outside the initial 0.1 contribution and must not be implied by an assessment digest.

The 0.1 contract should therefore state:

> A presented assessment proves the bound evidence it contains. It does not prove that no other assessment was performed or withheld.

This is an evidence-completeness limit, not a reason to abandon the artifact.

## Residual dependency: canonicalization issue #322

`agentrust-io/agent-manifest#322` remains open and reports that the repository-shared canonicalizer is not fully RFC 8785 conformant.

The assessment prototype intentionally reuses the repository canonical hash primitive rather than creating a competing algorithm.

That remains the correct dependency decision, but it has a consequence for the reconciled applicability model:

- suite and retriever-profile digests can be used consistently inside implementations sharing the same current repository canonicalizer;
- until #322 is fixed, those digests must not be described as independently RFC 8785-portable across implementations;
- a cross-language approval gate comparing those digests could disagree at known canonicalization boundaries.

The existing strict expected-failure tests on the frozen implementation branch correctly keep this dependency visible.

The design response should not compete for #322 or fold its repair into #298.

## Provenance verdict

Repository review confirms that Agent Manifest v0.2 has a strong COSE envelope, but it is intentionally domain-separated to Agent Manifest documents through protected media types and `typ` validation.

It cannot be reused verbatim for `MemoryCheckpointAssessment` without defining another document profile.

TRACE has a signed evidence architecture, but the maintainer explicitly directed TRACE/runtime integration out of the first #298 contribution.

Therefore the safest 0.1 design boundary is:

- no new signature architecture;
- unsigned assessment payloads do not claim cryptographic producer provenance;
- `attested-run-only` is either reserved pending an accepted authenticated wrapper or requires an external authenticated producer assertion whose mechanism remains outside this artifact;
- wrapper/provenance verification stays distinct from behavioral result.

## Approval-boundary verdict

The most important correction from the original design is not merely replacing the word `may` with `MUST`.

A meaningful control requires applicability.

The artifact says:

> what was evaluated and what happened

The approval policy says:

> what must be evaluated before this approval action may occur

When the assessment gate is adopted, evidence that is missing, malformed, or bound to substitute inputs cannot satisfy the gate.

An applicable `fail` is specifically prohibited by the maintainer ruling.

A `pass` never grants approval.

This preserves both parts of the maintainer feedback:

1. the control is not advisory at the approval decision point;
2. the evidence remains valid and historically auditable even when the control is violated.

## Questions worth taking upstream

The internal review reduced the maintainer questions to four focused points.

1. Does the maintainer agree with the explicit applicability distinction: external policy chooses to adopt the assessment gate, but once adopted it requires valid applicable evidence and an applicable `fail` cannot approve?
2. Is the intended 0.1 gate pass-only, so `indeterminate` remains a distinct behavioral result but does not satisfy an adopted approval gate?
3. Should the endorsed reproducibility modes coexist with `material_access` as separate dimensions?
4. For `attested-run-only`, should 0.1 reserve the mode until an accepted authenticated wrapper exists, or define the mode as requiring an external authenticated producer assertion without standardizing that wrapper?

The selective-disclosure and #322 limits should be disclosed rather than posed as design questions unless the maintainer chooses to expand scope.

## Implementation hold

Do not modify the frozen implementation branch until the maintainer design boundary is answered.

In particular, do not yet:

- add `reproducibility_mode` to Pydantic;
- remove `MaterialAccess`;
- add an approval API;
- encode `indeterminate` as fail;
- invent producer signing;
- merge TRACE concepts into the artifact;
- change canonicalization independently of #322.

After maintainer confirmation, update the design first, then models, vectors, tests, and CI in that order.
