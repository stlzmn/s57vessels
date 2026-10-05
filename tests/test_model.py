import pytest

from model import Float, String, BooleanDefault, GeoCoords


class Dummy:
    lat = Float()
    name = String()
    active = BooleanDefault(default_value=True)
    position = GeoCoords((0.0, 0.0))


def test_float_accepts_float():
    d = Dummy()
    d.lat = 54.4
    assert d.lat == 54.4


def test_float_rejects_non_float():
    d = Dummy()
    with pytest.raises(TypeError):
        d.lat = 'not a float'


def test_string_accepts_str():
    d = Dummy()
    d.name = 'own ship'
    assert d.name == 'own ship'


def test_boolean_default_uses_default_when_unset():
    d = Dummy()
    assert d.active is True


def test_boolean_default_can_be_overridden():
    d = Dummy()
    d.active = False
    assert d.active is False


def test_geocoords_default():
    d = Dummy()
    assert d.position == (0.0, 0.0)


def test_geocoords_accepts_two_element_tuple():
    d = Dummy()
    d.position = (54.4, 18.5)
    assert d.position == (54.4, 18.5)


def test_geocoords_rejects_wrong_length():
    d = Dummy()
    with pytest.raises(ValueError):
        d.position = (1.0, 2.0, 3.0)


def test_geocoords_rejects_non_tuple():
    d = Dummy()
    with pytest.raises(ValueError):
        d.position = [1.0, 2.0]
