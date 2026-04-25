from __future__ import annotations

import secrets
from ctypes import c_uint8


def add(a: int, b: int) -> int:
    """
    Adds two numbers in the finite field GF(256)
    """
    out = a ^ b
    return out


def inverse(a: int) -> int:
    b = mul(a, a)
    c = mul(a, b)
    b = mul(c, c)
    b = mul(b, b)
    c = mul(b, c)
    b = mul(b, b)
    b = mul(b, b)
    b = mul(b, c)
    b = mul(b, b)
    b = mul(a, b)
    return mul(b, b)


def mul(a: int, b: int) -> int:
    a_u = c_uint8(a)
    b_u = c_uint8(b)
    r = c_uint8(0)
    i = 8

    while i > 0:
        i -= 1
        p1 = -(c_uint8(b_u.value >> i).value & 1) & a_u.value
        p2 = -(c_uint8(r.value >> 7).value) & 0x1B
        p3 = c_uint8(2 * r.value)
        r = c_uint8(p1 ^ p2 ^ p3.value)

    return r.value


def div(a: int, b: int) -> int:
    a_u = c_uint8(a)
    b_u = c_uint8(b)

    if b_u.value == 0:
        raise ZeroDivisionError("Divide by zero")
    ret = mul(a_u.value, inverse(b_u.value))

    if a_u.value == 0:
        return 0

    return ret


class Polynomial:
    """Polynomial in GF(256), evaluated via Horner's method."""

    def __init__(self, degree: int) -> None:
        self.coefficients = bytearray(degree + 1)

    def evaluate(self, x: int) -> int:
        # origin case
        if x == 0:
            return self.coefficients[0]

        # compute the polynomial value using Horner's method
        degree = len(self.coefficients) - 1
        out = self.coefficients[degree]
        for i in range(degree - 1, -1, -1):
            coeff = self.coefficients[i]
            out = add(mul(out, x), coeff)
        return out


def make_polynomial(intercept: int, degree: int) -> Polynomial:
    """
    Creates a random polynomial with the given intercept and degree
    :param intercept:
    :param degree:
    :return:
    """
    polynomial_instance = Polynomial(degree)

    # Set the intercept
    polynomial_instance.coefficients[0] = intercept

    # assign random co-efficients to the polynomial
    polynomial_instance.coefficients[1:] = secrets.token_bytes(degree)

    return polynomial_instance


def interpolate_polynomial(x_samples: bytearray, y_samples: bytearray, x: int) -> int:
    """Lagrange-interpolate N sample points in GF(256), returning the value at x."""
    limit = len(x_samples)
    result = 0
    for i in range(limit):
        basis = 1
        for j in range(limit):
            if i != j:
                num = add(x, x_samples[j])
                den = add(x_samples[i], x_samples[j])
                term = div(num, den)
                basis = mul(basis, term)
        group = mul(y_samples[i], basis)
        result = add(result, group)
    return result


def generate_x_coordinates(n: int) -> list[int]:
    x_coordinates = list(range(n))
    secrets.SystemRandom().shuffle(x_coordinates)
    return x_coordinates
