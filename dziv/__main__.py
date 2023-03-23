#!/usr/bin/env python
import sys
import click

import shutil
from pathlib import Path
from dziv.dzi import Pyramid
from dziv.tile import Tiler
from dziv.image import Data as Image
from dziv.web import osd_header

cmddef = dict(context_settings = dict(help_option_names=['-h', '--help']))
@click.group(**cmddef)
@click.pass_context
def cli(ctx):
    ctx.obj = dict()

@cli.command("serve")
@click.argument('source', nargs=-1)
def serve(source):
    print(source)
    import dziv.server
    app = dziv.server.create(source)
    app.debug = True
    app.run(host="0.0.0.0", port=5100, threaded=False)

@cli.command("tile")
@click.option("-S","--size", default=254, help="Tile size")
@click.option("-O","--overlap", default=1, help="Tile overlap")
@click.option("-f","--format", default=None, help="Output format")
@click.option("-d","--directory", default=None, help="Output directory")
@click.option("-o","--output", default=None, help="Output DZI file")
@click.argument("filename")
def tile(size, overlap, format, directory, output, filename):
    '''
    Fill directory with tree of deep zoom tiles
    '''
    if not any((directory, output)):
        print("require either --directory or --output")
        sys.exit(1)
    if not output:
        output = directory + ".dzi"
    if not directory:
        directory = output.rsplit('.',1)[0]

    output = Path(output)
    directory = Path(directory)

    inpath = Path(filename)
    if not inpath.exists():
        print(f'no such file: {filename}')
        sys.exit(1)
        
    if format is None:
        format = inpath.suffix[1:]

    # for now, just images are assumed
    d = Image(inpath)
    p = Pyramid(d.shape, size, overlap, format)
    t = Tiler(p, d)

    p.save(output)
    t.save(directory)
    
@cli.command("osdweb")
@click.option("-S","--size", default=254, help="Tile size")
@click.option("-O","--overlap", default=1, help="Tile overlap")
@click.option("-f","--format", default=None, help="Output format")
@click.option("-t","--target", default=None, help="Output directory")
@click.option("-u","--url", default=None, help="Base URL")
@click.argument("filename")
def osdweb(size, overlap, format, target, url, filename):
    '''
    Populate a static web area.
    '''
    inpath = Path(filename)
    if not inpath.exists():
        print(f'no such file: {filename}')
        sys.exit(1)
        
    if format is None:
        format = inpath.suffix[1:]

    # for now, just images are assumed
    d = Image(inpath)
    p = Pyramid(d.shape, size, overlap, format)
    t = Tiler(p, d)

    target = Path(target)

    dziname = str(inpath.stem)
    p.save(target / f'{dziname}.dzi')
    t.save(target / f'{dziname}_files' )

    osd = Path("osd")
    header = osd_header(f'{dziname}.dzi', osd, inpath.stem)
    with open(target / f'{inpath.stem}.html', "w") as html:
        html.write(f'<html>\n{header}\n</html>\n')

    shutil.copytree("osd/images", target / osd / "images")
    osdjs = Path("osd/openseadragon.min.js")
    shutil.copy(osdjs, target / osdjs )

def main():
    cli(obj=None)

if '__main__' == __name__:
    main()
