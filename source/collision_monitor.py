import enum
import os
import test
import math
import pyproj
import numpy as np
import pygame as pg
from osgeo import ogr
from numba import jit, cuda
from misc import COLOR
from s57 import DataSource

@jit(nopython=True)
def line_intersect(Ax1, Ay1, Ax2, Ay2, Bx1, By1, Bx2, By2):
    """ returns a (x, y) tuple or None if there is no intersection """
    d = (By2 - By1) * (Ax2 - Ax1) - (Bx2 - Bx1) * (Ay2 - Ay1)
    if d:
        uA = ((Bx2 - Bx1) * (Ay1 - By1) - (By2 - By1) * (Ax1 - Bx1)) / d
        uB = ((Ax2 - Ax1) * (Ay1 - By1) - (Ay2 - Ay1) * (Ax1 - Bx1)) / d
    else:
        return
    if not(0 <= uA <= 1 and 0 <= uB <= 1):
        return
    x = Ax1 + uA * (Ax2 - Ax1)
    y = Ay1 + uA * (Ay2 - Ay1)
    
    return x, y

def get_dist(lat1, lon1, lat2, lon2):
    r = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = r * c
    return d

@jit(nopython=True)
def TEST_calculate_xy_for_stationary_object(view_mode, surface_height, own_ship_curr_pos_x, own_ship_curr_pos_y, own_ship_lat, own_ship_lon, own_ship_hdg, own_ship_range, object_coords):
    angle = math.radians(90)

    ts_lat, ts_lon = object_coords
    os_lat, os_lon = own_ship_lat, own_ship_lon

    lat1 = os_lat
    lon1 = os_lon
    lat2 = ts_lat
    lon2 = ts_lon

    diffLong = math.radians(lon2 - lon1)
    x = math.sin(diffLong) * math.cos(math.radians(lat2))
    y = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - math.sin(math.radians(lat1))* math.cos(math.radians(lat2)) * math.cos(diffLong)
    initial_bearing = math.atan2(y, x)
    initial_bearing = math.degrees(initial_bearing)
    fwd_azimuth = initial_bearing

    # degrees_to_radians = math.pi/180.0
    # phi1 = (90.0 - lat1) * degrees_to_radians
    # phi2 = (90.0 - lat2) * degrees_to_radians
    # theta1 = lon1 * degrees_to_radians
    # theta2 = lon2 * degrees_to_radians
    # cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + math.cos(phi1) * math.cos(phi2))
    # arc = math.acos(cos)

    # distance = arc * 6371 / 1.852

    r = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = r * c
    distance = d / 1.852

    x = own_ship_curr_pos_x + ((distance/ own_ship_range) * surface_height / 2 * 0.9) * math.cos(math.radians(fwd_azimuth) - angle)
    y = own_ship_curr_pos_y + ((distance / own_ship_range) * surface_height / 2 * 0.9) * math.sin(math.radians(fwd_azimuth) - angle)

    return x, y


def intersection_examine(enc, view_mode, surface, surface_height, own_ship, own_ship_curr_pos_x, 
                         own_ship_curr_pos_y, own_ship_lat, own_ship_lon, own_ship_hdg, own_ship_range, max_dist=500):
    
    for geom_points in enc.get_layer_data('LNDARE'):
        for idx, _ in enumerate(geom_points):
            p1 = geom_points[idx-1]
            p2 = geom_points[idx]
            # x, y = TEST_calculate_xy_for_stationary_object(view_mode, surface_height, own_ship_curr_pos_x, own_ship_curr_pos_y, own_ship_lat, own_ship_lon, own_ship_hdg, own_ship_range, p1)
            # x1, y1 = TEST_calculate_xy_for_stationary_object(view_mode, surface_height, own_ship_curr_pos_x, own_ship_curr_pos_y, own_ship_lat, own_ship_lon, own_ship_hdg, own_ship_range, p2)
            x, y = calculate_xy_for_stationary_object(surface, own_ship, p1, view_mode)
            x1, y1 = calculate_xy_for_stationary_object(surface, own_ship, p2, view_mode)

            pg.draw.line(surface, COLOR['YELLOW'], (x, y), (x1, y1))
            os_sog, os_hdg = float(own_ship.positions[-1].sog), float(own_ship.positions[-1].hdg)

            x_r1 = own_ship_curr_pos_x + math.cos(math.radians(os_hdg-90)) * ((os_sog * max_dist / 60) / own_ship_range) * surface_height / 2 * 0.9
            y_r1 = own_ship_curr_pos_y + math.sin(math.radians(os_hdg-90)) * ((os_sog * max_dist / 60) / own_ship_range) * surface_height / 2 * 0.9

            intersection = line_intersect(own_ship_curr_pos_x, own_ship_curr_pos_y, x_r1, y_r1, x, y, x1, y1)
            if intersection is not None:
                pg.draw.circle(surface, COLOR['MAGENTA'], intersection, 10, 2)
                    
@cuda.jit
def increment_by_one(arr):
    x, y = cuda.grid(2)
    if x < arr.shape[0] and y < arr.shape[1]:
        arr[x, y] **= 100

import time
if __name__ == '__main__':
    enc = DataSource(os.path.join('maps', 'PL5GDYNA.000'))
    layer_data = enc.get_layer_data('LNDARE')

    threads_per_block = (8, 8)
    data = np.random.rand(1, 2)
    blockspergrid_x = math.ceil(data.shape[0] / threads_per_block[0])
    blockspergrid_y = math.ceil(data.shape[1] / threads_per_block[1])
    blocks_per_grid = (blockspergrid_x, blockspergrid_y)


    # #####################################----------CUDA-------##################################

    start = time.time()
    increment_by_one[blocks_per_grid, threads_per_block](data)
    print(time.time() - start)



    ####################################----------PURE-------##################################

    start = time.time()
    data = np.random.rand(1, 2)
    for x in data:
        x **= 100
    print(time.time() - start)

    
