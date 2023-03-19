#!/usr/bin/env python
import sys
import click

from pathlib import Path
from dziv.dzi import Pyramid
from dziv.tile import Tiler
from dziv.image import Data as Image

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
    dziv.server.source = source
    dziv.server.app.run(host="0.0.0.0", port=5100)

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
    
def main():
    cli(obj=None)

if '__main__' == __name__:
    main()
