#base classes for object displaying purposes
#author: Łukasz Stolzmann

import model

class Actor:
    '''This class is to be inherited by objects designated to draw'''
    drawable = model.BooleanDefault(True)
    lclicked = model.BooleanDefault(False)
    rclicked = model.BooleanDefault(False)

    def on_click(self):
        print('drawing circle around me {self.mmsi}')
