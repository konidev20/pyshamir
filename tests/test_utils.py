"""Direct tests for the GF(256) primitives in pyshamir._utils.

These functions are exercised transitively through split/combine in
test_shamir.py, but direct tests pin the cryptographic invariants
(field axioms, AES Rijndael polynomial reduction, Horner evaluation,
Lagrange interpolation) and surface failures closer to their root cause.
"""

from __future__ import annotations

import pytest

from pyshamir._utils import (
    Polynomial,
    add,
    div,
    generate_x_coordinates,
    interpolate_polynomial,
    inverse,
    make_polynomial,
    mul,
)

# ----- add -----


@pytest.mark.parametrize(
    "a, b", [(a, b) for a in [0, 1, 0x55, 0xAA, 0xFF] for b in [0, 1, 0x55, 0xAA, 0xFF]]
)
def test_add_is_xor(a, b):
    assert add(a, b) == a ^ b


def test_add_zero_is_identity():
    for a in range(256):
        assert add(a, 0) == a
        assert add(0, a) == a


def test_add_self_is_zero():
    for a in range(256):
        assert add(a, a) == 0


# ----- mul -----


def test_mul_zero_annihilates():
    for a in range(256):
        assert mul(a, 0) == 0
        assert mul(0, a) == 0


def test_mul_one_is_identity():
    for a in range(256):
        assert mul(a, 1) == a
        assert mul(1, a) == a


@pytest.mark.parametrize(
    "a, b, expected",
    [
        # mul(2, x) doubles in GF(256); high-bit overflow XORs the Rijndael 0x1B.
        (2, 1, 2),
        (2, 0x40, 0x80),
        (2, 0x80, 0x1B),
        # 3 = 2 ^ 1, so mul(3, 7) = mul(2, 7) ^ mul(1, 7) = 14 ^ 7 = 9.
        (3, 7, 9),
        # FIPS 197 §4.2 worked example: 0x57 * 0x83 = 0xC1.
        (0x57, 0x83, 0xC1),
    ],
)
def test_mul_known_vectors(a, b, expected):
    assert mul(a, b) == expected


def test_mul_is_commutative():
    for a in [0x12, 0x34, 0x56, 0x78]:
        for b in [0x9A, 0xBC, 0xDE, 0xF0]:
            assert mul(a, b) == mul(b, a)


# ----- inverse -----


def test_inverse_times_self_is_one():
    for a in range(1, 256):
        assert mul(a, inverse(a)) == 1


def test_inverse_of_zero_is_zero():
    # 0 has no true multiplicative inverse; the exponentiation chain
    # collapses to 0, matching the Go reference.
    assert inverse(0) == 0


# ----- div -----


def test_div_by_zero_raises():
    with pytest.raises(ZeroDivisionError, match="Divide by zero"):
        div(5, 0)


def test_div_zero_numerator_returns_zero():
    for b in range(1, 256):
        assert div(0, b) == 0


def test_div_inverts_mul():
    for a in [0x01, 0x42, 0xAB, 0xFF]:
        for b in [0x01, 0x42, 0xAB, 0xFF]:
            assert div(mul(a, b), b) == a


# ----- Polynomial.evaluate -----


def test_polynomial_evaluate_at_zero_returns_intercept():
    p = Polynomial(3)
    p.coefficients[0] = 0x42
    p.coefficients[1] = 0x11
    p.coefficients[2] = 0x22
    p.coefficients[3] = 0x33
    assert p.evaluate(0) == 0x42


@pytest.mark.parametrize("x", [1, 2, 0x55, 0xAA, 0xFF])
def test_polynomial_evaluate_matches_manual_horner(x):
    p = Polynomial(3)
    p.coefficients[0] = 0x05
    p.coefficients[1] = 0x07
    p.coefficients[2] = 0x0B
    p.coefficients[3] = 0x0D

    # Horner: ((c3 * x + c2) * x + c1) * x + c0, with + as XOR in GF(256).
    expected = p.coefficients[3]
    expected = add(mul(expected, x), p.coefficients[2])
    expected = add(mul(expected, x), p.coefficients[1])
    expected = add(mul(expected, x), p.coefficients[0])

    assert p.evaluate(x) == expected


# ----- make_polynomial -----


def test_make_polynomial_sets_intercept_and_size():
    poly = make_polynomial(0x77, 5)
    assert poly.coefficients[0] == 0x77
    assert len(poly.coefficients) == 6  # degree + 1


# ----- interpolate_polynomial round-trip -----


@pytest.mark.parametrize("intercept", [0x00, 0x01, 0x55, 0xAA, 0xFF])
def test_interpolate_recovers_intercept(intercept):
    """Build a degree-3 polynomial, sample 4 distinct x's, interpolate at x=0."""
    poly = make_polynomial(intercept, 3)
    xs = bytearray([1, 2, 3, 4])
    ys = bytearray([poly.evaluate(x) for x in xs])
    assert interpolate_polynomial(xs, ys, 0) == intercept


# ----- generate_x_coordinates -----


def test_generate_x_coordinates_returns_permutation():
    n = 100
    xs = generate_x_coordinates(n)
    assert len(xs) == n
    assert sorted(xs) == list(range(n))


def test_generate_x_coordinates_is_shuffled():
    # Two independent calls on n=100 collide with probability 1/100! ≈ 0.
    assert generate_x_coordinates(100) != generate_x_coordinates(100)
