# helper functions and constant values
# author: Łukasz Stolzmann

import time
import pygame as pg
from itertools import tee

def fps(func):
    def clocked(*args):
        t0 = time.perf_counter()
        func(*args)
        elapsed = time.perf_counter() - t0
        print(f'FPS: {1/elapsed:.1f}', end='\r')
    return clocked
    
def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

import numpy as np
if __name__ == '__main__':
    line = (1, 2), (3, 4), (5, 6)
    for x in pairwise(line):
        print(x)

KEY_MAP = {pg.K_UP: (1, 0), pg.K_DOWN: (-1, 0), pg.K_RIGHT: (0, 1), pg.K_LEFT: (0, -1)}
COLOR = {
	'BLACK' : (0, 0, 0),
	'WHITE': (255, 255, 255),
	'RED': (255, 0, 0),
	'DARKORANGE': (255, 140, 0),
	'GREEN': (0, 255, 0),
	'MEDIUMSPRINGGREEN': (0, 250, 154),
	'BLUE': (0, 0, 255),
	'DEEPSKYBLUE': (0, 191, 255),
	'ALICEBLUE': (240, 248, 255),
	'TURQUISE': (0, 206, 209),
	'AQUAMARINE': (127, 255, 212),
	'NAVY': (0, 0, 128),
	'PURPLE': (69, 0, 69),
	'MAGENTA': (255, 0, 255),
	'INDIGO': (75, 0, 130),
	'DEEPPINK': (255, 20, 147),
	'CYAN': (51, 255, 255),
	'YELLOW': (255, 255, 0),
	'GOLD': (255, 223, 0),
	'GREY': (200, 200, 200),
	'DIMGREY': (105, 105, 105),
	'DARKGREY': (64, 64, 64),
	'DARKBLUE': (0, 25, 51),
	'ORANGE': (200, 100, 50),
	'TRANS': (1, 1, 1),
}