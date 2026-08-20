# MemoryCheckpointAssessment/0.1 design draft

> **Status: non-normative design draft for issue #298.** This document defines a proposed reference assessment artifact and harness boundary. It does not change Agent Manifest conformance or authorize checkpoint promotion.

## What this assessment does not prove

A `MemoryCheckpointAssessment/0.1` result is not a certification that a memory system is safe. It does not prove that stored content is true, that the assessor or signer is honest, that a model answer is correct, that a memory write was authorized, or that a checkpoint should be deployed. Agent Manifest continues to own checkpoint integrity, lineage, ordering, freshness, and update-budget checks.

The 0.1 claim is deliberately narrower:

> Under the bound inputs and retriever profile, the reference harness observed the declared retrieval behavior and evaluated the declared deterministic predicates according to the recorded procedure.

The gating path never uses an LLM judge.

## Keep three questions separate

The design separates:

1. **behavioral result**: did the declared retrieval predicates pass, fail, or remain indeterminate?
2. **rerun/verifiability**: can another party obtain the bound material and reproduce or verify the run?
3. **policy consequence**: what does a relying party do with the evidence?

These are deliberately not one enum.

A private-store assessment may still produce a behavioral `pass` or `fail`. Lack of third-party data access limits independent rerun/verifiability; it does not retroactively change the behavioral result.

## Material access

`material_access` describes whether a verifier can obtain the material needed to rerun the assessment:

- `public`
- `restricted`
- `unavailable_to_verifier`

This field does not determine `pass`, `fail`, or `indeterminate`.

## Deterministic capability and repeatability evidence

The adapter/profile declares whether it can satisfy the 0.1 deterministic contract:

- `deterministic`
- `unsupported_or_unknown`

A declaration alone is not evidence.

The harness records observed repeatability:

```yaml
repeatability:
  trials: 20
  distinct_orderings_observed: 1
  observed_status: stable
  tie_events_observed: null
```

The initial reference floor is 20 identical runs per unique query/state/profile combination. This is an engineering evidence floor, not proof of mathematical determinism.

A profile is eligible for the 0.1 deterministic result path only when the adapter declares deterministic capability, the profile binds an explicit deterministic tie policy, the required repeatability trials ran, and `distinct_orderings_observed == 1`.

If the backend can expose tie events, the adapter records `tie_events_observed`; otherwise it records `null`. Tie observability is diagnostic. Declaring deterministic tie behavior is still required for deterministic eligibility.

The terms `verified` and `attested-run-only` are intentionally avoided.

## Configuration profile and state-specific retrieval material

The retriever **configuration profile** is content-addressed separately from the baseline and candidate retrieval states.

The profile includes configuration that should stay fixed across the comparison:

- implementation identity and version/source revision;
- embedding model identity and immutable revision/digest when available;
- quantization/precision mode;
- tokenizer identity/version where applicable;
- query normalization/preprocessing;
- similarity/distance function;
- index implementation and build configuration;
- namespace/scope/tenant filtering rules;
- top-k and truncation rules;
- reranker identity/configuration;
- deterministic tie policy;
- deterministic seeds where applicable;
- harness version;
- adapter version.

Opaque components are marked opaque. A profile digest proves only which declaration is bound; it does not prove that the running retriever matched that declaration.

State-specific derived material does **not** belong in the shared profile because the candidate is expected to differ from the baseline. Each state reference therefore binds its own retrieval-state evidence:

```yaml
baseline_state:
  checkpoint_digest: "sha256:..."
  retrieval_state_digest: "sha256:..."
  indexed_item_count: 120

candidate_state:
  checkpoint_digest: "sha256:..."
  retrieval_state_digest: "sha256:..."
  indexed_item_count: 123
```

`retrieval_state_digest` may identify a derived index snapshot or another adapter-defined immutable retrieval representation when one exists.

## Runtime consistency observations

The artifact may record cheap execution observations that make a false declaration easier to detect on rerun, for example adapter/runtime build identity or embedding dimensionality.

These observations are consistency evidence only. They are not attestation, do not prove that an opaque provider executed the declared implementation, and are not required to turn a completed private-store behavioral run into `pass` or `fail`.

A later verifier that can rerun the assessment should report a profile or runtime-observation mismatch as a **verification mismatch**, not as behavioral `indeterminate`.

## Stable assessment identity

The harness does not infer memory identity from prose similarity.

Adapters emit a stable logical assessment key plus a version/content digest:

```python
class RetrievedItem:
    item_key: str
    item_version_digest: str
    rank: int
    scope_labels: tuple[str, ...]
```

Floating retrieval scores are intentionally excluded from the load-bearing 0.1 observation contract. The four initial predicates require identity, order, and scope metadata, not cross-runtime floating-point score equality. An adapter may expose scores as non-gating diagnostics later.

Probe references state where an item key is required:

```yaml
item_ref:
  key: "account.owner-name"
  required_in: both
```

`required_in` is one of `baseline`, `candidate`, or `both`. This distinction matters because an introduced correction can legitimately exist only in the candidate, while an anchor-continuity key must resolve in both states.

