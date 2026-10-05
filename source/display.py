# helper classes for displaying objects on screen
# author: Łukasz Stolzmann

import os
import math
import random
import threading
import itertools
import init_params
import conversion
import numpy as np
import pandas as pd
import pygame as pg
import tkinter_dialogs
from misc import COLOR
from s57 import DataSource
from enc_drawer import ENCArtist
from user_interface import TextBox, Slider, WindRose, Button
from operator import add

class DisplayDims:
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.name == 'height':
            result = instance.screen.get_height()
        elif self.name == 'width':
            result = instance.screen.get_width()
        else:
            raise ValueError('Following string argument must be passed at object initialization: width or height.')
        return result

class Display:
    disp_width = DisplayDims('width')
    disp_height = DisplayDims('height')

    def __init__(self):
        pg.init()
        pg.display.set_caption('ENC')
        self.screen = pg.display.set_mode((init_params.SCREEN_WIDTH, init_params.SCREEN_HEIGHT), pg.RESIZABLE)
        self.terminated = False
        self._setup_controls()
        self._setup_disp_params()

    def _setup_disp_params(self):
        self._current_palette = 'night'
        keys = ['background', 'os', 'ts_init', 'ts_ninit', 'v_hdg', 'v_cog', 'v_rot', 'collzone', 'text', 'poly_fill']
        day_theme = ['DEEPSKYBLUE', 'YELLOW', 'MAGENTA', 'DEEPPINK', 'RED', 'BLACK', 'RED', 'INDIGO', 'BLACK', 0]
        night_theme = ['BLACK', 'YELLOW', 'MAGENTA', 'DEEPPINK', 'RED', 'GREEN', 'RED', 'CYAN', 'WHITE', 1]
        self._theme_colors = {'day': dict(zip(keys, day_theme)), 'night': dict(zip(keys, night_theme))}

    def _setup_controls(self):
        self.text_area_os = TextBox(300, 100, (10, 10))
        self.text_area_ts = TextBox(300, 100, (180, 10))
        self.text_area_collzone = TextBox(300, 100, (350, 10))
        self.slider_cog_alt = Slider('cog_slider', f'ALTER COURSE', self.screen, 0, -25, 25, 10, init_params.SCREEN_HEIGHT - 60)
        self.wind_rose = WindRose(self.screen, 70, (self.disp_width - 80, 80))

        self.button_group = pg.sprite.Group([
            Button((self.disp_width * 0.01 + 20, self.disp_height - 35), 'assets\icon_settings.jpg'),
            Button((self.disp_width * 0.01 + 70, self.disp_height - 35), 'assets\icon_wind.png'),
            Button((self.disp_width * 0.01 + 120, self.disp_height - 35), 'assets\icon_steering_gear.png')
        ])

    def _draw_controls(self):
        self.button_group.draw(self.screen)

        if self.button_group.sprites()[1].lclicked:
            self.wind_rose.draw(self._theme_colors[self._current_palette]['text'])
        

    def _draw_interface(self, enc=False):
        self._visible_objects['radar_circle'] = pg.draw.circle(self.screen, COLOR['WHITE'], self._radar_center, self._radius, 1)
        pg.draw.line(self.screen, COLOR['BLACK'], (self.disp_width / 1.5, 0), (self.disp_width / 1.5, self.disp_height), 1)
        self.screen.fill(COLOR[self._theme_colors[self._current_palette]['background']])
        # self.slider_cog_alt.draw()
        if enc:
            self._draw_enc()
        self._visible_objects['os_place'] = pg.draw.circle(self.screen, COLOR['BLACK'], self._radar_center, 1)

        # pg.draw.line(self.screen, COLOR['WHITE'], 
        #              (self._radar_center[0] - 10, self._radar_center[1]),
        #              (self._radar_center[0] + 10, self._radar_center[1]), 1)
        # pg.draw.line(self.screen, COLOR['WHITE'],
        #              (self._radar_center[0], self._radar_center[1] + 10),
        #              (self._radar_center[0], self._radar_center[1] - 10), 1)
        
        # self._draw_controls()
        
        
        
