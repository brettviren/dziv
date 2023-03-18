#!python

# Copyright 2023 Brett Viren <brett.viren@gmail.com>
#
# This file is part of dziv
#
# dziv is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# dziv is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar. If not, see <https://www.gnu.org/licenses/>.


from pathlib import Path
from functools import cache

class Tiler(object):
    def __init__(self, pyramid, data):
        '''
        Create a pyramid tiler of the data.

        The data should be like image.Data or array.Data
        '''
        self._pyramid = pyramid
        self._pyramid.shape = data.shape
        self._data = data
        
    @cache
    def zoom(self, level):
        '''
        Return a new data zoomed to this level
        '''
        lshape = self._pyramid.level_shape(level)
        return self._data.zoom(lshape)

    def crop(self, level, loc):
        '''
        Return crop of data at given level and tile loc=(row,col)
        '''
        zi = self.zoom(level)
        sl = self._pyramid.slices(level, loc)
        return zi.crop(sl)

    def save(self, directory=Path("."), writer = lambda data,path: data.save(path)):
        '''
        Fully tile, saving the tiles with the per data writer.
        '''
        if isinstance(directory, str):
            directory = Path(directory)

        for layer, loc in self._pyramid.visit:
            path = directory / self._pyramid.filename(layer, loc)
            data = self.crop(layer, loc)
            writer(data, path)
