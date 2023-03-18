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

import scipy



def Data(object):

    def __init__(self, array, order = 3):
        '''
        Create a Data from an array.

        The order gives the zoom interpolation order.
        '''
        self._array = array
        self._order = order

    @property
    def shape(self):
        return self._array.shape[:2]

    def zoom(self, shape):
        '''
        Return a new Data scaled to fit shape.
        '''
        s = self.shape
        zf = [1.0]*len(s)
        zf[0] = shape[0] / s[0]
        zf[1] = shape[1] / s[1]
        new = scipy.ndimage.zoom(self._array, zf, self._order)
        return Data(new, self._order)

    def crop(self, slices):
        '''
        Return a new Data in slices 
        '''
        sls = [slice(0, n) for n in self._array.shape]
        sls[0] = slices[0]
        sls[1] = slices[1]
        sls = tuple(sls)
        return Data(self._array[sls], self._order)

    def save(self, tgt, fmt=None):
        '''
        Save self to target.

        Target may be file name as string or pathlib.Path or a file object.
        '''
        if isinstance(tgt, str):
            tgt = Path(tgt)
        if isinstance(tgt, Path):
            if not tgt.parent.exists():
                tgt.parent.mkdir(parents=True)
            if fmt is None:
                fmt = tgt.suffix[1:]
        if fmt is None:
            fmt = "npz"
        if fmt == "npy":
            numpy.save(tgt, self._array)
            return
        if fmt == "npz":
            numpy.savez_compressed(tgt, {path.stem, self._array})
            return
        # o.w. we assume image
        scipy.misc.imsave(tgt, self._array, format=fmt);

