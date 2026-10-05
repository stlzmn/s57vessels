import math
import collections
import pygame as pg
from actor import Actor
from misc import COLOR

class TextBox(Actor):
    def __init__(self, width, height, position, text=''):
        pg.init()
        self.rect = pg.Rect(*position, width, height)
        self.font = pg.font.SysFont('couriernew', 20)
        self.color_border = COLOR['BLACK']
        self.color_inner = COLOR['BLACK']
        self.color_text = pg.Color('white')
        self.text = text

    def set_text(self, text):
        self.text = str(text).replace(', ', '\n').splitlines()

    def handle_events(self, ev):
        if ev.type == pg.MOUSEMOTION and pg.mouse.get_pressed()[2]:
            if self.rect.collidepoint(ev.pos):
                self.rect.left += ev.rel[0]
                self.rect.top += ev.rel[1]

        if ev.type == pg.MOUSEMOTION and pg.mouse.get_pressed()[1]:
            if self.rect.collidepoint(pg.mouse.get_pos()):
                self.rect.w += ev.rel[0] * 8.5
                self.rect.h += ev.rel[1] * 8.5

    def draw(self, surface, color):
        # pg.draw.rect(surface, self.color_inner, self.rect)
        for i, line in enumerate(self.text):
            text_surf = self.font.render(line, True, color)
            surface.blit(text_surf, (self.rect.x + 5, self.rect.y + 5 + i * 20))

    def update_position(self, position):
        self.rect = pg.Rect(*position, self.rect.width, self.rect.height)


class Button(pg.sprite.Sprite, Actor):
    def __init__(self, position, img_path):
        super().__init__()
        img = pg.image.load(img_path)
        img = pg.transform.scale(img, (40, 40))
        self.o_img = pg.Surface((40, 40))
        self.o_img.blit(img, img.get_rect(center=self.o_img.fill((127, 127, 127)).center))
        self.h_img = pg.Surface((40, 40))
        self.h_img.blit(img, img.get_rect(center=self.h_img.fill((228, 228, 228)).center))
        self.image = self.o_img
        self.rect = self.image.get_rect(center=position)
        self.hover = False

    def update(self):
        self.hover = self.rect.collidepoint(pg.mouse.get_pos())
        self.image = self.h_img if self.hover else self.o_img


class Slider():
    def __init__(self, ID, name, screen, val, maxi, mini, xpos, ypos):
        self.id = ID
        self.val = val  # start value
        self.maxi = maxi  # maximum at slider position right
        self.mini = mini  # minimum at slider position left
        self.xpos = xpos  # x-location on self.screen
        self.ypos = ypos
        self.surf = pg.surface.Surface((185, 50))
        self.screen = screen
        self.hit = False  # the hit attribute indicates slider movement due to mouse interaction
        self.font = pg.font.SysFont('arial', 15)
        self._visible = False

        self.txt_surf = self.font.render(name, 1,COLOR['WHITE'])
        self.txt_rect = self.txt_surf.get_rect(center=(92.5, 15))

        # Static graphics - slider background #
        self.surf.fill((100, 100, 100))
        pg.draw.rect(self.surf, COLOR['GREY'], [0, 0, 185, 50], 3)
        pg.draw.rect(self.surf, COLOR['BLACK'], [10, 5, 165, 20], 0)
        pg.draw.rect(self.surf, COLOR['WHITE'], [10, 30, 165, 5], 0)

        self.surf.blit(self.txt_surf, self.txt_rect)  # this surface never changes

        # dynamic graphics - button surface #
        self.button_surf = pg.surface.Surface((20, 20))
        self.button_surf.fill(COLOR['TRANS'])
        self.button_surf.set_colorkey(COLOR['TRANS'])
        pg.draw.circle(self.button_surf, COLOR['BLACK'], (10, 10), 6, 0)
        pg.draw.circle(self.button_surf, COLOR['GREEN'], (10, 10), 4, 0)

        try:
            pos = (10+int((self.val-self.mini)/(self.maxi-self.mini)*160), 33)
            self.button_rect = self.button_surf.get_rect(center=pos)
        except ZeroDivisionError as e:
            pos = 10, 10
            self.button_rect = self.button_surf.get_rect(center=pos)

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value

    def set_pos(self, value):
        self.xpos, self.ypos = value

    def set_text(self, value):
        self.surf.fill(COLOR['BLACK'], self.txt_surf.get_rect(center=(92.5, 15)))
        self.txt_surf = self.font.render(value, 1, COLOR['WHITE'])
        self.txt_rect = self.txt_surf.get_rect(center=(92.5, 15))
        self.surf.blit(self.txt_surf, self.txt_rect)  # this surface never changes

    def get_val(self):
        return int(self.val)

    def draw(self):
        """ Combination of static and dynamic graphics in a copy of the basic slide surface """
        surf = self.surf.copy()
        pos = (10+int((self.val-self.mini)/(self.maxi-self.mini)*160), 33)
        self.button_rect = self.button_surf.get_rect(center=pos)
        surf.blit(self.button_surf, self.button_rect)
        self.button_rect.move_ip(self.xpos, self.ypos)  # move of button box to correct self.screen position
        self.screen.blit(surf, (self.xpos, self.ypos))

    def move(self):
        """ The dynamic part; reacts to movement of the slider button. """
        try:
            self.val = (pg.mouse.get_pos()[0] - self.xpos - 10) / 160 * (self.maxi - self.mini) + self.mini
            if self.val < self.mini:
                self.val = self.mini
            if self.val > self.maxi:
                self.val = self.maxi
        except ZeroDivisionError:
            pass
import random
class WindRose:
    def __init__(self, surface, radius, position):
        self.surface = surface
        self.radius = radius
        self.center = position
        self.angles = collections.deque(maxlen=3)
        self.angles.append(180 - 90)
        self.angles.append(172 - 90)
        self.angles.append(166 - 90)
        self.text = TextBox(90, 30, (self.center[0] - 40, self.center[1] + self.radius + 10))

    def draw(self):
        pg.draw.circle(self.surface, pg.Color('white'), self.center, self.radius, 1)
        if len(self.angles):
            for angle in self.angles:
                angle = math.radians(angle)
                d = math.radians(1)
                points = [
                    (self.center[0] + math.sin(angle) * (self.radius * 0.2), self.center[1] + math.cos(angle) * (self.radius * 0.2)),
                    (self.center[0] + math.sin(angle - d) * (self.radius * 0.8), self.center[1] + math.cos(angle - d) * (self.radius * 0.8)),
                    (self.center[0] + math.sin(angle + d) * (self.radius * 0.8), self.center[1] + math.cos(angle + d) * (self.radius * 0.8))
                ]
                pg.draw.polygon(self.surface, pg.Color('white'), points)
                self.text.draw(self.surface)
                

    def update(self, angle, speed):
        self.angles.append(random.randrange(30, 70) - 90)
        self.text.set_text(f'{speed} Knt.')

    def update_placement(self, center):
        self.center = center
        self.text.update_position((self.center[0] - 40, self.center[1] + self.radius + 10))

