'''
;===================================
; Author: Łukasz Stolzmann
;===================================
'''

import math
import collections
import tkinter as tk
import tkinter.font as tkFont
from itertools import product

def normalize(x, bounds):
    return bounds['desired']['lower'] + (x - bounds['actual']['lower']) * (bounds['desired']['upper'] - bounds['desired']['lower']) / (bounds['actual']['upper'] - bounds['actual']['lower'])

def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x - r, y - r, x + r, y + r, **kwargs)
tk.Canvas.create_circle = _create_circle

def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier

def transparent_icon():
    import tempfile
    import base64, zlib
    ICON = zlib.decompress(base64.b64decode('eJxjYGAEQgEBBiDJwZDBy''sAgxsDAoAHEQCEGBQaIOAg4sDIgACMUj4JRMApGwQgF/ykEAFXxQRc='))
    _, ICON_PATH = tempfile.mkstemp()
    with open(ICON_PATH, 'wb') as icon_file:
        icon_file.write(ICON)
    return ICON_PATH

def trial_man_gui(queue):
    root = tk.Tk()
    root.iconbitmap(default=transparent_icon())
    app = TrialManoeuvreDialog(root, queue)
    root.mainloop()

def settings_ui(queue):
    root = tk.Tk()
    root.iconbitmap(default=transparent_icon())
    app = SettingsDialog(root, queue)
    root.mainloop()


class GenericDialog:
    def _setup_window(self, root, width, height, title):
        root.title(title)
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 4 - 320, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

class SettingsDialog(GenericDialog):
    def __init__(self, root, queue):
        self._setup_window(root, width=300, height=150, title='Settings')

        GLabel_708=tk.Label(root)
        ft = tkFont.Font(family='Times',size=14)
        GLabel_708["font"] = ft
        GLabel_708["fg"] = "#333333"
        GLabel_708["justify"] = "center"
        GLabel_708["text"] = "Color Theme"
        GLabel_708["relief"] = "flat"
        GLabel_708.place(x=10, y=10, width=77, height=20)

        radio_day = tk.Radiobutton(root)
        ft = tkFont.Font(family='Times',size=18)
        radio_day["font"] = ft
        radio_day["fg"] = "#333333"
        radio_day["justify"] = "center"
        radio_day["text"] = "Day"
        radio_day.place(x=10, y=40, width=150, height=30)
        radio_day["command"] = self.radio_day

        radio_night = tk.Radiobutton(root)
        ft = tkFont.Font(family='Times',size=18)
        radio_day["font"] = ft
        radio_day["fg"] = "#333333"
        radio_day["justify"] = "center"
        radio_day["text"] = "Night"
        radio_night.place(x=10, y=60, width=150, height=30)
        radio_day["command"] = self.radio_night

    def radio_day(self):
        print("day palette")

    def radio_night(self):
        print('night palette')
    
class TrialManoeuvreDialog(GenericDialog):
    def __init__(self, root, queue):
        self._setup_window(root, width=600, height=450, title='COLLZONE Trial Maneuver')

        self.queue = queue

        self.selected_circle = collections.deque(maxlen=1)

        self.canvas = tk.Canvas(root)
        self.canvas.create_line(20, 360, 580, 360, fill='black', width=2)
        self.canvas.create_line(300, 360, 300, 40, fill='black', width=2)

        self.canvas.create_text(300, 20, fill='black', text='Course Alteration [°]')
        self.canvas.create_text(530, 390, fill='black', text='Rudder Deflection [°]')

        defl_angles = [-35, -15, -10, -5, 0, 5, 10, 15, 35]
        c_alt_angles = [20, 40, 60]
        
        for angle in defl_angles:
            self.canvas.create_text(normalize(angle,{'actual':{'lower':-35,'upper':35},'desired':{'lower':30,'upper':570}}), 375, fill='black', text=f'{angle}')
        for angle in c_alt_angles:
            self.canvas.create_text(315, normalize(angle,{'actual':{'lower':60,'upper':0},'desired':{'lower':40,'upper':340}}), fill='black', text=f'{angle}')

        angles_prod = list(product([v for v in defl_angles if v != 0], c_alt_angles))
        angles_prod.append((0, 0))
        self.circles = dict()
        for crd in angles_prod:
            self.circles[crd] = self.canvas.create_circle(normalize(crd[0],{'actual':{'lower':-35,'upper':35},'desired':{'lower':30,'upper':570}}),
                                            normalize(crd[1],{'actual':{'lower':60,'upper':0},'desired':{'lower':40,'upper':340}}),
                                            7, fill='blue', outline='#DDD', width=2, tags=f'{crd}')
            self.canvas.tag_bind(self.circles[crd], '<ButtonPress-1>', self.on_object_click)
        self.canvas.pack(fill=tk.BOTH, expand=1)

    def on_object_click(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        item_tag = self.canvas.gettags(item)
        self.selected_circle.append(item_tag)
        self.canvas.itemconfig(item, fill='red')

        for key in self.circles.keys():
            if not str(key) == f'{item_tag[0]} {item_tag[1]}':
                self.canvas.itemconfig(self.circles[key], fill='blue')

        result = self.selected_circle[0]
        r_defl = int(result[0][1:-1])
        c_alt = int(result[1][:-1])
        self.queue.put({'r_defl': r_defl, 'c_alt': c_alt})




