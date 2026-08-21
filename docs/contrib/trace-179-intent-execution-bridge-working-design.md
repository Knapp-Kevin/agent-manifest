# TRACE #179 reconciliation record

Status: upstream implementation already merged; do not duplicate

Upstream tracker: agentrust-io/trace-spec#179
Merged implementation: agentrust-io/trace-spec#180
Merge commit: `70ec2e52b4db976155bb80317972b59db842a6c1`
Incubator branch: `research/trace-179-intent-execution-bridge-incubator`

## Why this record exists

Preparatory research initially treated #179 as an open implementation lane because the issue is still open and has no comments. Repository inspection then found that PR #180 already merged and explicitly states that it implements #179.

This record preserves that correction so later work does not rediscover the stale issue state and accidentally build a second bridge.

## What already landed

The merged TRACE implementation provides an optional PIC-CJSON/1.0 to TRACE authorization bridge with:

- an informative bridge design and threat boundary;
- a versioned JSON Schema at `schema/pic-trace-bridge-v1.json`;
- a reference implementation in `agentrust_trace.intent_bridge`;
- a detached authorization artifact signed by an authorizer key resolved from verifier trust configuration;
- no embedded trust anchor in the signed artifact;
- preservation of PIC-CJSON/1.0 `intent_digest` and `args_digest` semantics;
- bridge-specific RFC 8785/JCS digests for the declaration and executed tool call;
- tool and impact scope checks;
- authorization validity-window checks;
- transcript before/after binding when required;
- fail-closed error semantics for malformed/unverifiable evidence, denial, and execution mismatch;
- focused positive and negative security tests.

The merged documentation identifies the profile as a detached authorization artifact and keeps it outside the base TRACE Trust Record schema.

## Architectural boundary now established

The ecosystem already has the core separation we were considering:

```text
pre-execution authorization
        |
        v
PIC/TRACE bridge
        |
        v
runtime execution evidence
        |
        v
TRACE verification
```

The runtime cannot bootstrap authorization by embedding its own key or self-asserting `allow`.

This means there is no value in opening a second #179 implementation or proposing a competing schema.

## Residual review questions worth keeping in mind

Future work may still need to test or extend the merged bridge at adjacent boundaries, but those should be separate issues and must not be framed as unfinished #179 implementation unless maintainers say otherwise.

Potential review surfaces include:

1. signer authorization beyond matching `authorizer_key_id` to a trusted JWK `kid`, if tool/impact-specific signer authority needs stronger expression;
2. independent-vector depth for every load-bearing rule, following trace-spec#124;
3. canonicalization interoperability, particularly while agent-manifest#322 documents an RFC 8785 defect in the sibling repository;
4. attributable human `step_up`/`defer` outcomes tracked in trace-spec#191;
5. versioning and fallback behavior for any future bridge revision;
6. replay and binding coverage across authorization id, run identity, action identity, and transcript identity;
7. cross-runtime portability of `tool_call_digest` if additional enforcement systems consume the bridge.

These are review/research leads, not claims of current defects.

## Submission boundary

Do not post to #179 or open a PR to "complete" it. The implementation already exists upstream.

If a concrete, independently demonstrated defect is later found in the merged bridge, track it as a separate focused issue and wait for the same maintainer-welcome boundary before submitting implementation work.

## Repository placement note

This branch remains an incubator record in `Knapp-Kevin/agent-manifest` because no `Knapp-Kevin/trace-spec` fork currently exists. It should not be proposed upstream from this repository.

Signed-off-by: Kevin Knapp <krknapp@gmail.com>
