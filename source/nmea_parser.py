class Parser:
    def __init__(self, sentence):
        return self._preprare_fields(sentence)

    @classmethod
    def parse(cls, sentence):
        for subcls in cls.__subclasses__():
            if subcls.__name__ == sentence.split(',')[0][-3:]:
                obj = super().__new__(subcls)
                return obj.__init__(sentence)
            
    def _process_lat_lon(self, sentence):
        sentence = dict(sentence)
        lat, lon = sentence['lat'], sentence['lon']
        lat_dir = -1 if sentence['lat_dir'] == 'S' else 1
        lon_dir = -1 if sentence['lon_dir'] == 'W' else 1
        lat = float(lat[:2]) + float(lat[2:4]) / 60 + float(lat[4:]) / 60
        lon_d, _, = lon.split('.')
        if len(lon_d) == 5:
            lon = float(lon[:3]) + float(lon[3:5]) / 60 + float(lon[5:]) / 60
        elif len(lon_d) == 4:
            lon = float(lon[:2]) + float(lon[2:4]) / 60 + float(lon[4:]) / 60
        lat *= lat_dir
        lon *= lon_dir
        sentence.update({'lat': lat, 'lon': lon})
        return sentence
            
    def _preprare_fields(self, sentence):
        sentence = dict(zip(self.fields, sentence.split(',')))
        if any(key in sentence.keys() for key in ('lat', 'lon')):
            sentence = self._process_lat_lon(sentence)
        return sentence
        
class GGA(Parser):
    fields = (
        'id', 'utc', 'lat', 
        'lat_dir', 'lon', 'lon_dir', 
        'qual', 'svs', 'hdop', 'ort_len', 
        'unit_of_meas', 'geoid_sep', 'geoid_sep_meas', 
        'dgps_age', 'ref_station', 'checksum')
    
class GLL(Parser):
    fields = (
        'id', 'lat', 'lat_dir', 'lon', 
        'lon_dir', 'utc', 'status', 'checksum'
        )
    
class HDT(Parser):
    fields = (
        'id', 'hdg', 'orient', 'checksum'
    )

class VTG(Parser):
    fields = (
        'id', 'cog', 'cog_orient', 'cog_mag', 'cog_mag_orient', 'sog', 'sog_unit', 'sog_kmph', 'status', 'checksum'
    )

class MWV(Parser):
    fields = (
        'id', 'angle', 'ref', 'speed', 'units', 'status'
    )

class ROT(Parser):
    fields = (
       'id', 'angle', 'status' 
    )

class RMC(Parser):
    fields = (
        'id', 'utc', 'status', 'lat', 
        'lat_dir', 'lon', 'lon_dir', 
        'sog', 'cog', 'date', 'mag_var', 'mag_var_dir', 'checksum'
        )