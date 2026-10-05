#vessels and position handling classes
#author: Łukasz Stolzmann

import collections
from actor import Actor
from dataclasses import dataclass
from nmea_parser import Parser
from pyais import decode_msg
from pyais.exceptions import MissingMultipartMessageException, InvalidNMEAMessageException


Position = collections.namedtuple('Position', field_names=['lat', 'lon', 'sog', 'hdg', 'cog', 'rot', 'wind', 'time', 'pos_type'])

@dataclass
class Vessel:
    mmsi: str
    name: str
    vessel_type: str
    length: float
    
    def __init__(self, mmsi, name, vessel_type, length, beam):
        self.mmsi = mmsi
        self.name = name
        self.vessel_type = vessel_type
        self.length = length
        self.beam = beam
        self._positions = collections.deque(maxlen=5)
        self.to_stern = 0
        self.to_port = 0

    @property
    def position(self):
        return self._positions[-1]
    
    @position.setter
    def position(self, new_position):
        self._positions.append(new_position)

    def __iter__(self):
        for position in self._positions:
            yield position

class VesselDict(collections.UserDict):
    def __init__(self, content, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = content

    def __setitem__(self, mmsi: str, vessel: Vessel):
        if not isinstance(vessel, Vessel):
            raise TypeError('Expected value type: Vessel')
        self.data[str(mmsi)] = vessel
    
    def __contains__(self, mmsi):
        return str(mmsi) in self.data
    
    def __missing__(self, mmsi):
        if isinstance(mmsi, str):
            raise KeyError(f'Vessel: {mmsi} not found')

class OwnShip(Vessel, Actor):
    def __init__(self, mmsi, name, vessel_type, length, beam):
        super().__init__(mmsi, name, vessel_type, length, beam)
        self.position = Position(0., 0., 0., 0., 0., 0., 0., 0., 'DUMMMY')
        self.to_port = 8
        self.to_stern = 80

    @property
    def collzone(self):
        if hasattr(self, '_collzone'):
            return self._collzone
        return None
    
    @collzone.setter
    def collzone(self, value):
        self._collzone = value

class TargetShip(Vessel, Actor):        
    @property
    def initialized(self):
        if hasattr(self, '_fully_initialized'):
            return self._fully_initialized
        
    @initialized.setter
    def initialized(self, value):
        self._fully_initialized = value
            
class Director:
    @classmethod
    def create(cls, destination):
        if destination.content == 'targets':
            obj = super().__new__(TargetShipDirector)
            obj.__init__(destination)
        elif destination.content == 'own_vsl':
            obj = super().__new__(OwnShipDirector)
            obj.__init__(destination)
        return obj

class TargetShipDirector(Director):
    def __init__(self, vessel_buffer):
        self.buffer = vessel_buffer
        self._multipart = []
    
    def decide(self, raw_report):
        tmp_raw = raw_report.split(',')
        if len(tmp_raw) > 7:
            tmp_raw = tmp_raw[1:]
            tmp_raw[0] = '!BSVDM'
            raw_report = ','.join(tmp_raw)
        
        if tmp_raw[1] == '2':
            self._multipart.append(raw_report)

        if len(self._multipart) == 2:
            raw_report = self._multipart
            self._multipart = []
        try:
            if isinstance(raw_report, list):
                msg = decode_msg(*raw_report)
            else:
                msg = decode_msg(raw_report)
        except (MissingMultipartMessageException, InvalidNMEAMessageException) as err:
            # print(err, tmp_raw)
            pass
        else:
            msg = self._handle_unknown_values(msg)
            if msg['type'] not in (5,) and not len(self.buffer):
                self._add_new_vessel(msg)
            if msg['type'] in (5,) and msg['mmsi'] in self.buffer.keys():
                self._add_static_data(msg)
            else:
                if msg['mmsi'] in self.buffer.keys():
                    self._update_old_vessel(msg)
                else:
                    self._add_new_vessel(msg)
            
    def _handle_unknown_values(self, report):
        if 'heading' in report.keys() and report['heading'] == 511:
            report = dict(report) #tworzyc kopie czy nie ??
            report.update({'heading': report['course']})
            return report
        return report

    def _add_new_vessel(self, report):
        try:
            vessel = TargetShip(report['mmsi'], 'UNKNOWN', 'UNKNOWN', 0.0, 0.0)
            vessel.position = Position(report['lat'], report['lon'], report['speed'], report['heading'], report['course'], report['turn'], (0.0, 0.0), report['second'], 'AIS')
            self.buffer[report['mmsi']] = vessel
        except KeyError as e:
            pass

    def _add_static_data(self, report):
        vessel = self.buffer[report['mmsi']]
        vessel.name = report['shipname']
        vessel.vessel_type = report['shiptype']
        vessel.length = sum(map(lambda x: float(x), (report['to_stern'], report['to_bow'])))
        vessel.beam = sum(map(lambda x: float(x), (report['to_port'], report['to_starboard'])))
        vessel.initialized = True
        vessel.to_stern = report['to_stern']
        vessel.to_port = report['to_port']
        self.buffer.update({report['mmsi']: vessel})

    def _update_old_vessel(self, report):
        vessel = self.buffer[report['mmsi']]
        try:
            vessel.position = Position(report['lat'], report['lon'], report['speed'], report['heading'], report['course'], report['turn'], (0.0, 0.0), report['second'], 'AIS')
        except KeyError:
            pass
        self.buffer.update({report['mmsi']: vessel})

class OwnShipDirector(Director):
    def __init__(self, own_vsl):
        try:
            self.own_vsl = list(own_vsl.values())[0]
        except IndexError:
            raise ValueError('Create OwnVessel object.')
        self.position_dict = collections.defaultdict(float)
        self.method_map = {
            '$GPGGA': self._update_position, '$HEHDT': self._update_hdg, '$GPVTG': self._update_cog_sog, 
            '$WIMWV': self._update_wind, '$HEROT': self._update_rot, '$GPRMC': (lambda msg: (self._update_position(msg), self._update_cog_sog(msg)))
        }

    def decide(self, raw_report):
        msg = Parser.parse(raw_report)

        try:
            self.method_map[msg['id']](msg)
        except (KeyError, TypeError):
            pass
        else:
            self.own_vsl.position = Position(
                self.position_dict['lat'], self.position_dict['lon'], self.position_dict['sog'],
                self.position_dict['hdg'], self.position_dict['cog'], self.position_dict['rot'], 
                self.position_dict['wind'], self.position_dict['time'], 'SENSOR'
                )

    def _update_position(self, parsed_msg):
        self.position_dict.update({'lon': parsed_msg['lon'], 'lat':parsed_msg['lat']})

    def _update_hdg(self, parsed_msg):
        self.position_dict.update({'hdg': float(parsed_msg['hdg'])})

    def _update_cog_sog(self, parsed_msg):
        self.position_dict.update({'cog': float(parsed_msg['cog']), 'sog': float(parsed_msg['sog'])})

    def _update_wind(self, parsed_msg):
        self.position_dict.update({'wind': (float(parsed_msg['angle']), float(parsed_msg['speed']))})

    def _update_rot(self, parsed_msg):
        self.position_dict.update({'rot': float(parsed_msg['rot'])})
