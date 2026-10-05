# module for s57 datasource reading
# author: Łukasz Stolzmann

import os
import numpy as np
from osgeo import ogr
from functools import cached_property

class Layer:
    def __init__(self, name, layer_source):
        self.name = name
        self.layer_source = layer_source
    
    @cached_property
    def data(self):
        methods = {'POINT': self._point, 'LINESTRING': self._line, 'POLYGON': self._polygon}
        for feature in self.layer_source:
            geom = feature.GetGeometryRef()
            name = geom.GetGeometryName()
            if 'MULTI' in name:
                name = name[5:]
            break
        return methods[name]()
    
    def _point(self):
        result = []
        for feature in self.layer_source:
            geom = feature.GetGeometryRef()
            for idx in range(geom.GetGeometryCount()):
                result.append([geom.GetGeometryRef(idx).GetX(), geom.GetGeometryRef(idx).GetY()])
        return np.expand_dims(np.array(result), axis=0)
    
    def _line(self):
        result = []
        for feature in self.layer_source:
            geom = feature.GetGeometryRef()
            result.append(np.array(geom.GetPoints()))
        return result

    def _polygon(self):
        result = []
        for feature in self.layer_source:
            geom = feature.GetGeometryRef()
            for idx in range(geom.GetGeometryCount()):
                linear_ring = geom.GetGeometryRef(idx)
                poly = np.array(linear_ring.GetPoints())
                result.append(poly)
        return result

class DataSource:
    def __init__(self, filename):
        self.layers = dict()
        self.filename = filename
        self.data_source = ogr.Open(self.filename, 0)
        self._load_data()

    def _load_data(self):
        if not os.path.exists(self.filename):
            return FileNotFoundError(f'File {self.filename} not found.')
       
        for layer in self.data_source:
            layer_name = layer.GetName()
            self.layers[layer_name] = Layer(layer_name, layer)

    def get_layer_data(self, layer_name):
        return self.layers[layer_name].data