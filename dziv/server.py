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

from pathlib import Path
from flask import Flask, url_for, send_from_directory, send_file
# from flask_restful import Resource, Api

from .tile import Tiler
from .dzi import Pyramid
from .image import Data as Image
from .web import osd_header

# fixme: this will only work for in-source running!
# fixme: need to install osd/ files!
osd_dir = Path(__file__).parent.parent / "osd"
print("OSD_DIR:", osd_dir)

def create(source):
    if isinstance(source, str):
        source=[source]

    tilers = dict()

    sources = list()
    for one in source:
        path = Path(one)
        if not path.exists():
            raise ValueError(f'no such file or directory: {one}')
        
        ## for a numpy array, this makes a good false color image. 
        # matplotlib.image.imsave('arr.png', arr, cmap='gist_ncar')
        if path.suffix in ('.jpg','.jpeg','.png'):
            sources.append(path)
            d = Image(path)            
            p = Pyramid(d.shape)
            t = Tiler(p,d)

            # for level, loc in p.visit:
            #     t.crop(level, loc) # precalc

            tilers[path] = t
            print(f'TILER for {path} shape:{d.shape}')
        else:
            raise ValueError(f'unsupported format: {path.suffix}')

    app = Flask(__name__)
    assert app.has_static_folder


    @app.route("/")
    def index():
        lines = ['<ul>']
        for num, one in enumerate(sources):
            lines.append(f'<li><a href="/{num}/index.html">{one.stem}</a></li>')
        lines.append('</ul>')
        return '\n'.join(lines)


    @app.route('/favicon.ico')
    def favicon():
        d = Path(".")
        fi = d / "favicon.ico"
        print(f'serve {fi.absolute()}')
        return send_file(fi.absolute())

    @app.route('/osd/<path:path>')
    def send_osd(path):
        # osd = Path("/home/bv/dev/openseadragon/src")
        print(f'serve OSD file: {path} from {osd_dir.absolute()}')
        got = send_from_directory(osd_dir.absolute(), path)
        print("SUCCESS", type(got))
        return got

    ## something asks for /src/openseadragon.js
    @app.route('/src/<path:path>')
    def send_src(path):
        # osd = Path("/home/bv/dev/openseadragon/src")
        print(f'serve OSD file: {path} from {osd_dir.absolute()}')
        got = send_from_directory(osd_dir.absolute(), path)
        return got


    @app.route("/<int:number>/index.html")
    def image_number(number):
        if number < 0 or number >= len(sources):
            raise ValueError("unknown source")
        path = sources[number]

        osd_js_url = f'/osd/openseadragon.js'
        osd_images_url = f'/osd/images/'
        image_dzi = f'/{number}/image.dzi'

        html = f'''
<html>
<head>
<script src="{osd_js_url}"></script>
</head>
<body>
        

<div id="openseadragon{number}" style="width: 800px; height: 600px;"></div>

<script type="text/javascript">
    OpenSeadragon({{
        id: "openseadragon{number}",
        prefixUrl: "{osd_images_url}",
        tileSources: "{image_dzi}",
        minZoomImageRatio: 0.8,
        maxZoomPixelRatio: 8,
        imageSmoothingEnabled: false,
    }});
</script>
</body>
</html>'''
        print(html)
        fp = io.BytesIO()
        fp.write(html.encode())
        fp.seek(0)
        return send_file(fp, download_name=f'{number}.html')


    @app.route("/<int:number>/image.dzi")
    def dzi_number(number):
        '''
        Return the DZI
        '''
        if number < 0 or number >= len(sources):
            raise ValueError("unknown source")
        path = sources[number]
        # print(f'DZI: {number} with {path}')
        t = tilers[path]
        assert(t)
        p = t._pyramid
        fp = io.BytesIO()
        fp.write(p.as_xml().toxml(encoding="UTF-8"))
        fp.seek(0)
        return send_file(fp, mimetype='text/plain') #, download_name=f'image.xml')


    @app.route("/<int:number>/image_files/<int:layer>/<int:col>_<int:row>.<string:fmt>")
    def dzi_tile(number, layer, col, row, fmt):
        if number < 0 or number >= len(sources):
            raise ValueError("unknown source")
        path = sources[number]
        # print(f'DZI image: {number} with {path} {layer} ({row},{col}).{fmt}')
        t = tilers[path]
        assert(t)
        d = t.crop(layer, (row,col))
        fp = io.BytesIO()
        d.save(fp, path.suffix[1:])
        fp.seek(0)
        return send_file(fp, download_name=str(path))

    return app
