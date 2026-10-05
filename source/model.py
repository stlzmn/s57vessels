class Typed:
    expected_type = type(None)

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = '_' + name

    def __set__(self, instance, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(f'Expected value type: {self.expected_type}')
        setattr(instance, self.private_name, value)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.private_name)
    
class Float(Typed):
    expected_type = float

class String(Typed):
    expected_type = str

class BooleanDefault(Typed):
    expected_type = bool

    def __init__(self, default_value):
        self.default_value = default_value

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return getattr(instance, self.private_name, self.default_value)
        
class GeoCoords(Typed):
    expected_type = tuple

    def __init__(self, default_value):
        self.default_value = default_value

    def __set__(self, instance, value):
        if isinstance(value, self.expected_type) and len(value) == 2:
            setattr(instance, self.private_name, value)
        else:
            raise ValueError('Argument must be a tuple contatining exactly two elements.')
        
    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return getattr(instance, self.private_name, self.default_value)

    

