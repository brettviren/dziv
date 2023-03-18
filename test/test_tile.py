#!/usr/bin/env pytest

from pathlib import Path
from dziv.dzi import Pyramid
from dziv.tile import Tiler

class Dummy(object):
    def __init__(self, shape, saved):
        self.shape = shape
        self.saved = saved
    def zoom(self, shape):
        return Dummy(shape, self.saved)
    def crop(self, slices):
        sr,sc = slices
        return Dummy((sr.stop-sr.start, sc.stop-sc.start), self.saved)
    def save(self, path):
        path = Path(path)
        # print("Dummy.save",path.absolute())
        self.saved.append(path)
        # if not path.parent.exists():
        #     path.parent.mkdir(parents=True)
        # path.open("w").write("%d %d\n" % self.shape)

def test_tiler():
    
    p = Pyramid((1,1))
    shape = (1230,4560)
    saved = list()
    d = Dummy(shape, saved)
    assert d.shape == shape
    t = Tiler(p, d)
    p = t._pyramid
    assert p.shape == shape
    last = p.depth - 1
    print("depth: ", p.depth)
    d2 = t.zoom(last)
    assert d2.shape == d.shape
    d3 = t.zoom(last)
    assert d3.shape == d.shape
    t.save(prefix="test-tile/")
    print ("saved:",len(saved))
    assert len(saved) == 141
    
