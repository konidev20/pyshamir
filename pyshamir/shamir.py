from ._utils import add, mul, div, interpolate_polynomial


def combine(parts):
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
