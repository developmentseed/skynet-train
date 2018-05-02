# https://github.com/BVLC/caffe/issues/861
import matplotlib
matplotlib.use('Agg')

import json
import os
from os import path as op
import sys
import subprocess

caffe_root = os.getenv('CAFFE_ROOT', '/home/ubuntu/caffe-segnet/')
sys.path.insert(0, caffe_root + 'python')
import caffe
import click
import numpy as np
import rasterio
from mercantile import bounds
from pyproj import Proj, transform
from PIL import Image

from inference import predict
from vectorize import vectorize

dirname = op.dirname(op.realpath(__file__))
polys_to_lines = op.join(dirname, '../vectorize.js')

class TileNotFoundError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


def setup_net(model_file, weights_file, gpu, cpu_only):
    if not op.isfile(weights_file) and op.isdir('/model'):
        caffemodels = filter(lambda x: x.endswith('.caffemodel'), os.listdir('/model'))
        if len(caffemodels) == 0:
            raise Exception('No .caffemodel files found in /model.')
        weights_file = '/model/%s' % caffemodels[0]

    # read model definition
    model = open(model_file, 'r').read()
    # create net
    if cpu_only:
        caffe.set_mode_cpu()
    else:
        caffe.set_mode_gpu()
        caffe.set_device(gpu)

    return caffe.Net(model_file.encode('utf8'),
                     weights_file.encode('utf8'),
                     caffe.TEST)


def make_prediction(net, colors, im, threshold, outfile):
    bands = len(im.getbands())
    imdata = np.array(im.getdata()).reshape(im.size[0], im.size[1], bands)
    predicted = predict(net, colors, threshold, imdata)
    predicted.save(outfile, 'PNG')


def get_image_tile(raster, x, y, z):
    try:
        bound = bounds(x, y, z)

        with rasterio.open(raster) as src:
            x_res, y_res = src.transform[0], src.transform[4]
            p1 = Proj({'init': 'epsg:4326'})
            p2 = Proj(**src.crs)

            # project tile boundaries from lat/lng to source CRS
            tile_ul_proj = transform(p1, p2, bound.west, bound.north)
            tile_lr_proj = transform(p1, p2, bound.east, bound.south)
            # get origin point from the TIF
            tif_ul_proj = (src.bounds.left, src.bounds.top)

            # use the above information to calculate the pixel indices of the window
            top = int((tile_ul_proj[1] - tif_ul_proj[1]) / y_res)
            left = int((tile_ul_proj[0] - tif_ul_proj[0]) / x_res)
            bottom = int((tile_lr_proj[1] - tif_ul_proj[1]) / y_res)
            right = int((tile_lr_proj[0] - tif_ul_proj[0]) / x_res)

            window = ((top, bottom), (left, right))

            # read the first three bands (assumed RGB) of the TIF into an array
            data = np.empty(shape=(3, 256, 256)).astype(src.profile['dtype'])
            for k in (1, 2, 3):
                src.read(k, window=window, out=data[k - 1], boundless=True)

            return Image.fromarray(np.moveaxis(data, 0, -1), mode='RGB')
    except Exception as err:
        raise TileNotFoundError(err)


@click.command()
@click.argument('raster')
@click.argument('tiles')
@click.option('--model', type=str, default='/model/segnet_deploy.prototxt')
@click.option('--weights', type=str, default='/model/weights.caffemodel')
@click.option('--classes', type=str, default='/model/classes.json')
@click.option('--output', type=str, default='/inference')
@click.option('--gpu', type=int, default=0)
@click.option('--cpu-only', is_flag=True, default=False)
@click.option('--threshold', type=float, default=0.5)
def run_batch(raster, tiles, model, weights, classes, output, gpu, cpu_only):
    net = setup_net(model, weights, gpu, cpu_only)

    # read classes metadata
    with open(classes) as c:
        colors = map(lambda x: x['color'][1:], json.load(c))
        colors.append('000000')
        colors = map(lambda rgbstr: tuple(map(ord, rgbstr.decode('hex'))), colors)

    centerlines_file = op.join(output, 'complete.geojson')
    centerlines = open(centerlines_file, 'w')

    with open(tiles) as tile_list:
        for tile in tile_list:
            try:
                click.echo('processing: %s' % tile.strip())
                x, y, z = [int(t) for t in tile.strip().split('-')]
                image = get_image_tile(raster, x, y, z)
                image.save(op.join(output, '%s_real.png' % tile.strip()))

                # run prediction
                predicted_file = op.join(output, '%s.png' % tile.strip())
                make_prediction(net, colors, image, threshold, predicted_file)

                # trace raster -> polygons
                polygonized_file = op.join(output, '%s.geojson' % tile.strip())
                with open(polygonized_file, 'w') as p:
                  p.write(json.dumps(vectorize(predicted_file)))

                # polygons => centerlines
                polyspine_args = map(str, [polys_to_lines, polygonized_file, x, y, z, 0.2])
                exitcode = subprocess.call(polyspine_args, stdout=centerlines)

                if exitcode != 0:
                    raise Exception('Vectorize exited nonzero')

            except TileNotFoundError:
                click.echo('Imagery tile not found.')
            except Exception as err:
                click.echo(err)

    centerlines.close()


if __name__ == '__main__':
    run_batch()
