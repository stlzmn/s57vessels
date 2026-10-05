import pytest

pytest.importorskip('pyproj')

from navi_calculator import Calculator


class Position:
    def __init__(self, lon, lat):
        self.lon = lon
        self.lat = lat


class Vessel:
    def __init__(self, lon, lat):
        self.position = Position(lon, lat)


def test_calculator_normalizes_lowercase_measure_names():
    calc = Calculator(['brgrng'])
    assert calc.measures == ['BRGRNG']


def test_calculator_keeps_already_uppercase_measure_names():
    calc = Calculator(['BRGRNG'])
    assert calc.measures == ['BRGRNG']


def test_brgrng_same_position_has_zero_distance():
    calc = Calculator(['BRGRNG'])
    vsl1 = Vessel(18.5, 54.4)
    vsl2 = Vessel(18.5, 54.4)
    [(bearing, distance)] = calc.calculate(vsl1, vsl2)
    assert distance == pytest.approx(0.0, abs=1e-6)


def test_brgrng_returns_positive_distance_for_different_positions():
    calc = Calculator(['BRGRNG'])
    vsl1 = Vessel(18.5, 54.4)
    vsl2 = Vessel(18.6, 54.5)
    [(bearing, distance)] = calc.calculate(vsl1, vsl2)
    assert distance > 0
