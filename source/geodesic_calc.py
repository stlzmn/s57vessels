# Mixin class for performing geadesic calculations
# author: Łukasz Stolzmann

import math
import model
import pyproj
import conversion
import numpy as np

class GeoCalculationMixin:
    ref_point = model.GeoCoords((54.4, 18.5))
    wgs84 = pyproj.Geod(ellps='WGS84')

    def crds_to_xy(self, crds, w, h):
        fwd_azimuth, _, dist = self.wgs84.inv(*self.ref_point, *crds[::-1])
        angle_corr = math.radians(90)
        fwd_azimuth = math.radians(fwd_azimuth)
        dist = conversion.nm(dist)
        
        x = (dist / self.display_range) * h * math.cos(fwd_azimuth) - angle_corr
        y = (dist / self.display_range) * w * -math.sin(fwd_azimuth) - angle_corr

        return x, y
    
    def numpy_crds_to_xy(self, batch, w, h):
        for crds in batch:
            ref_pt = np.tile(np.array(self.ref_point), crds.shape[0]).reshape(-1, 2)
            fwd_azimuths, _, dists = self.wgs84.inv(ref_pt[:, 0], ref_pt[:, 1], crds[:, 1], crds[:, 0])

            angle_corr = np.deg2rad(90)
            fwd_azimuths = np.deg2rad(fwd_azimuths)
            dists = conversion.nm(dists)
            
            x = np.expand_dims((dists / self.display_range) * h * np.cos(fwd_azimuths) - angle_corr, axis=1)
            y = np.expand_dims((dists / self.display_range) * w * -np.sin(fwd_azimuths) - angle_corr, axis=1)

            yield np.concatenate([x, y], axis=1)

    def future_position(self, lon, lat, dist, brg):
        endLon, endLat, _ = self.wgs84.fwd(lon, lat, brg, dist)
        return endLon, endLat

class relative_pos_comps(GeoCalculationMixin):
    def __new__(self, obj1: tuple, obj2: tuple):
        fwd_az, _, dist_t = self.wgs84.inv(*obj1, *obj2)
        return  dist_t * math.sin(math.radians(fwd_az)), dist_t * math.cos(math.radians(fwd_az))

        