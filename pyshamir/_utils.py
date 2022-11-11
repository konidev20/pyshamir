from ._constants import LOG_TABLE, EXP_TABLE

def add(a, b):
    return a ^ b

# mul multiplies two numbers in the finite field GF(256)
def mul(a, b):
    log_a = LOG_TABLE[a]
    log_b = LOG_TABLE[b]
    sum = (int(log_a) + int(log_b)) % 255
    ret = int(EXP_TABLE[sum])
    return int(ret)

# div divides two numbers in the finite field GF(256)
def div(a, b):
    if b == 0:
        raise Exception("Divide by zero")
    log_a = LOG_TABLE[a]
    log_b = LOG_TABLE[b]
    diff = ((int(log_a) - int(log_b)) + 255) % 255
    ret = int(EXP_TABLE[diff])
    return int(ret)