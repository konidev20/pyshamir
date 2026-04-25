"""Hypothesis-based property tests for the GF(256) primitives in pyshamir._utils.

These complement the explicit-value tests in test_utils.py by sweeping random
inputs across the full byte domain and shrinking failures to minimal
counterexamples. Each test pins an algebraic invariant of the field; together
they form a partial fuzzing harness recognized by OpenSSF Scorecard's
`Fuzzing` check.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from pyshamir._utils import (
    add,
    div,
    interpolate_polynomial,
    inverse,
    make_polynomial,
    mul,
)

byte = st.integers(min_value=0, max_value=255)
nonzero_byte = st.integers(min_value=1, max_value=255)
small_degree = st.integers(min_value=2, max_value=8)


# ----- add (XOR) field axioms -----


@given(a=byte, b=byte)
def test_add_is_commutative(a: int, b: int) -> None:
    assert add(a, b) == add(b, a)


@given(a=byte, b=byte, c=byte)
def test_add_is_associative(a: int, b: int, c: int) -> None:
    assert add(add(a, b), c) == add(a, add(b, c))


@given(a=byte)
def test_add_zero_is_identity(a: int) -> None:
    assert add(a, 0) == a


# ----- mul field axioms -----


@given(a=byte, b=byte)
def test_mul_is_commutative(a: int, b: int) -> None:
    assert mul(a, b) == mul(b, a)


@given(a=byte, b=byte, c=byte)
def test_mul_distributes_over_add(a: int, b: int, c: int) -> None:
    assert mul(a, add(b, c)) == add(mul(a, b), mul(a, c))


@given(a=byte)
def test_mul_one_is_identity(a: int) -> None:
    assert mul(a, 1) == a


# ----- inverse / div -----


@given(a=nonzero_byte)
def test_inverse_is_multiplicative_inverse(a: int) -> None:
    assert mul(a, inverse(a)) == 1


@given(a=byte, b=nonzero_byte)
def test_div_inverts_mul(a: int, b: int) -> None:
    assert div(mul(a, b), b) == a


# ----- Polynomial / Lagrange round-trip -----


@settings(max_examples=200)
@given(intercept=byte, degree=small_degree)
def test_interpolate_recovers_intercept(intercept: int, degree: int) -> None:
    """For any random polynomial of degree d with intercept I,
    sampling at d+1 distinct non-zero x's and interpolating at x=0 yields I.
    """
    poly = make_polynomial(intercept, degree)
    xs = bytearray(range(1, degree + 2))
    ys = bytearray([poly.evaluate(x) for x in xs])
    assert interpolate_polynomial(xs, ys, 0) == intercept
