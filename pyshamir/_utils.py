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
