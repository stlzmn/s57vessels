import pyproj

class Calculator:
    def __init__(self, measures):
        self.measures = list(map(lambda meas: meas.upper() if meas.islower() else meas, measures))
        self.wgs84 = pyproj.Geod(ellps='WGS84')

    def calculate(self, vsl1, vsl2):
        result = []
        for subcls in self.__class__.__subclasses__():
            if subcls.__name__ in self.measures:
                obj = super().__new__(subcls)
                result.append(obj.calculate(vsl1, vsl2, self.wgs84))
        return result
        
class CPA(Calculator):
    def calculate(self, vsl1, vsl2, wgs84):
        return f'CPA dla {vsl1} i {vsl2} = {0.0}'

class BCR(Calculator):
    def calculate(self, vsl1, vsl2, wgs84):
        return f'BCR dla {vsl1} i {vsl2} = {0.0}'

class DDV(Calculator):
    def calculate(self, vsl1, vsl2, wgs84):
        return f'DDV dla {vsl1} i {vsl2} = {0.0}'

class BRGRNG(Calculator):
    def calculate(self, vsl1, vsl2, wgs84):
        fwd_azim, _, distance = wgs84.inv(vsl1.position.lon, vsl1.position.lat, vsl2.position.lon, vsl2.position.lat)
        return fwd_azim, distance
    
if __name__ == '__main__':
    calc = Calculator(['cpa', 'bcr', 'DDV', 'BRGRNG'])
    for res in calc.calculate(1, 2):
        print(res)
    