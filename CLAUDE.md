# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Python port of HashiCorp Vault's `shamir` package (Go) implementing Shamir's Secret Sharing. The public API is just `split(secret, parts, threshold)` and `combine(parts)`, exported from `pyshamir/__init__.py`.

When behavior of the algorithm is ambiguous, the Go original is the source of truth: https://github.com/hashicorp/vault/tree/main/shamir. Match its semantics rather than inventing new ones.

## Commands

Tests use `pytest` with `pytest-cov`. Lint is `ruff` (check + format), type-check is `mypy --strict`. All tool config lives in `pyproject.toml`.

```sh
# Run all tests
pytest

# Run a single test
pytest tests/test_utils.py::test_mul_known_vectors

# Run tests with coverage
pytest --cov=pyshamir --cov-report=term-missing

# Lint + format check
ruff check pyshamir tests
ruff format --check pyshamir tests

# Type-check (strict)
mypy pyshamir

# Multi-version matrix via tox
tox                    # py39..py313 + lint + type
tox -e py311           # single Python
tox -e lint            # ruff only
tox -e type            # mypy only
tox -e coverage        # writes coverage.xml + htmlcov/
```

Pre-commit hooks (ruff, ruff-format, mypy --strict, plus standard whitespace/yaml hooks) are configured in `.pre-commit-config.yaml`. Install with `pre-commit install` after cloning.

## Architecture

Two-file core; treat them as a unit when changing the algorithm.

**`pyshamir/shamir.py`** — public `split` / `combine`. Wire format: each "part" is a `bytearray` of length `len(secret) + 1`; the **final byte** holds the x-coordinate (offset by +1 so it's never 0), and bytes `0..len(secret)-1` hold the polynomial evaluations at that x for each secret byte. `combine` reverses this by reading the last byte as x, then Lagrange-interpolating each byte position back to x=0. Both `parts` and `threshold` must be ≥2 and ≤255.

**`pyshamir/_utils.py`** — GF(256) finite field arithmetic and the `Polynomial` class. `add` is XOR; `mul` implements the Rijndael/AES reduction polynomial (0x1B) and uses `ctypes.c_uint8` for exact 8-bit wraparound that matches the Go reference. `inverse` is a fixed exponentiation chain (a^254). `make_polynomial` builds a degree-`(threshold-1)` polynomial with a fixed intercept (the secret byte) and **cryptographically random coefficients via `secrets.token_bytes`** — do not swap to `random` or any non-CSPRNG source. `generate_x_coordinates` likewise uses `secrets.SystemRandom().shuffle`.

`Polynomial.evaluate` uses Horner's method over GF(256). `interpolate_polynomial` is Lagrange interpolation in GF(256) — note `add` is XOR so `add(a, b)` doubles as both addition and subtraction.

`tests/test_utils.py` exercises the GF(256) primitives directly (FIPS 197 worked vectors, Rijndael overflow, the `inverse(0)` edge case, a make/sample/interpolate round-trip). When changing math in `_utils.py`, run that file specifically — failures land closer to the broken primitive than they would going through `split`/`combine`.

## Conventions

- **PEP-585 generic type hints are allowed** (`list[bytearray]`, `dict[int, bool]`). They work under py3.9 because both source files start with `from __future__ import annotations`, which defers all annotation evaluation to strings. Don't add them to a file that's missing the `__future__` import without also adding the import.
- **`mypy --strict` must stay green.** New functions need full type annotations; new module-level re-exports need an `__all__` entry in `pyshamir/__init__.py`.
- **Don't reword exception messages.** Tests in `tests/test_shamir.py` match them with `pytest.raises(..., match=...)`; changing an error string will break tests in another file.
- **Version source**: `__version__` in `pyshamir/__init__.py` is read at build time by `pyproject.toml`'s `[tool.setuptools.dynamic] version = { attr = ... }`. Bumping the version is a one-line change there; tag release commits as `chore: bump version to vX.Y.Z`.
- **License is MPL-2.0** (since commit 983d9f1). The SPDX expression in `pyproject.toml` and the matching `LICENSE` file are the canonical source — don't add `License :: ...` classifiers (PEP 639 reserves them as mutually exclusive with the SPDX form).
