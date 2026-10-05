import pytest

import conversion


def test_nm_zero():
    assert conversion.nm(0) == 0


def test_nm_one_nautical_mile_in_meters():
    assert conversion.nm(1852) == pytest.approx(1.0)


def test_nm_known_value():
    assert conversion.nm(3704) == pytest.approx(2.0)