class EncDisplay(Display):
    enc = DataSource(os.path.join('maps', 'PL5GDYNA.000'))
    
    def change_enc(self, new_enc):
        self.enc = DataSource(os.path.join('maps', new_enc))

    def _vessel_icon(self, angle, xy):
        points = np.array([(-0.5, -0.866), (-0.5, 0.866), (2.0, 0.0)], dtype=np.float32)

        theta = -np.radians(angle)
        c, s = np.cos(theta), np.sin(theta)

        S = np.array(((6, 0), (0, 6)), dtype=np.float32)
        R = np.array(((c, -s,), (s, c)), dtype=np.float32)
        # T = np.array(((1, 0, xy[0]), (0, 1, xy[1])))

        scaled_points = np.dot(points, S)
        rotated_pts = np.dot(scaled_points, R)
        # translated_pts = np.dot(rotated_pts, T)

        translated_pts = [(xy[0] + point[0], xy[1] + point[1]) for point in rotated_pts.tolist()]

        return translated_pts, xy
    
    def _vessel_hull(self, vsl, xy):
        points = np.array([(0.0, 0.0), (0.0, 0.16), (0.8, 0.16), (0.95, 0.12), (1.0, 0.08), (0.95, 0.04), (0.8, 0.0)])

        theta = -np.radians(vsl.position.hdg) + np.radians(90)
        c, s = np.cos(theta), np.sin(theta)

        S = np.array([[vsl.length, 0], [0, vsl.length]])
        R = np.array(((c, -s), (s, c)))
        # T = np.array()

        scaled_points = np.dot(points, S)
        scaled_points[:, 0] = conversion.nm(scaled_points[:, 0]) / self.display_range * self.disp_height
        scaled_points[:, 1] = conversion.nm(scaled_points[:, 1]) / self.display_range * self.disp_width
        rotated_pts = np.dot(scaled_points, R)

        off_center = [float(vsl.to_stern), float(vsl.to_port)]
        off_center[0] = conversion.nm(off_center[0]) / self.display_range * self.disp_height
        off_center[1] = conversion.nm(off_center[1]) / self.display_range * self.disp_width
        off_center = np.dot(np.array([off_center]), R)
        off_x, off_y = off_center[0]

        translated_pts = [(xy[0] + point[0] - off_x, xy[1] + point[1] - off_y) for point in rotated_pts]
        
        return translated_pts, xy
        
    def _draw_collzone(self, own_vsl, center):
        if (collzone := own_vsl.collzone) is not None:
            df = pd.DataFrame(collzone[0])
            angle = math.radians(float(own_vsl.position.hdg))
            vec_wh = (self.disp_height ** 2 + self.disp_width ** 2) ** 0.5
            points = []
            for index, _ in df.iterrows():
                x = center[0] + (((df.at[index, 'mdtc_nm']) / self.display_range) * vec_wh) * math.sin(df.at[index, 'bearing_rad'] + angle)
                y = center[1] + (((df.at[index, 'mdtc_nm']) / self.display_range) * vec_wh) * -math.cos(df.at[index, 'bearing_rad'] + angle)
                points.append((x, y))

            for i, pt in enumerate(points):
                prev = points[i-1]
                curr = points[i]
                pg.draw.line(self.screen, COLOR[self._theme_colors[self._current_palette]['collzone']], prev, curr, 2)

    def _draw_vessels(self):
        os_list = list(self._own_vsl.values())
        ts_list = list(self._vessels.values())

        for vessel in itertools.chain(os_list, ts_list):
            (vessel_icon, center), v_end_pt_cog, v_end_pt_hdg, v_end_rot = self._prepare_for__draw(vessel)
            os_info, ts_info = '', ''
            if vessel.__class__.__name__ == 'OwnShip':
                vessel_color = COLOR['YELLOW']
                self.vsl_center = center
                os_info = f'OWN VESSEL\nCOG: {round(vessel.position.cog, 3)}, HDG: {round(vessel.position.hdg, 3)}, SOG: {round(vessel.position.sog, 3)}'
                self._draw_collzone(vessel, center)

            elif vessel.__class__.__name__ == 'TargetShip':
                vessel_color = COLOR[self._theme_colors[self._current_palette]['ts_init']] if not vessel.initialized else COLOR[self._theme_colors[self._current_palette]['ts_ninit']]
                ts_info = f'TARGET VESSEL\nCOG: {round(vessel.position.cog, 3)}, HDG: {round(vessel.position.hdg, 3)}, SOG: {round(vessel.position.sog, 3)}'
                if hasattr(vessel, 'brg_rng_ts'):
                    ts_info += f'\nBRG: {vessel.brg_rng_ts[0] if vessel.brg_rng_ts[0] >= 0 else vessel.brg_rng_ts[0]+360 :.2f}, RNG: {vessel.brg_rng_ts[1] / 1852:.2f}'
                

            #vsl antenna
            if self.display_range <= 3:
                pg.draw.circle(self.screen, COLOR['RED'], center, 3)
            #hdg & cog
            pg.draw.line(self.screen, COLOR[self._theme_colors[self._current_palette]['v_cog']], center, v_end_pt_cog, 1)
            pg.draw.line(self.screen, COLOR[self._theme_colors[self._current_palette]['v_hdg']], center, v_end_pt_hdg, 1)
            #rate of turn
            pg.draw.line(self.screen, COLOR[self._theme_colors[self._current_palette]['v_rot']], v_end_pt_hdg, v_end_rot, 1)

            # self.text_area_os.set_text(os_info)
            self.text_area_os.draw(self.screen, self._theme_colors[self._current_palette]['text'])
            self.text_area_collzone.draw(self.screen, self._theme_colors[self._current_palette]['text'])

            if vessel.lclicked:
                # pg.draw.polygon(self.screen, COLOR['INDIGO'], vessel_icon)
                pg.draw.circle(self.screen, COLOR['YELLOW'], center, 17, 1)
                
                self.text_area_ts.set_text(ts_info)
                self.text_area_ts.draw(self.screen, self._theme_colors[self._current_palette]['text'])

            if vessel.rclicked:
                pass
                
            self._vsl_actors[vessel.mmsi] = pg.draw.polygon(self.screen, vessel_color, vessel_icon, 2)

    def _draw_enc(self, detect_coll=False):
        draw_method = {'LNDARE': ENCArtist.draw_polygons}#
        for lyr_name, func in draw_method.items():
            for xy in self.numpy_crds_to_xy(self.enc.get_layer_data(lyr_name), self.disp_width, self.disp_height):
                func(self.screen, xy, self._radar_center, init_params.ENC_COLOR[lyr_name], self._theme_colors[self._current_palette]['poly_fill'])
                # self._draw_os_intrs(tuple(map(lambda crd: crd + self._radar_center, xy)))

    def _draw_os_intrs(self, geo_polygon):
        for intersections in self.find_intersections(geo_polygon):
            if intersections is not None:
                for intersection in intersections:
                    if hasattr(self, 'vsl_center'):
                        pg.draw.line(self.screen, COLOR['ORANGE'], self.vsl_center, intersection, 1)
                        pg.draw.circle(self.screen, COLOR['MAGENTA'], intersection, 8, 2)

    def _draw_reward(self):
        if self.reward_pos is None:
            self.reward_pos = self.enc.get_layer_data('SOUNDG').squeeze()
            self.reward_pos = self.reward_pos[np.random.randint(0, self.reward_pos.shape[0] - 1)]
        xy = self.crds_to_xy(self.reward_pos, self.disp_width, self.disp_height)
        xy = list(map(add, xy, self._radar_center))
        pg.draw.circle(self.screen, COLOR['RED'], xy, 10)
                    