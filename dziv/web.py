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

from .tile import Tiler
from .dzi import Pyramid
from .image import Data as Image

def osd_header(dzi_url, osd_url="", divid="osd1"):
    'Return HTML for OSD widget'
    return f'''
<div id="{divid}" style="width: 800px; height: 600px;"></div>
<script src="{osd_url}/openseadragon.min.js"></script>
<script type="text/javascript">
    var viewer = OpenSeadragon({{
        id: "{divid}",
        prefixUrl: "{osd_url}/images/",
        tileSources: "{dzi_url}"
    }});
</script>'''

def populate_relative(tgt, img, base_url):
    '''
    Populate a relative web directory with everything needed
    '''
    tgt = Path(tgt)
    img = Path(img)

    d = Image(image)
    p = Pyramid(d.shape)
    t = Tiler(p,d)
    t.save(tgt)

    dzifname = img.name + ".dzi"
    osd = osd_header(f'{base_url}/{dzifname}', f'{base_url}/osd')
    with open(tgt / "index.html") as html:
        html.write(f'''<html>\n{osd}\n</html>\n''')
    shutil.copytree("osd/images", tgt / "osd/images")
    
