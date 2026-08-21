# TRACE #179 intent-to-execution bridge working design

Status: preparatory research only

Upstream tracker: agentrust-io/trace-spec#179
Incubator branch: `research/trace-179-intent-execution-bridge-incubator`
Target upstream repository: `agentrust-io/trace-spec`

## Repository placement note

This document is temporarily stored in the `Knapp-Kevin/agent-manifest` fork because no `Knapp-Kevin/trace-spec` fork exists yet and this work must not live only in chat or local scratch state.

This branch is an incubator, not a proposed Agent Manifest change. Before any upstream contribution, transplant the relevant commits/design into a fork of `agentrust-io/trace-spec` with clean ancestry from the then-current TRACE base.

Do not open an upstream PR, comment on #179, request review, or otherwise submit this work to AgentTrust until a maintainer explicitly welcomes the contribution.

## Upstream problem statement

TRACE records runtime evidence but has no standardized binding to a separately authorized pre-execution intent.

The upstream issue already establishes the initial design constraints:

- use an optional, separately versioned PIC/TRACE bridge artifact and schema;
- compose by reference rather than embedding PIC types into TRACE;
- authorization signature covers the decision and complete bridge authorization object;
- runtime evidence cannot self-assert an `allow` decision;
- verification confirms the signer was authorized for the relevant tool/impact scope;
- preserve PIC-CJSON/1.0 meanings for `intent_digest` and `args_digest`;
- use bridge-specific names such as `declaration_digest` and, once the MCP profile has a canonical call form, `tool_call_digest`;
- bind the authorized intent to the executed call/transcript;
- reuse RFC 8785/JCS rather than inventing another canonicalization layer.

The upstream deliverables are:

1. informative bridge design and threat boundary;
2. versioned JSON Schema;
3. canonical signing and verification rules;
4. deterministic positive and negative vectors;
5. reference verifier behavior.

## Current ecosystem facts that narrow the design

Subsequent cMCP work has already resolved an important upstream question: declared intent is not accepted as a per-call self-assertion from the governed agent.

The current direction places intent in the issuer-signed Agent Manifest, inside the signing pre-image, and carries only its digest into TRACE runtime evidence as `intent_hash`.

That gives the bridge a useful separation of authority:

```text
Agent Manifest
  issuer-signed declared intent
          |
          v
Authorization bridge
  separately signed decision over a proposed action
          |
          v
Runtime enforcement
  cMCP / another enforcement point evaluates and dispatches
          |
          v
TRACE
  records what actually executed
          |
          v
Bridge verification
  proves the executed action corresponds to the authorized decision
```

The bridge therefore should not attempt to infer whether an action is semantically aligned with free-form intent. cMCP currently leaves semantic intent/action comparison unclaimed because that requires model-mediated semantics and a separate trust/attestation story.

## Candidate artifact boundary

Working name only:

`IntentExecutionBridge/0.1`

This name is non-normative and may change if maintainers prefer the existing PIC naming.

The bridge should describe a join between three separately authoritative things:

1. a declared-intent identity already bound by Agent Manifest;
2. an authorization decision made before execution by an authorized decision signer;
3. runtime evidence showing the actual executed call/transcript.

The bridge itself must not become the source of any of those authorities.

## Candidate evidence relationships

A minimal 0.1 design should be capable of binding:

- bridge version/type;
- subject/agent identity or manifest reference;
- declared intent digest;
- declaration digest if distinct from the manifest-carried intent digest;
- authorization decision identifier;
- authorization decision result;
- authorization signer/key identifier or externally resolvable signer reference;
- signer authorization scope reference;
- canonical action/tool-call digest;
- argument digest where PIC semantics require it;
- optional policy identifier/digest used for the authorization decision;
- optional validity window for the authorization decision;
- TRACE record identifier/hash or transcript reference;
- observed runtime tool-call digest;
- verification result with explicit failure reasons.

Do not finalize field names before inspecting current PIC and TRACE schemas in detail.

## Non-goals for 0.1

The first bridge should not:

- decide whether a free-form natural-language intent semantically matches an action;
- make PIC mandatory for TRACE;
- make Agent Manifest mandatory for every TRACE record beyond what the profile itself requires;
- conflate authorization with runtime attestation;
- infer approval from the fact that an action executed;
- treat a valid TRACE signature as authorization;
- define human `step_up`/`defer` lifecycle semantics from trace-spec#191;
- define a new signing envelope;
- define a new canonicalization algorithm;
- claim that execution success means business-world completion.

## Threat boundary

