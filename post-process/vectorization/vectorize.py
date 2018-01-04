#!/usr/bin/env python
import os
import sys
import json
import argparse
import glob
from datetime import datetime
import gippy
import numpy as np
from osgeo import osr
from pyproj import Proj, transform
from pygeotile.tile import Tile
import logging


__version__ = '0.1.1'
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout)


def lines_to_features(lines):
    """ Create features from lines """
    gid = 0
    features = []
    for line in lines:
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': line
            },
            'properties': {
                'id': gid
            }
        }
        features.append(feature)
        gid += 1
    geojson = {
        'type': 'FeatureCollection',
        'features': features,
    }
    return geojson


def trace_line(arr, endpoint):
    """ Trace a line starting with an endpoint """
    # loop until another endpoint is reached
    pt = endpoint
    line = [[pt[0]+0.5, pt[1]+0.5]]
    i = 0
    while True:
        # zero out current point
        arr[pt[0], pt[1]] = 0
        # extract subarray
        xmin, xmax = max(0, pt[0]-1), min(arr.shape[0], pt[0]+2)
        ymin, ymax = max(0, pt[1]-1), min(arr.shape[1], pt[1]+2)
        subarr = arr[xmin:xmax, ymin:ymax]
        # locate next point
        loc = np.where(subarr > 1)
        if len(loc[0]) == 0:
            break
        pt = [loc[0][0]+xmin, loc[1][0]+ymin]
        line.append([pt[0]+0.5, pt[1]+0.5])
        # check if endpoint
        val = arr[pt[0], pt[1]]
        if val != 3:
            arr[pt[0], pt[1]] = 0
            xmin, xmax = max(0, pt[0]-1), min(arr.shape[0], pt[0]+2)
            ymin, ymax = max(0, pt[1]-1), min(arr.shape[1], pt[1]+2)
            subarr = arr[xmin:xmax, ymin:ymax]
            # decrement any remaining pixels in local region
            for x in range(xmin, xmax):
                for y in range(ymin, ymax):
                    arr[x, y] = max(0, arr[x, y]-1)
            break
        i = i+1
    return line


def vectorize(img):
    """ Vectorize a raster skeleton """
    # get convolution of 3x3 with skeleton
    kernel = np.ones((3, 3))
    skel = img[0].skeletonize().read()
    skelconv = img[0].skeletonize().convolve(kernel, boundary=False).read()
    skelconv[skel == 0] = 0
    img[1].write(skelconv)
    # img[2].write(skelconv)

    lines = []
    # Create list of 2D points
    pts = [list(coord_arr) for coord_arr in np.where(skelconv == 2)]
    pts = np.vstack(pts).T

    while len(pts) > 0:
        # start with an endpoint and trace the entire line, pt by pt
        pt = [pts[0][0], pts[0][1]]
        line = trace_line(skelconv, pt)
        lines.append(line)

        # Recalculate point list since 1 line has been recorded and removed
        pts = [list(coord_arr) for coord_arr in np.where(skelconv == 2)]
        pts = np.vstack(pts).T
    img[2].write(skelconv)
    return lines


def open_tile(filename, outdir='./'):
    """ Open a tile image and assign projection and geotransform """
    img = gippy.GeoImage(filename)
    z, x, y = map(int, img.basename().split('-'))
    tile = Tile.from_tms(tms_x=x, tms_y=y, zoom=z)
    img[0] = (img[0] == 255)
    fout = os.path.join(outdir, img.basename() + '.tif')
    geoimg = img.save(fout, options={'COMPRESS': 'DEFLATE'})
    geoimg.set_srs('EPSG:3857')
    minpt = tile.bounds[0].meters
    maxpt = tile.bounds[1].meters
    affine = np.array(
        [
            minpt[0], (maxpt[0]-minpt[0])/geoimg.xsize(), 0.0,
            abs(minpt[1]), 0.0, -(maxpt[1]-minpt[1])/geoimg.ysize()
        ])
    geoimg.set_affine(affine)
    return geoimg


def main(filename, outdir='./'):
    start0 = datetime.now()
    geoimg = open_tile(filename, outdir=outdir)
    logger.debug('Open tile (%s)' % (datetime.now() - start0))

    start = datetime.now()
    lines = vectorize(geoimg)
    logger.debug('Vectorize tile (%s)' % (datetime.now() - start))

    # geolocate
    start = datetime.now()
    srs = osr.SpatialReference(geoimg.srs()).ExportToProj4()
    projin = Proj(srs)
    projout = Proj(init='epsg:4326')
    newlines = []
    for line in lines:
        newline = []
        for point in line:
            pt = geoimg.geoloc(point[1], point[0])
            # convert to lat-lon
            pt = transform(projin, projout, pt.x(), pt.y())
            newline.append(pt)
        newlines.append(newline)
    logger.debug('Transform coordinates (%s)' % (datetime.now() - start))

    geojson = lines_to_features(newlines)
    fout = os.path.join(outdir, geoimg.basename() + '.geojson')
    with open(fout, 'w') as f:
        f.write(json.dumps(geojson))
    logger.info('Completed vectorization in %s' % (datetime.now() - start0))


def parse_args(args):
    """ Parse arguments for the NDWI algorithm """
    desc = 'Binary image vectorization (v%s)' % __version__
    dhf = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description=desc, formatter_class=dhf)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--filename', help='Input PNG tile')
    group.add_argument('-d', '--directory', help='Input directory')

    parser.add_argument('--outdir', help='Save intermediate files to this dir (otherwise temp)', default='')
    h = '0: Quiet, 1: Debug, 2: Info, 3: Warn, 4: Error, 5: Critical'
    parser.add_argument('--verbose', help=h, default=2, type=int)

    parser.add_argument('--version', help='Print version and exit', action='version', version=__version__)

    return parser.parse_args(args)


def cli():
    args = parse_args(sys.argv[1:])
    logger.setLevel(args.verbose * 10)
    if args.directory is None:
        filenames = [args.filename]
    else:
        filenames = glob.glob(os.path.join(args.directory, '*.png'))
    for f in filenames:
        main(f, outdir=args.outdir)


if __name__ == "__main__":
    cli()
