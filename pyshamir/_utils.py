from ._constants import LOG_TABLE, EXP_TABLE

def add(a, b):
    return a ^ b

def mul(a, b):
    """
    Multiplies two numbers in the finite field GF(256)
    """
    log_a = LOG_TABLE[a]
    log_b = LOG_TABLE[b]
    sum = (int(log_a) + int(log_b)) % 255
    ret = int(EXP_TABLE[sum])
    return int(ret)


def div(a, b):
    """
    Divides two numbers in the finite field GF(256)
    """
    if b == 0:
        raise Exception("Divide by zero")
    log_a = LOG_TABLE[a]
    log_b = LOG_TABLE[b]
    diff = ((int(log_a) - int(log_b)) + 255) % 255
    ret = int(EXP_TABLE[diff])
    return int(ret)

def interpolate_polynomial(x_samples, y_samples, x):
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