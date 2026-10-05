# Radar class for maintaining vessels
# author: Łukasz Stolzmann

import math
import init_params
import collections
from display import EncDisplay
from ship_handling import VesselDict, OwnShip
from geodesic_calc import GeoCalculationMixin

from collision_monitor import line_intersect

class Radar(EncDisplay, GeoCalculationMixin):
    vector_length = init_params.VECTOR_LENGTH
    display_range = init_params.DEFAULT_RANGE
    range_scales = init_params.RANGE_SCALES
    orientation = init_params.DISPLAY_MODE['n_up']
    motion_mode = init_params.MOTION_MODE['rel']

    def __init__(self):
        super().__init__() 
        self._visible_objects = dict()
        self._vessels = VesselDict('targets')
        self._vsl_actors = dict()
        self._own_vsl = VesselDict('own_vsl', {'123456789': OwnShip('123456789', 'OwnShip', 'HSC', 100, 15)})
        self._acquired_vsls = collections.deque(maxlen=1)

        self.reward_pos = None

    @property
    def radar_dims(self):
        return self.disp_width, self.disp_height, self._radius, self.display_range

    @property
    def _radar_center(self):
        return self.disp_width / 2.0, self.disp_height / 2.0
    
    @property
    def _radius(self):
        return self.disp_height / 2 - 10
    
    def _v_end_pt(self, xy, angle, vsl_sog):        
        l_w = ((float(vsl_sog) * self.vector_length / 60) / self.display_range) * self.disp_height
        l_h = ((float(vsl_sog) * self.vector_length / 60) / self.display_range) * self.disp_width 
        l = (l_w ** 2 + l_h ** 2) ** 0.5

        v_line_pt = l * math.cos(math.radians(angle)), l * math.sin(math.radians(angle))
        v_end_x, v_end_y = tuple(map(sum, zip(xy, v_line_pt)))

        return v_end_x, v_end_y   

    def _prepare_for__draw(self, vessel):
        vsl_xy = self.crds_to_xy((vessel.position.lat, vessel.position.lon), self.disp_width, self.disp_height)
        vsl_hdg, vsl_cog, vsl_sog, vsl_rot = vessel.position.hdg, vessel.position.cog, vessel.position.sog, vessel.position.rot
        x, y = tuple(map(sum, zip(self._radar_center, vsl_xy)))

        if self.orientation == 1: # n_up
            '''North up'''
            vsl_hdg = vsl_hdg - 90 #pygame initially _draws relative to x axis
            vsl_cog = vsl_cog - 90 #pygame initially _draws relative to x axis
            
            v_end_x_cog, v_end_y_cog = self._v_end_pt((x, y), vsl_cog, vsl_sog)
            v_end_x_hdg, v_end_y_hdg = self._v_end_pt((x, y), vsl_hdg, vsl_sog)

            rot_dir = 90
            rot_l = vsl_sog / 7
            if vsl_rot in range(-127, 0):
                rot_dir = 270
            elif vsl_rot == 0:
                rot_l = 0.0001
            elif abs(vsl_rot) == 128:
                rot_l = 0.0001

            l_rot = ((float(rot_l) * self.vector_length / 60) / self.display_range) * self._radius
            v_line_pt_rot = [l_rot * func(math.radians(rot_dir + vsl_hdg)) for func in [math.cos, math.sin]]
            v_end_x_rot, v_end_y_rot = tuple(map(sum, zip((v_end_x_hdg, v_end_y_hdg), v_line_pt_rot)))
            vsl_silouette = self._vessel_hull(vessel, (x, y)) if self.display_range <= 3 and vessel.length > 0 else self._vessel_icon(vsl_hdg, (x, y))
            
            return vsl_silouette, (v_end_x_cog, v_end_y_cog), (v_end_x_hdg, v_end_y_hdg), (v_end_x_rot, v_end_y_rot)

        elif self.orientation == 2:# h_up
            '''Heading up'''
            hdg_up_angle = -self.rotation_degree
            ox, oy = self.center_point

            qx = ox + math.cos(math.radians(hdg_up_angle)) * (vsl_xy[0] - ox) - math.sin(math.radians(hdg_up_angle)) * (vsl_xy[1] - oy)
            qy = oy + math.sin(math.radians(hdg_up_angle)) * (vsl_xy[0] - ox) + math.cos(math.radians(hdg_up_angle)) * (vsl_xy[1] - oy)

    def _acquire_target(self, target_vsl):
        target_vsl.lclicked = True if not target_vsl.lclicked else False
        if target_vsl.lclicked:
                self._acquired_vsls.append(target_vsl)
        else:
            if target_vsl in self._acquired_vsls:
                self._acquired_vsls.remove(target_vsl)

    def find_intersections(self, geo_polygon, max_range=3):
        intersections = []
        for idx, _ in enumerate(geo_polygon):
            os_cog = list(self._own_vsl.values())[0].position.cog - 90
            os_sog = list(self._own_vsl.values())[0].position.sog
            for angle in (os_cog - 35, os_cog, os_cog + 35):
                if hasattr(self, 'vsl_center'):
                    vsl_future_pos = self._v_end_pt(self.vsl_center, angle, max_range)
                    if (intersection := line_intersect(*self.vsl_center, *vsl_future_pos, *geo_polygon[idx-1], *geo_polygon[idx])) is not None:
                        intersections.append(intersection)
                        yield intersections

    def dist_os_land(self, geo_polygon, max_range=3):
        pass