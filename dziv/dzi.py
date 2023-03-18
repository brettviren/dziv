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

import io
import xml.dom.minidom
from math import (ceil, log)
from pathlib import Path

class Pyramid(object):
    '''
    Describe the pyramid of tiles of an image.
    '''

    def __init__(self, shape,
                 tile_size=254, tile_overlap=1, tile_format="jpg"):
        '''
        Create pyramid for given image shape and square tile size and overlap

        All shapes are ordered like numpy: (nrows, ncols) and NOT like PIL's image.size!
        '''
        self.shape = shape
        self.tile_size = tile_size
        self.tile_overlap = tile_overlap
        self.tile_format = tile_format

    @property
    def depth(self):
        "The number of levels in the pyramid"
        bigger = max(*self.shape)
        return int(ceil(log(bigger, 2))) + 1

    def scale(self, level):
        '''Scale of a pyramid level.

        This is approximately the linear size of a pixel in a level
        measured in the linear size of a pixel in the full scale
        image.
        '''
        self._vet_level(level)
        return 0.5 ** (self.depth - 1 - level)

    def level_shape(self, level):
        "The (nrows,ncols) number of tiles in a level"
        scale = self.scale(level)
        return tuple([int(ceil(s * scale)) for s in self.shape])

    def tiles_shape(self, level):
        "Number of tiles (nrows, ncols)"
        nrc = self.level_shape(level)
        return tuple([ceil(float(s) / self.tile_size) for s in nrc])

    def slices(self, level, loc):
        """Bounding box of the tile at loc=(row,col) as (rows_slice, cols_slice)
        """
        self._vet_level(level)
        ret = list()
        for dim, ls in zip(loc, self.level_shape(level)):
            offset = 0 if dim == 0 else self.tile_overlap
            d = (dim * self.tile_size) - offset
            n = self.tile_size + (1 if dim == 0 else 2) * self.tile_overlap
            n = min(n, ls - d)
            ret.append(slice(d, d+n))
        return tuple(ret)

    def filename(self, level, loc):
        '''
        Return a DZI filename.
        '''
        row, col = loc
        fmt = self.tile_format
        return f'{level}/{col}_{row}.{fmt}'
        
    @property
    def visit(self):
        '''
        Return a generator that iterates over the pyramid.

        Each element is (level, loc) with loc = (irow, icol).

        loc order is column major.
        '''
        for level in range(self.depth):
            ls = self.tiles_shape(level)
            for icol in range(ls[1]):
                for irow in range(ls[0]):
                    yield (level, (irow, icol))

    def _vet_level(self, level):
        "Assure level is valid"
        if 0 <= level and level < self.depth:
            return
        raise ValueError(f'invalid pyramid level: {level}')

    def dump(self, verbose=False):
        print(f'tile: size={self.tile_size} overlap={self.tile_overlap}')
        for l in range(self.depth):
            ls = self.level_shape(l)
            s = self.scale(l)
            tiles = self.tiles_shape(l)
            r = ls[0]/ls[1]
            p = ls[0]*ls[1]
            pos = p/s
            print (f'level {l}: scale={s}, pix={p}, shape={ls}, r={r:.3f}, tiles={tiles}')
            if not verbose:
                continue
            nr,nc = tiles
            for ic in range(nc):
                for ir in range(nr):
                    s = self.slices(l,(ir,ic))
                    fn = self.filename(l, (ir,ic))
                    print(f'\t{s}, {fn}')

    def as_dict(self):
        '''
        Dictionary representation equivalent to OpenSeadragon JSON.

        All leaf values are of string type.
        '''
        xmlns = "http://schemas.microsoft.com/deepzoom/2008";
        return dict(
            Image = dict(
                xmlns    = xmlns,
                Format   = self.tile_format,
                Overlap  = str(self.tile_overlap),
                TileSize = str(self.tile_size),
                Size     = dict(
                    Height = str(self.shape[0]), # nrows
                    Width  = str(self.shape[1]), # ncols
                )))

    def as_xml(self):
        '''
        Return representation of pyramid as XML document in DZI schema
        '''
        d = self.as_dict()
        di = d['Image']
        doc = xml.dom.minidom.Document()
        image = doc.createElementNS(di['xmlns'], "Image")
        for key in 'xmlns TileSize Overlap Format'.split():
            image.setAttribute(key, di[key])
        size = doc.createElementNS(di['xmlns'], "Size")
        ds = di['Size']
        size.setAttribute("Width", ds['Width'])
        size.setAttribute("Height", ds['Height'])
        image.appendChild(size)
        doc.appendChild(image)
        return doc


    def save(self, fp):
        'Save pyramid to DZI XML file name or file object'
        if not isinstance(fp, io.IOBase):
            if not isinstance(fp, Path):
                fp = Path(fp)
            if not fp.parent.exists():
                fp.parent.mkdir(parents=True)
            fp = open(fp, 'wb')
        doc = self.as_xml()
        fp.write(doc.toxml(encoding="UTF-8"))
        fp.close()


def load(source):
    'Read source of DZI XML, return Pyramid'
    if not isinstance(source, io.IOBase):
        source = open(source, 'rb')
    doc = xml.dom.minidom.parse(source)
    image = doc.getElementsByTagName("Image")[0]
    size = doc.getElementsByTagName("Size")[0]
    return Pyramid((int(size.getAttribute("Height")),
                    int(size.getAttribute("Width"))),
                   int(image.getAttribute("TileSize")),
                   int(image.getAttribute("Overlap")),
                   image.getAttribute("Format"))



