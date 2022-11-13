import secrets
from ._constants import LOG_TABLE, EXP_TABLE

def add(a, b)->int:
    """
    Adds two numbers in the finite field GF(256)
    """
    out = a ^ b
    return out

def mul(a, b)->int:
    """
    Multiplies two numbers in the finite field GF(256)
    """
    log_a = LOG_TABLE[a]
    log_b = LOG_TABLE[b]
    log_sum = (int(log_a) + int(log_b)) % 255
    ret = int(EXP_TABLE[log_sum])

    if a == 0 or b == 0:
        return 0
    
    return int(ret)

def div(a, b)->int:
    """
    Divides two numbers in the finite field GF(256)
    """
    if b == 0:
        raise ZeroDivisionError("Divide by zero")
    log_a = LOG_TABLE[a]
    log_b = LOG_TABLE[b]
    diff = ((int(log_a) - int(log_b)) + 255) % 255
    ret = int(EXP_TABLE[diff])

    if a == 0:
        return 0

    return int(ret)

class Polynomial:
    """
    Takes N sample points and returns the value of the polynomial at x using Lagrange interpolation
    """
    def __init__(self, degree):
        self.coefficients = bytearray(degree + 1)

    def evaluate(self, x)->int:
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

def make_polynomial(intercept, degree)->Polynomial:
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

def interpolate_polynomial(x_samples, y_samples, x)->int:
    """
    Takes N sample points and returns the value of the polynomial at x using Lagrange interpolation
    """
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
