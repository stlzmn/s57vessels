# application logic
# author: Łukasz Stolzmann

import sys
import queue
import threading
import pygame as pg
import multiprocessing
import tkinter_dialogs
from misc import fps
from radar import Radar
from dataflow import NMEADataStream, DatabaseConsumer
from init_params import AIS_ADDRESS, AIS_PORT, AIS_ADDRESS_SZWECJA, AIS_PORT_SZWECJA
from user_interface import TextBox
from navi_calculator import Calculator
from collzone_handler import CollzoneTask

class Application(Radar):
    def __init__(self):
        super().__init__()
        self._setup_data_streams()
        self._setup_nav_tools()
        self._setup_init()

    def _setup_init(self):
        self.frame = 0

    def _setup_data_streams(self):
        self._ais_stream = NMEADataStream.from_server(addr=AIS_ADDRESS, port=AIS_PORT, destination=self._vessels)
        # self._ais_stream_szwecja = NMEADataStream.from_server(addr=AIS_ADDRESS_SZWECJA, port=AIS_PORT_SZWECJA, destination=self._vessels)

        self._gps_stream = NMEADataStream.from_serial('COM2', 4800, destination=self._own_vsl)
        # self._gps_stream = NMEADataStream.from_server(addr='192.168.1.101', port=8040, destination=self._own_vsl)
        # self._os_cdn_stream = NMEADataStream.from_serial(port='COM3', baudrate=480, destination=self._own_vsl)

        # self._ais_stream.run()
        # self._ais_stream_szwecja.run()

        self._gps_stream.run()
        # self._os_cdn_stream.run()

        self._collzone_tasks = multiprocessing.JoinableQueue()
        self._collzone_results = multiprocessing.Queue()
        self._collzone_consumer = DatabaseConsumer(self._collzone_tasks, self._collzone_results)
        self._collzone_consumer.start()

        self._trial_input_queue = queue.Queue()
        self._settings_signals_queue = queue.Queue()

    def _setup_nav_tools(self):
        self._navi_meas = Calculator(['BRGRNG'])

    # @fps
    def run(self):
            running = True
            while running:
                if self.terminated:
                    running = False
                self._event_loop()
                self._update_values()
                self._update_ui()
                self._draw()
                pg.display.update()
            self._quit()

    def _event_loop(self):
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                self.terminated = True

            if ev.type == pg.MOUSEBUTTONDOWN:
                if any(list(map(lambda target: target.collidepoint(pg.mouse.get_pos()), self._vsl_actors.values()))):
                    for (mmsi, target) in self._vsl_actors.items():
                        if target.collidepoint(pg.mouse.get_pos()):
                            if pg.mouse.get_pressed()[0]:
                                if mmsi in self._vessels.keys():
                                    self._acquire_target(self._vessels[mmsi])
                                elif mmsi in self._own_vsl.keys():
                                    self._own_vsl[mmsi].lclicked = True if not self._own_vsl[mmsi].lclicked else False
                                else:
                                    continue
                            if pg.mouse.get_pressed()[2]:
                                if mmsi in self._vessels.keys():
                                    self._vessels[mmsi].rclicked = True if not self._vessels[mmsi].rclicked else False
                                    print(f'{self._vessels[mmsi].to_stern=}, {self._vessels[mmsi].to_port=}, {self._vessels[mmsi].length=}, {self._vessels[mmsi].beam=}')
                                elif mmsi in self._own_vsl.keys():
                                    self._own_vsl[mmsi].rclicked = True if not self._own_vsl[mmsi].rclicked else False
                                    print(self._own_vsl[mmsi].position)
                                else:
                                    continue
                if self.slider_cog_alt.button_rect.collidepoint(pg.mouse.get_pos()) and self.slider_cog_alt.visible:
                    self.slider_cog_alt.hit = True

                for sprite in self.button_group.sprites():
                    if sprite.hover:
                        if pg.mouse.get_pressed()[0]:
                            sprite.lclicked = True if not sprite.lclicked else False

                if self.button_group.sprites()[2].lclicked:
                    if not hasattr(self, 't_trial_dialog'):
                        self.t_trial_dialog = threading.Thread(target=tkinter_dialogs.trial_man_gui, args=(self._trial_input_queue,))
                        self.t_trial_dialog.start()                        
                if not self.button_group.sprites()[2].lclicked:
                    if hasattr(self, 't_trial_dialog'):
                        self.t_trial_dialog.join()
                        delattr(self, "t_trial_dialog")
                if self.button_group.sprites()[0].lclicked:
                    self._current_palette = 'day'
                    # if not hasattr(self, 't_settings_dialog'):
                    #     self.t_settings_dialog = threading.Thread(target=tkinter_dialogs.settings_ui, args=(self._settings_signals_queue,))
                    #     self.t_settings_dialog.start()  
                if not self.button_group.sprites()[0].lclicked:
                    self._current_palette = 'night'
                    # if hasattr(self, 't_settings_dialog'):
                    #     self.t_settings_dialog.join()
                    #     delattr(self, "t_settings_dialog")

            if ev.type == pg.MOUSEMOTION and pg.mouse.get_pressed()[0]:
                self.ref_point = tuple(map(sum, zip(self.ref_point, map(lambda val: val * 0.00005 * self.display_range, (ev.rel[1], -ev.rel[0])))))

            if ev.type == pg.MOUSEWHEEL and self._visible_objects['radar_circle'].collidepoint(pg.mouse.get_pos()):
                self.display_range = self.range_scales[max(0, min(self.range_scales.index(self.display_range) - ev.y, len(self.range_scales) - 1))]
                pg.display.set_caption(f'RANGE: {self.display_range} NM')
                
                if self.display_range > 5:
                    self.change_enc('PL2MP500.000')
                if self.display_range <= 5:
                    self.change_enc('PL5GDYNA.000')

            if ev.type == pg.VIDEORESIZE:
                self.wind_rose.update_placement((self.disp_width - 80, 80))
                for offset, sprite in zip((20, 70, 120), self.button_group.sprites()):
                    sprite.rect = sprite.image.get_rect(center=(self.disp_width * 0.01 + offset, self.disp_height - 35))

    def _update_values(self):
        self.wind_rose.update(10, 20)
        #send collzone query task to background process

        

        for mmsi, own_vsl in self._own_vsl.items():
            if not len(self._acquired_vsls):
                continue
            self._acquired_vsls[-1].brg_rng_ts = self._navi_meas.calculate(own_vsl, self._acquired_vsls[-1])[0]

            try:
                own_vsl.r_defl, own_vsl.c_alt = self._trial_input_queue.get(timeout=0.0001).values()
            except queue.Empty:
                pass

            if self.frame % 100 == 0:
                if hasattr(own_vsl, 'r_defl'):
                    self.text_area_collzone.set_text(f'Rudder Deflection: {own_vsl.r_defl}°\nCourse Alteration: {own_vsl.c_alt}°')
                    self._collzone_tasks.put(CollzoneTask(own_vsl, self._acquired_vsls[-1], *self.ref_point[::-1], rudder_defl=own_vsl.r_defl, course_alt=own_vsl.c_alt))
                self.frame = 0

            try:
                collzone_result = self._collzone_results.get(timeout=0.0001)
            except queue.Empty:
                continue
            else:
                own_vsl.collzone = collzone_result
        self.frame += 1

        
        # for intersection in self.obs_generator():
        #     print(intersection)
        
    def _update_ui(self):
        self.button_group.update()
                
    def _draw(self):
        self._draw_interface(enc=True)
        self._draw_vessels()   
        self._draw_reward()

    def obs_generator(self):
        for xy in self.numpy_crds_to_xy(self.enc.get_layer_data('LNDARE'), self.disp_width, self.disp_height):
            yield from self.find_intersections(tuple(map(lambda crd: crd + self._radar_center, xy)))

    def _quit(self):
        self._gps_stream.terminate()
        self._ais_stream.terminate()
        # self._ais_stream_szwecja.terminate()
        self._collzone_consumer.terminate()
        
        self._collzone_tasks.put(None)
        self._collzone_tasks.join()

        self.t_trial_dialog.join()
        
        pg.quit()
        sys.exit()