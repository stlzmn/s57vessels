import pygame as pg
from pygame import gfxdraw
from misc import pairwise

class ENCArtist:
    @classmethod
    def draw_points(cls, screen, xy, where_to_draw, color):
        for pt in xy:
            pg.draw.circle(screen, color, tuple(map(sum, zip(pt, where_to_draw))), 1)

    @classmethod
    def draw_lines(cls, screen, xy, where_to_draw, color):
        for pt_pair in pairwise(xy):
            pt_pair = tuple(map(lambda crd: crd + where_to_draw, pt_pair))
            pg.draw.line(screen, color, pt_pair[0], pt_pair[1])

    @classmethod
    def draw_polygons(cls, screen, polygons, where_to_draw, color, width=1):
        pg.draw.polygon(screen, color, tuple(map(lambda crd: crd + where_to_draw, polygons)), width)
        # gfxdraw.aapolygon(screen, tuple(map(lambda crd: crd + where_to_draw, polygons)), pg.Color('white'))