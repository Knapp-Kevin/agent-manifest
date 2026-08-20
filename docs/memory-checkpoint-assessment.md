# MemoryCheckpointAssessment/0.1 design draft

> **Status: non-normative design draft for issue #298.** This document defines a proposed reference assessment artifact and harness boundary. It does not change Agent Manifest conformance or authorize checkpoint promotion.

## What this assessment does not prove

A `MemoryCheckpointAssessment/0.1` result is not a certification that a memory system is safe. It does not prove that stored content is true, that the assessor or signer is honest, that a model answer is correct, that a memory write was authorized, or that a checkpoint should be deployed. Agent Manifest continues to own checkpoint integrity, lineage, ordering, freshness, and update-budget checks.

The 0.1 claim is deliberately narrower:

> Under the bound inputs and retriever profile, the reference harness observed the declared retrieval behavior and evaluated the declared deterministic predicates according to the recorded procedure.

The gating path never uses an LLM judge.

## Material access, deterministic capability, and repeatability are separate

A single reproducibility label would conflate distinct properties. The artifact therefore records three concepts independently.

### Material access

`material_access` describes whether a verifier can obtain the material needed to rerun the assessment:

- `public`
- `restricted`
- `unavailable_to_verifier`

This says nothing about deterministic behavior.

### Deterministic capability

The adapter/profile declares whether it can satisfy the 0.1 deterministic contract:

- `deterministic`
- `unsupported_or_unknown`

A declaration alone is not evidence.

### Repeatability evidence

The harness records observed repeatability:

```yaml
repeatability:
  trials: 20
  distinct_orderings_observed: 1
  tie_events_observed: 0
  observed_status: stable
```

The initial reference floor is 20 identical runs per probe/profile/state combination. That is an engineering evidence floor, not a mathematical proof of determinism.

A profile is eligible for the 0.1 deterministic result path only when the adapter declares deterministic capability, the profile binds an explicit deterministic tie policy, the required repeatability trials ran, `distinct_orderings_observed == 1`, and required runtime observations are present. Otherwise the affected probe is `indeterminate` with an explicit reason code.

The terms `verified` and `attested-run-only` are intentionally avoided.

## Retriever profile

The assessment binds a canonical retriever profile by digest. The profile should include every known element that can materially alter selected context:

- implementation identity and version/source revision;
- embedding model identity and immutable revision/digest when available;
- quantization/precision mode;
- tokenizer identity/version where applicable;
- query normalization/preprocessing;
- similarity/distance function;
- index implementation and material build parameters;
- derived index-state digest when retrieval depends on derived state;
- namespace/scope/tenant filters;
- top-k and truncation rules;
- reranker identity/configuration;
- deterministic tie policy;
- deterministic seeds where applicable;
- harness version;
- adapter version.

Opaque components are marked opaque. A profile digest proves only which declaration is bound. It does not prove that the running retriever matched that declaration.

## Runtime consistency observations

To make a false profile declaration easier to detect on rerun, the artifact records cheap observed invariants where available:

```yaml
runtime_observation:
  embedding_dimension: 1024
  indexed_item_count: 12345
  fingerprint_probe_digest: "sha256:..."
  observation_digest: "sha256:..."
```

These values are consistency evidence, not attestation and not proof that an opaque provider executed the declared implementation.

## Stable assessment identity

The harness does not infer memory identity from prose similarity.

Adapters emit a stable logical assessment key plus a version/content digest:

```python
class RetrievedItem:
    item_key: str
    item_version_digest: str
    rank: int
    score: float | None
    scope_labels: tuple[str, ...]
```

Probe references state where an item key is required:

```yaml
item_ref:
  key: "account.owner-name"
  required_in: baseline
```

`required_in` is one of `baseline`, `candidate`, or `both`. This distinction matters because an introduced correction can legitimately exist only in the candidate, while an anchor-continuity key must resolve in both states.

If a probe requires a key in both states and the adapter cannot resolve it consistently, the probe is `indeterminate` with reason `id_churn`.

Chunked/vector systems that regenerate all logical identities on reindex cannot support transition invariants unless they provide a stable external identity mapping. The 0.1 design states that limitation rather than hiding it behind semantic matching.

## Tie behavior

A deterministic-eligible profile must declare a deterministic tie policy unconditionally. Examples include stable lexical order by `item_key`, a stable backend comparator identified by implementation/version, or another explicit total ordering.

If the backend cannot guarantee deterministic tie resolution, deterministic capability is `unsupported_or_unknown`.

The harness records `tie_events_observed` during repeatability trials. Observing no ties does not remove the requirement to declare the policy.

## Probe suite

A probe suite is versioned, frozen before execution, and content-addressed. A gating suite must not be rewritten after candidate results are observed.

The initial invariant classes are:

1. transition invariants: correction precedence and anchor preservation;
2. state invariants: scope isolation;
3. paired-state invariants: state-conditioned differentiation.

Each probe contains a probe ID, class, required item references, baseline preconditions when relevant, an explicit predicate, a severity class, and the expected access/scope context.

### Correction precedence

The probe names the superseded item and correcting item and declares the expected inclusion/order rule. The relation is supplied as test data. The harness does not infer a correction semantically.

### Anchor preservation

The probe declares an anchor key and baseline precondition. If the baseline precondition is not met, the result is `indeterminate` with reason `baseline_precondition_unmet`. If the baseline satisfies the precondition and the candidate violates it, the result is `fail`.

### Scope isolation

The probe declares active scope and forbidden item keys or scope labels. Retrieving forbidden material is `fail` with severity class `confidentiality`.

