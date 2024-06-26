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
from PIL import Image
import numpy
from matplotlib import cm

# pil is kind of annoying
def pil_fmt(fmt):
    if fmt is None or fmt.lower() == "jpg":
        return "jpeg"
    return fmt

# avoid PIL.Image.DecompressionBombError
# we are, after all, here to deal with large images.
Image.MAX_IMAGE_PIXELS = 14400 * 14400

def load(image):
    '''
    Return an Image from file name or path.
    '''
    if isinstance(image, Image.Image):
        return image
    if isinstance(image, str):
        image = Path(image)
    if image.name.endswith(".npy"):
        arr = numpy.load(image)
        print(arr.shape)
        eps=10
        arr[arr<eps] = eps
        arr=numpy.log10(arr/eps)
        vmin = numpy.min(arr)
        vmax = numpy.max(arr)
        arr = (arr-vmin) / (vmax-vmin)
        arr[arr < 0.0] = 0.0
        arr[arr > 1.0] = 1.0
        return Image.fromarray(numpy.uint8(cm.plasma(arr)*255))
        # return Image.fromarray(arr.astype('uint8'))
    return Image.open(image)

class Data(object):
    '''
    Adapt PIL image to dzi data model.
    '''
    def __init__(self, image, interpolation = "bicubic"):
        self._image = load(image)
        s = self._image.size
        self.shape = (s[1], s[0])
        self._interpolation = interpolation

    def zoom(self, shape):
        '''
        Return a new Data scaled to fit shape.
        '''
        sz = (shape[1],shape[0])
        filt = getattr(Image, self._interpolation.upper())
        print(f'zoom {self.shape} to {shape} size={self._image.size}')
        newimg = self._image.resize(sz, filt)
        return Data(newimg, self._interpolation)

    def crop(self, slices):
        '''
        Return a new Data in slices 
        '''
        sr, sc = slices
        box = (sc.start, sr.start, sc.stop,  sr.stop)
        print(f'crop shape:{self.shape} size:{self._image.size} to box:{box}')
        newimg = self._image.crop(box)
        return Data(newimg, self._interpolation)

    def save(self, tgt, fmt=None):
        '''
        Save self to target.

        Target may be file name as string or pathlib.Path or a file object.

        A fmt gives the format as a common extension, sans the ".".
        '''
        if isinstance(tgt, str):
            tgt = Path(tgt)
        if isinstance(tgt, Path):
            if not tgt.parent.exists():
                tgt.parent.mkdir(parents=True)
            if fmt is None:
                fmt = tgt.suffix[1:]
        fmt = pil_fmt(fmt)
        print(f'saving: {tgt} {fmt}')
        self._image.save(tgt, format=fmt)
