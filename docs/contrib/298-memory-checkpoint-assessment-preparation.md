# MemoryCheckpointAssessment/0.1 preparation record

Status: fork preparation complete enough for continued adversarial review; upstream submission still prohibited pending explicit maintainer welcome

Upstream tracker: agentrust-io/agent-manifest#298
Working branch: `feat/memory-checkpoint-assessment-298`
Fork-only validation PR: `Knapp-Kevin/agent-manifest#1`

## Submission boundary

This branch is preparatory work only. Do not open an upstream pull request, request upstream review, or post implementation updates to AgentTrust until a maintainer explicitly indicates that the contribution is welcome.

The upstream issue already contains an ownership claim for the implementation lane. Silence after that claim is not treated as approval to submit.

The draft PR in the `Knapp-Kevin/agent-manifest` fork exists only as a CI surface. It is not an AgentTrust submission and must not be retargeted upstream without explicit maintainer welcome.

## Intended contribution boundary

`MemoryCheckpointAssessment/0.1` is an external, optional, non-normative behavioral assessment artifact and reference harness for candidate memory checkpoints.

It evaluates retrieval behavior at the checkpoint transition boundary. It does not certify model correctness, memory truth, deployment safety, or Agent Manifest conformance.

The initial invariants are:

1. correction precedence;
2. anchor preservation;
3. scope isolation;
4. state-conditioned differentiation.

The deterministic assessment result is separate from relying-party promotion policy. A model judge, if ever attached, is diagnostic only and cannot be the source of the deterministic result.

## Maintainer questions incorporated

The design preserves the three requirements raised on #298:

1. Retriever pinning includes embedding model, revision, quantization, preprocessing, retrieval/index configuration, distance metric, top-k, reranking, filtering, and deterministic tie behavior where applicable.
2. Private-store evidence distinguishes identity/provenance from independent rerunnability. Material access does not silently change behavioral pass/fail semantics.
3. Assessment result and relying-party consequence remain separate, so the first external tool does not silently become a new conformance requirement.

## Current fork implementation

The branch now contains:

- `docs/memory-checkpoint-assessment.md`, the working design record;
- `python/src/agent_manifest/_memory_assessment.py`, the non-normative artifact models, adapter contract, and deterministic reference harness;
- `python/tests/test_memory_assessment.py`, the initial focused coverage;
- `python/tests/test_memory_assessment_hardening.py`, adversarial and mutation-resistance coverage plus two independently shaped retriever implementations;
- `python/tests/test_memory_assessment_vectors.py`, executable public reference-vector coverage;
- `python/tests/test_memory_assessment_canonicalization_dependency.py`, strict expected-failure guards for the open RFC 8785 dependency;
- `python/tests/fixtures/memory_assessment/README.md`, vector design and independence rules;
- `python/tests/fixtures/memory_assessment/reference-vectors-v0.1.json`, the first self-contained public reference-vector bundle.

Important implementation commits include:

- `40dc171424f977fdb4811948465e44cec169ba47` design draft;
- `1c7176c55c41c965d6608f6181219fc38136e03a` result/verifiability separation;
- `cefb7951c779b0e38685ec014901faf97863497c` preliminary harness;
- `c1210d73548193a8f1c5a1773c162fde6cae8a7e` preliminary focused tests;
- `9de0197ebe8f9a3f7152f8b164bee2eab6f17768` durable preparation record;
- `5d2f628fc2cd10a97734769ac829e3e58f5258ed` durable vector plan;
- `5e49d921a80f66ca8aafba2c0430c19dacc0cf78` hardened evidence boundary;
- `05db2b1a5a33381922b9fedfa41c38d24ba23648` hardening and second-retriever tests;
- `2e286c959f45d5b74a7b061ad5960bd67fedbf8e` public reference-vector bundle;
- `064afccd6a3defdcb80512d9c0e1532cd852ad59` executable reference-vector tests;
- `6eb18de78fc3d7b3cfcef3c4e4dff8561556cf34` canonicalization dependency tests;
- `16f63c9830d07f177fed0b31245f40b2f7c64ce2` type/security-gate fixes.

## Hardening completed

The implementation now:

- freezes Pydantic assessment evidence models;
- snapshots the retriever profile and probe suite at run start;
- deep-copies retrieval requests for every trial so an adapter cannot mutate later trials;
- permits unsupported/unknown adapters to omit a tie policy while requiring an explicit tie policy for deterministic eligibility;
- requires timezone-aware `assessed_at` values;
- includes scope labels in repeatability identity because scope metadata is load-bearing for confidentiality isolation;
- surfaces confidentiality failures even when a probe is diagnostic/non-required;
- distinguishes `pass`, `fail`, and `indeterminate` without embedding promotion policy;
- records explicit indeterminate reasons for unsupported adapters, unstable/not-run repeatability, failed baseline preconditions, and identity churn;
- prevents a probe suite with no gating probe from vacuously passing;
- binds profile and suite content through repository-canonical digests;
- keeps the model-judge path outside deterministic gating;
- exposes no approval, promotion, or deployment API.

Adversarial tests now cover:

- correction absent and correction outranked as independent failure shapes;
- anchor absent and anchor demoted as independent failure shapes;
- state-conditioned collapse;
- confidentiality leaks through forbidden item identity and forbidden scope labels;
- scope-label nondeterminism;
- diagnostic confidentiality failure visibility;
- identity churn;
- unsupported deterministic capability;
- deterministic tie-policy requirements;
- timestamp validation;
- adapter request mutation resistance;
- retriever-profile digest changes;
- vacuous-suite rejection.