The bridge should be designed to detect at least these deterministic substitution classes:

1. authorized decision replayed for a different agent/manifest;
2. authorized decision replayed for a different run;
3. authorized decision replayed for a different tool/action;
4. arguments changed after authorization;
5. runtime evidence linked to the wrong authorization decision;
6. authorization signer cryptographically valid but not authorized for the declared scope;
7. runtime self-asserted `allow` with no external authorization evidence;
8. stale or expired authorization decision used after its validity window;
9. digest or reference substitution across bridge fields;
10. valid negative authorization outcome misrepresented as permission to execute.

A bridge that cannot distinguish an authentic denial from an authorization failure is underspecified. Negative outcomes are evidence and must remain representable.

## Separation of verdicts

Do not collapse these into one boolean:

- bridge structure/signature authenticity;
- signer authorization;
- declared-intent binding;
- action/argument binding;
- execution-evidence binding;
- authorization outcome;
- runtime outcome.

An authentic bridge may carry a denial. A valid authorization may correspond to a runtime fault. A valid TRACE record may prove that an unauthorized call was attempted. Evidence validity and action admissibility are different questions.

## Canonicalization dependency

The bridge must reuse the project-approved RFC 8785/JCS primitive. However, agent-manifest#322 currently reports a concrete interoperability defect in the Agent Manifest canonicalizer.

Preparatory work must therefore include portable canonicalization boundary vectors. Do not copy the Agent Manifest helper or create another ad hoc serializer merely to make local tests pass.

If the eventual TRACE implementation already uses a standards-conformant RFC 8785 library, prefer that primitive at the bridge layer.

## Deterministic vector plan

Start with synthetic, language-neutral fixtures. At minimum:

### Positive

- valid declared-intent reference + valid authorization + matching executed call;
- valid authorization with an explicit negative runtime outcome;
- valid denied authorization represented as authentic evidence and not admissible for execution.

### Negative

- different manifest/subject;
- different authorization decision id;
- tool/action digest mismatch;
- argument digest mismatch;
- different run identifier;
- wrong TRACE record/transcript reference;
- untrusted authorization signer;
- signer trusted but unauthorized for the tool/impact scope;
- expired/not-yet-valid authorization where validity is present;
- runtime-produced `allow` with no external authorization signature;
- valid denial followed by execution evidence;
- canonicalization boundary cases including non-BMP keys/numeric boundaries if JSON remains in the signed pre-image.

Use the independence discipline from trace-spec#124. Where practical, each load-bearing rule should have more than one vector capable of catching a different defect.

## Relationship to trace-spec#191

TRACE #191 concerns attributable human approval outcomes for `step_up` and `defer` and should remain a follow-on layer.

The #179 bridge should establish the general authorization-to-execution join first. #191 can later supply a human-oversight authorization source or lifecycle without forcing human-specific semantics into the base bridge.

## Kill/redesign criteria

Materially redesign or stop this contribution if:

1. TRACE maintainers decide the join belongs entirely inside an existing profile rather than a separately versioned bridge;
2. preserving PIC-CJSON/1.0 meanings is incompatible with binding the actual execution evidence without semantic reinterpretation;
3. the runtime must self-authorize for the bridge to work;
4. the design requires embedding PIC schemas directly in the TRACE base schema;
5. the design requires a new signing envelope or canonicalization standard;
6. a valid bridge cannot distinguish authentic evidence from authorization/admissibility;
7. canonical action identity cannot be made stable across at least two independently shaped enforcement/runtime producers;
8. a deterministic counterexample can substitute the executed action while all bridge verification rules still pass.

## Preparatory research checklist

Before implementation:

- inspect current trace-spec #179 references and any linked collaborator discussion;
- inspect current PIC schema and canonicalization rules;
- inspect current TRACE schema/profile versioning and extension rules;
- inspect current cMCP `intent_hash` emission path;
- inspect current Agent Manifest intent binding and signer-authority semantics;
- map exact existing identifiers that can be reused rather than duplicated;
- determine whether `tool_call_digest` has a canonical MCP representation yet;
- identify the smallest schema that can express the join without semantic inference;
- draft public vectors before writing the verifier;
- adversarially review the vectors against substitution/replay cases.

## Submission gate

No upstream action until maintainers explicitly indicate the work is welcome.

If welcomed, create or update a proper `Knapp-Kevin/trace-spec` fork, transplant the polished commits onto a branch based on current TRACE main, rerun all target-repository validation, and only then prepare a narrow upstream contribution.

Signed-off-by: Kevin Knapp <krknapp@gmail.com>
