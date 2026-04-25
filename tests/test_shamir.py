from __future__ import annotations

import itertools
from base64 import b64decode

import pytest

from pyshamir import combine, split

SPLIT_SECRET = b64decode("a+m4G0kEkKDQK4MFGz7L0vLz5oViQkDSLThiC4zDRZU=")
COMBINE_SECRET = b64decode("esfX3MUC++BrcwkiwsKtK6M5Pi5yvuc/A/6LweWJ5FA=")


def test_split_returns_correct_part_count_and_length():
    parts = split(SPLIT_SECRET, 5, 3)
    assert len(parts) == 5
    for part in parts:
        assert len(part) == len(SPLIT_SECRET) + 1


def test_split_produces_distinct_parts():
    parts = split(SPLIT_SECRET, 5, 3)
    for i in range(len(parts) - 1):
        assert parts[i].hex() != parts[i + 1].hex()


@pytest.mark.parametrize(
    "parts, threshold, message",
    [
        (0, 0, "Parts and threshold must be greater than 1"),
        (2, 3, "Parts must be greater than threshold"),
        (1000, 3, "Parts must be less than 256"),
    ],
)
def test_split_invalid_arguments(parts, threshold, message):
    with pytest.raises(ValueError, match=message):
        split(SPLIT_SECRET, parts, threshold)


@pytest.mark.parametrize("secret", [None, bytearray(b"")], ids=["none", "empty"])
def test_split_invalid_secret(secret):
    with pytest.raises(ValueError, match="Secret must be at least 1 byte long"):
        split(secret, 5, 3)


@pytest.mark.parametrize(
    "indices",
    list(itertools.combinations(range(5), 3)),
    ids=lambda x: "+".join(str(i) for i in x),
)
def test_combine_recovers_secret_from_any_threshold_subset(indices):
    parts = split(COMBINE_SECRET, 5, 3)
    selected = [parts[i] for i in indices]
    assert combine(selected) == COMBINE_SECRET


@pytest.mark.parametrize("parts", [None, bytearray()], ids=["none", "empty"])
def test_combine_with_too_few_parts(parts):
    with pytest.raises(ValueError, match="Not enough parts to combine"):
        combine(parts)


def test_combine_with_mismatched_part_lengths():
    with pytest.raises(ValueError, match="Parts are not the same length"):
        combine([bytearray(b"ab"), bytearray(b"abc")])


def test_combine_with_too_short_parts():
    with pytest.raises(ValueError, match="Part is too short"):
        combine([bytearray(b"a"), bytearray(b"b")])


def test_combine_with_duplicate_samples():
    with pytest.raises(ValueError, match="Duplicate sample"):
        combine([bytearray(b"ab"), bytearray(b"ab")])
