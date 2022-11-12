import secrets

from ._utils import add, mul, div , make_polynomial


def interpolate_polynomial(x_samples: bytearray, y_samples: bytearray, x: int):
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


def combine(parts: list[bytearray]) -> bytearray:
    """
    Takes a list of parts and returns the secret
    :param parts:
    :return:
    """
    # Verify enough parts are present
    if len(parts) < 2:
        raise ValueError("Not enough parts to combine")

    # Verify all parts are all the same length
    first_part_len = len(parts[0])

    if first_part_len < 2:
        raise ValueError("Part is too short")

    for part in parts:
        if len(part) != first_part_len:
            raise ValueError("Parts are not the same length")

    # Create a buffer to store the reconstructed secret
    secret = bytearray(first_part_len - 1)

    # Buffer to store the samples
    x_samples = bytearray(len(parts))
    y_samples = bytearray(len(parts))

    # set the x value for each sample and ensure the no_sample values are the same , otherwise div() can be unhappy
    check_map = {}

    for i, part in enumerate(parts):
        samp = part[first_part_len - 1]
        if samp in check_map:
            raise ValueError("Duplicate sample")
        check_map[samp] = True
        x_samples[i] = samp

    # Reconstruct each  byte
    for idx, _ in enumerate(secret):
        for i, part in enumerate(parts):
            y_samples[i] = part[idx]

        # interpolate the polynomial and compute the vault at 0
        val = interpolate_polynomial(x_samples, y_samples, 0)

        # Evaluate the 0th value to get the intercept
        secret[idx] = val

    return secret


def split(secret: bytes, parts: int, threshold: int) -> list[bytearray]:
    """
    Takes a secret and splits it into parts
    :param secret:
    :param parts:
    :param threshold:
    :return:
    """
    # Sanity check the input
    if parts < threshold:
        raise ValueError("Parts must be greater than threshold")
    if parts > 255:
        raise ValueError("Parts must be less than 256")
    if threshold < 2:
        raise ValueError("Threshold must be greater than 1")
    if threshold > 255:
        raise ValueError("Threshold must be less than 256")
    if len(secret) < 1:
        raise ValueError("Secret must be at least 1 byte long")

    # Generate random list of x coordinates
    x_coordinates = [secrets.randbelow(255) for _ in range(1, 256)]

    # Allocate the output array , initalize the final byte of the output with the offset.
    # This is used to ensure that the same secret can be split into different parts
    output = [bytearray() for _ in range(parts)]
    for i in range(len(output)):
        output[i] = bytearray(len(secret) + 1)
        output[i][len(secret)] = int(x_coordinates[i]) + 1

    for i, val in enumerate(secret):
        polynomial_instance = make_polynomial(val, int(threshold - 1))

        for j in range(parts):
            x = int(x_coordinates[j]) + 1
            y = polynomial_instance.evaluate(x)
            output[j][i] = y

    return output