If a probe requires a key in both states and the adapter cannot resolve it consistently, that probe is `indeterminate` with reason `id_churn`.

Chunked/vector systems that regenerate all logical identities on reindex cannot support transition invariants unless they provide a stable external identity mapping. The 0.1 design states that limitation rather than hiding it behind semantic matching.

## Tie behavior

A deterministic-eligible profile must declare a deterministic tie policy unconditionally. Examples include stable lexical order by `item_key`, a stable backend comparator identified by implementation/version, or another explicit total ordering.

If the backend cannot guarantee deterministic tie resolution, deterministic capability is `unsupported_or_unknown`.

## Probe suite and precommitment limit

A probe suite is versioned and content-addressed. The reference harness freezes the suite before executing the candidate run and refuses in-process mutation after results begin.

A suite digest proves which suite was used. By itself it does **not** prove that the operator selected the suite before seeing candidate behavior. Strong operational precommitment requires an external timestamp, approval record, transparency entry, or other relying-party mechanism. 0.1 states that limit rather than fabricating one.

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

## Behavioral result and indeterminate semantics

Per-probe behavioral result:

- `pass`
- `fail`
- `indeterminate`

Every `indeterminate` requires one or more behavioral reason codes. Initial reason codes are:

- `adapter_unsupported`
- `repeatability_unstable`
- `repeatability_not_run`
- `baseline_precondition_unmet`
- `id_churn`

Material unavailability is **not** an indeterminate reason. A private or unavailable-to-verifier store can still produce a completed behavioral result; the limitation belongs to rerun/verifiability metadata.

A profile/runtime mismatch discovered during independent verification is also not an indeterminate reason. It is a verification mismatch outside the behavioral result.

Aggregate behavioral rule:

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

## Behavioral result is not policy

The reference harness computes evidence only. The SDK assessment path must not expose a function such as `approve_checkpoint()` or otherwise convert an assessment result into deployment authority.

An informative example may show a fail-closed relying-party mapping:

- `pass` => eligible for other approval checks;
- `fail` => not eligible;
- `indeterminate` => not eligible.

That mapping belongs in documentation/examples, not the assessment execution path. This keeps the first release non-normative in effect rather than merely labelled non-normative.

## Lifecycle and staleness

The artifact records `assessed_at`. There is no intrinsic TTL in 0.1. The evidence remains a statement about the exact bound inputs.

Reuse is invalid when a load-bearing bound value changes, including the baseline checkpoint digest, candidate checkpoint digest, baseline/candidate retrieval-state digest, probe-suite digest, or retriever-profile digest.

A relying party may impose a maximum assessment age without changing the artifact's meaning.

## Gaming and probe visibility

Known public probes can be optimized against. 0.1 does not pretend otherwise.

The artifact should state whether the gating suite is public or restricted. Restricted or held-out operational probes can reduce gaming but reduce independent rerunnability.

Rotated audit suites, held-out acceptance probes, and statistical/nondeterministic retrieval profiles are future work.

## Cost and feasibility

Let `R` be the number of unique retrieval invocations across all probe/state references and `T` the repeatability trial floor. The repeatability evidence path requires approximately `R × T` retrieval calls.

The reference fixture adapter requires no reindexing. Production adapters may require prebuilt baseline and candidate snapshots. The 0.1 harness does not require rebuilding an index solely to run the assessment.

The artifact may record operational run statistics such as retrieval-call count and duration. Those statistics are evidence, not conformance requirements.

## Illustrative artifact shape

```yaml
type: MemoryCheckpointAssessment
version: "0.1"

baseline_state:
  checkpoint_digest: "sha256:..."
  retrieval_state_digest: "sha256:..."
  indexed_item_count: 8

candidate_state:
  checkpoint_digest: "sha256:..."
  retrieval_state_digest: "sha256:..."
  indexed_item_count: 9

probe_suite_digest: "sha256:..."
retriever_profile_digest: "sha256:..."
assessed_at: "2026-08-20T00:00:00Z"
material_access: restricted

determinism:
  adapter_capability: deterministic
  trials: 20
  distinct_orderings_observed: 1
  observed_status: stable
  tie_events_observed: null

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

Signing/envelope semantics remain deliberately deferred. An unsigned payload cannot prove producer provenance. The first implementation should therefore describe producer identity as metadata unless and until maintainers choose an existing AgentTrust signing/envelope primitive. The payload must not invent a second signature architecture beside the project's current COSE direction.

## First implementation boundary

The first implementation should include typed Pydantic models, a deterministic adapter protocol, a public deterministic fixture adapter, canonical digests that reuse existing repository primitives, and positive/negative vectors for the four initial invariants.

Negative vectors should cover baseline-precondition failure, ID churn, unsupported adapter capability, unstable repeatability, scope-leak severity, tie behavior, profile/configuration change, and state-digest change.

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

Issue #298 names Pulse and the Pulse paper as implementation references. Relevant lessons for this design include freezing cases before seeing candidate results, retaining stable identifiers and digests in result receipts, marking boundary checks inconclusive when execution errors prevent evaluation, and keeping retrieval evidence separate from LLM-judged answer accuracy.

These are design influences, not dependencies. AgentTrust must not depend on Pulse.
