import pyproj

class Dummy:
    def __init__(self, lon, lat, hdg, sog):
        self.lon = lon
        self.lat = lat
        self.hdg = hdg
        self.cog = hdg
        self.sog = sog

        self.wgs84 = pyproj.Geod(ellps='WGS84')

    def move(self, cog, distance):
        self.lon, self.lat, _ = self.wgs84.fwd(self.lon, self.lat, cog, distance)