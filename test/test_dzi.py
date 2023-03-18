#!/usr/bin/env pytest

from dziv.dzi import ( Pyramid, load)
import pytest

def test_square():
    p = Pyramid((4096,4096))
    maxn = p.tile_size + 2*p.tile_overlap
    assert p.depth == 13
    with pytest.raises(ValueError):
        p.scale(p.depth)
    for l in range(p.depth):
        d = p.level_shape(l)
        assert d == (2**l, 2**l)
        nc, nr = p.tiles_shape(l)
        for ic in range(nc):
            for ir in range(nr):
                rs, cs = p.slices(l,(ir, ic))
                assert rs.start >= 0
                assert cs.start >= 0
                assert rs.stop > 0
                assert cs.stop > 0
                assert rs.stop-rs.start <= maxn
                assert cs.stop-cs.start <= maxn

    assert p.as_dict()
    assert p.as_xml()

def test_io(tmp_path):
    p = Pyramid((333, 291))
    path = tmp_path / "test.dzi"
    p.save(path)

    p2 = load(path)

    assert p.as_dict() == p2.as_dict()
    
def test_visit():
    shape = (1230,4560)
    p = Pyramid(shape)
    p.dump(True)

    
