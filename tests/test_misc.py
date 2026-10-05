import pytest

pytest.importorskip('pygame')

from misc import pairwise


def test_pairwise_empty():
    assert list(pairwise([])) == []


def test_pairwise_single_element():
    assert list(pairwise([1])) == []


def test_pairwise_multiple_elements():
    assert list(pairwise([1, 2, 3, 4])) == [(1, 2), (2, 3), (3, 4)]