## Multi-retriever portability checkpoint

The same four-invariant suite passes through two independently shaped deterministic retrievers in the test suite:

1. a table-driven adapter whose ranking is fixture-defined;
2. an independent token-overlap keyword retriever with its own preprocessing, scoring, top-k, and lexical tie policy.

This is preliminary evidence that the 0.1 abstraction is not coupled to one retrieval framework or implementation shape. It satisfies the current engineering checkpoint associated with precommitted kill criterion 5, while leaving room for stronger cross-language or external-retriever evidence later.

## Public reference vectors

`MemoryCheckpointAssessmentReferenceVectors/0.1` currently includes one passing case plus independent negative cases for:

- correction missing;
- correction outranked by the superseded item;
- anchor missing;
- anchor demoted below its maximum rank;
- forbidden item-key scope leak;
- forbidden scope-label leak;
- state-conditioned collapse;
- state-specific required retrieval missing.

These are reference assessment vectors, not AgentTrust conformance vectors. Do not relabel them as conformance material unless maintainers explicitly adopt that status.

## Canonicalization dependency

Agent Manifest issue #322 reports that the repository's shared canonicalization implementation is not fully RFC 8785 conformant. The assessment harness intentionally reuses that shared canonicalizer rather than inventing a second algorithm.

The dependency is now machine-visible through three strict `xfail` tests covering:

- UTF-16 code-unit object-key ordering;
- exponent normalization such as `1e-07` versus `1e-7`;
- over-escaping U+2028.

These expected failures are not assessment-harness failures. They document a known repository-level interoperability defect. Because the tests are strict, an upstream canonicalizer fix that turns them into XPASS will force the dependency test to be reviewed rather than silently leaving stale expectations behind.

Until #322 is resolved, assessment digests must not be described as independently RFC 8785-portable across implementations.

## Vector discipline

Use the independence principle described in trace-spec#124: a rule is not robustly covered merely because one fixture names it. Where practical, provide at least two vectors that can fail under different implementation defects.

The correction and anchor invariants already have two independent negative shapes. Scope isolation is independently exercised through item identity and scope-label leakage. State-conditioned differentiation has collapse and missing-required-item cases.

## Precommitted redesign/stop criteria

Materially redesign or stop this contribution if any of the following is demonstrated:

1. the artifact necessarily duplicates an AgentTrust normative primitive instead of composing with it;
2. stable framework-neutral assessment identity cannot support the four invariants without semantic or LLM inference;
3. evidence cannot remain structurally separate from deployment policy;
4. the first release requires a new signature/envelope standard;
5. deterministic 0.1 cannot support at least two independently shaped retrieval implementations without framework-specific semantics dominating;
6. maintainers move the work to another layer/repository and the artifact boundary cannot survive that move;
7. a concrete counterexample receives `pass` while violating a declared invariant under the same bound inputs and retriever profile.

No kill criterion is currently demonstrated. Criterion 5 has positive preliminary evidence from the two independent retriever fixtures.

## Validation evidence

A fork-only draft PR was used to exercise the repository's actual pull-request workflows against a fork `main` synchronized from current upstream before validation.

Validation branch: `ci/memory-checkpoint-assessment-298`
Validated head: `74abf40f2eff78b468cd7ed5f38dfb0c239c973e`
CI run: `32440131635`
CodeQL run: `32440131747`

All repository CI lanes completed successfully:

- Ruff lint: passed;
- mypy strict type check: passed;
- Bandit: passed;
- pip-audit: passed;
- package build/twine check: passed;
- AGT governance verify in strict mode: passed;
- Python 3.11 on Ubuntu: passed;
- Python 3.12 on Ubuntu: passed;
- Python 3.13 on Ubuntu: passed;
- Python 3.11 on macOS: passed;
- Python 3.11 on Windows: passed;
- CodeQL Python analysis: passed.

The Python 3.11 Ubuntu run reported:

- 1214 collected tests;
- 1205 passed;
- 6 skipped;
- 3 expected failures, all the explicit #322 canonicalization dependency guards;
- total package coverage 89.69 percent;
- `_memory_assessment.py` coverage 93 percent.

The first fork-only CI attempt exposed two contribution-local issues, a mypy local-name redefinition and Bandit's B105 false positive on the public enum token `"pass"`. Both were corrected without weakening the gates. The second run above is the authoritative validation evidence.

## Remaining work before upstream submission

The implementation is no longer blocked by repository validation, but upstream submission still requires explicit maintainer welcome.

Before an eventual upstream PR, perform another adversarial review focused on:

- artifact/schema naming and whether a dedicated JSON Schema should accompany the Pydantic model;
- whether all load-bearing retriever-profile fields are sufficiently portable and unambiguous;
- whether public vectors need a generator/regeneration check like existing Agent Manifest vector suites;
- whether material-access terminology should stay as currently modeled or be refined before becoming externally visible;
- whether canonicalization issue #322 is resolved or must be called out explicitly in the contribution limitations;
- whether the second-retriever evidence is sufficient or should include an independently maintained implementation before submission.

Do not broaden this pass into TRACE, AGT promotion policy, signatures, or framework-specific integrations.

## Eventual upstream PR boundary

If and only if a maintainer explicitly welcomes the contribution and the remaining adversarial review is satisfactory, prepare a narrow PR with:

- What;
- Why;
- Spec impact: none;
- Test plan;
- DCO.

Link #298, but do not automatically close it unless maintainers indicate the artifact/harness work completes the tracker.

Signed-off-by: Kevin Knapp <krknapp@gmail.com>
