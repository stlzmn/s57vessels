"""
Worker-process task that queries the collision-zone (CollZone) database
for the current own-ship/target-ship scenario.

Implementation bodies are intentionally omitted from this public copy;
only signatures are kept so the module still imports and the rest of the
codebase stays structurally intact.
"""
import pyodbc
from collzone import *
from geodesic_calc import relative_pos_comps


class CollzoneTask:
    def __init__(self, os_vsl, ts_vsl, zero_lon, zero_lat, rudder_defl=0, course_alt=0, default_weather=True):
        pass

    def __call__(self, cursor):
        pass

    def query_collzone(self, cursor):
        pass

    def _setup_vsls_dynamic_data(self, os_vsl, ts_vsl):
        pass

    def _setup_wave_params(self, wave_params):
        pass

    def _setup_time(self, time_start):
        pass

    def _setup_os_params(self):
        pass

    def _intermediate_computations(self):
        pass
