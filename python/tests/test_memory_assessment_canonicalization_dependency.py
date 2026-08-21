from __future__ import annotations

import pytest

from agent_manifest._canonicalize import canonicalize


_BLOCKER = pytest.mark.xfail(
    strict=True,
    reason=(
        "agent-manifest#322: shared canonicalizer is not yet fully "
        "RFC 8785 conformant"
    ),
)


@_BLOCKER
def test_rfc8785_orders_object_keys_by_utf16_code_units() -> None:
    value = {"\ue000": 2, "😀": 1}
    assert canonicalize(value) == '{"😀":1,"\ue000":2}'.encode()


@_BLOCKER
def test_rfc8785_normalizes_exponent_leading_zero() -> None:
    assert canonicalize(1e-7) == b"1e-7"


@_BLOCKER
def test_rfc8785_does_not_overescape_line_separator() -> None:
    assert canonicalize({"value": "\u2028"}) == '{"value":"\u2028"}'.encode()