The aggregate artifact surfaces:

```yaml
security_flags:
  contains_confidentiality_failure: true
```

Scope failures are therefore not flattened into an undifferentiated behavioral regression.

### State-conditioned differentiation

The paired probe declares the expected item inclusion/exclusion or rank relation between two states. No opaque semantic-distance threshold is used in 0.1.

## Result and indeterminate semantics

Per-probe result:

- `pass`
- `fail`
- `indeterminate`

Every `indeterminate` requires one or more reason codes. Initial reason codes are:

- `adapter_unsupported`
- `repeatability_unstable`
- `repeatability_not_run`
- `baseline_precondition_unmet`
- `id_churn`
- `material_unavailable`
- `runtime_observation_missing`
- `profile_mismatch`

Aggregate rule:

1. any required `fail` => aggregate `fail`;
2. otherwise any required `indeterminate` => aggregate `indeterminate`;
3. otherwise aggregate `pass`.

The artifact records coverage:

```yaml
coverage:
  required_probe_count: 20
  passed: 18
  failed: 0
  indeterminate: 2
  indeterminate_rate: 0.10
```

This prevents a mostly-indeterminate suite from looking equivalent to a useful assessment.

Cross-assessment downgrade policy is intentionally not invented inside the 0.1 artifact. A relying party may compare previous assessments separately.

## Result is not policy

The reference harness computes evidence only. The SDK assessment path must not expose a function such as `approve_checkpoint()` or otherwise convert an assessment result into deployment authority.

An informative example may show a fail-closed relying-party mapping:

- `pass` => eligible for other approval checks;
- `fail` => not eligible;
- `indeterminate` => not eligible.

That mapping belongs in documentation/examples, not the assessment execution path. This keeps the first release non-normative in effect rather than merely labelled non-normative.

## Lifecycle and staleness

The artifact records `assessed_at`. There is no intrinsic TTL in 0.1. The evidence remains a statement about the exact bound inputs.

Reuse is invalid when a load-bearing bound value changes, including the baseline checkpoint digest, candidate checkpoint digest, probe-suite digest, retriever-profile digest, relevant derived index-state digest, or required runtime fingerprint observation.

A relying party may impose a maximum assessment age without changing the artifact's meaning.

## Gaming and probe visibility

Known public probes can be optimized against. 0.1 does not pretend otherwise.

The artifact should state whether the gating suite is public or restricted. Restricted or held-out operational probes can reduce gaming but reduce independent rerunnability.

Rotated audit suites, held-out acceptance probes, and statistical/nondeterministic retrieval profiles are future work.

## Cost and feasibility

For `P` probe/state combinations and `T` repeatability trials, the deterministic evidence path requires approximately `P × T` retrieval calls, plus baseline/candidate calls required by transition predicates.

The reference fixture adapter requires no reindexing. Production adapters may require prebuilt baseline and candidate snapshots. The 0.1 harness does not require rebuilding an index solely to run the assessment.

The artifact may record operational run statistics such as retrieval-call count and duration. Those statistics are evidence, not conformance requirements.

## Illustrative artifact shape

```yaml
type: MemoryCheckpointAssessment
version: "0.1"
baseline_checkpoint_digest: "sha256:..."
candidate_checkpoint_digest: "sha256:..."
probe_suite_digest: "sha256:..."
retriever_profile_digest: "sha256:..."
assessed_at: "2026-08-20T00:00:00Z"
material_access: public

determinism:
  adapter_capability: deterministic
  trials: 20
  distinct_orderings_observed: 1
  tie_events_observed: 0
  observed_status: stable

runtime_observation:
  embedding_dimension: 1024
  indexed_item_count: 8
  fingerprint_probe_digest: "sha256:..."

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

Signing/envelope semantics remain deliberately deferred. The payload must not invent a second signature architecture beside Agent Manifest's existing COSE direction.

## First implementation boundary

The first implementation should include typed Pydantic models, a deterministic adapter protocol, a public deterministic fixture adapter, canonical digests that reuse existing repository primitives, and positive/negative vectors for the four initial invariants.

Negative vectors should cover baseline-precondition failure, ID churn, unsupported adapter capability, unstable repeatability, scope-leak severity, tie behavior, and profile/runtime observation mismatch.

The first PR should not modify `spec/` unless maintainers explicitly request it. It should add no external dependency and no SDK promotion/approval function.

## Precommitted kill criteria

Abandon or materially redesign this wedge before implementation if any of the following is demonstrated:

1. the artifact necessarily duplicates an existing AgentTrust normative primitive rather than composing with it;
2. a framework-neutral stable assessment identity cannot support the four initial invariants without semantic/LLM inference;
3. evidence cannot be separated from deployment policy in actual code;
4. the first release requires a new signature/envelope standard;
5. the deterministic 0.1 core cannot support at least two independently shaped retrieval implementations without framework-specific semantics dominating it;
6. repository/layer placement changes destroy the proposed artifact boundary rather than merely moving code;
7. a candidate can obtain `pass` while violating one of the four declared invariants under the same bound inputs and profile.

## Prior-art note

Issue #298 names Pulse and the Pulse paper as implementation references. Relevant lessons for this design include freezing cases before seeing candidate results, retaining IDs/digests/scores/timings/counts in result receipts, marking boundary checks inconclusive when execution errors prevent evaluation, and keeping retrieval evidence separate from LLM-judged answer accuracy.

These are design influences, not dependencies. AgentTrust must not depend on Pulse.
