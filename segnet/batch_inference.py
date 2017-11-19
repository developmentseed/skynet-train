# https://github.com/BVLC/caffe/issues/861
import matplotlib
matplotlib.use('Agg')

import re
import os
import os.path
import sys
import time
import random
import requests
import numpy as np
from PIL import Image
import click
import json
import StringIO
import subprocess
import tempfile
from boto3.session import Session
caffe_root = os.getenv('CAFFE_ROOT', '/home/ubuntu/caffe-segnet/')
sys.path.insert(0, caffe_root + 'python')
import caffe

from inference import predict
from queue import receive
from vectorize import vectorize

aws_session = Session()
s3 = aws_session.client('s3')
dirname = os.path.dirname(os.path.realpath(__file__))
polys_to_lines = os.path.join(dirname, '../vectorize.js')


class TileNotFoundError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


def parse_s3_uri(s3uri):
    match = re.search('s3://([^/]*)/(.*)$', s3uri)
    if not match:
        return None
    return (match.group(1), match.group(2))


def resolve_s3(s3uri):
    parsed = parse_s3_uri(s3uri)
    if not parsed:
        return s3uri
    (bucket, key) = parsed
    target = '/model/' + os.path.basename(key)
    if not os.path.isfile(target):
        print('downloading ' + s3uri + ' to ' + target)
        s3.download_file(bucket, key, target)
    else:
        print(s3uri + ' appears to have already been downloaded to ' + target +
              '; using local copy.')
    return target


def setup_net(model, weights, gpu, cpu_only):
    model_file = resolve_s3(model)
    weights_file = resolve_s3(weights)
    if not os.path.isfile(weights_file) and os.path.isdir('/model'):
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


def make_prediction(net, colors, im, outfile):
    bands = len(im.getbands())
    imdata = np.array(im.getdata()).reshape(im.size[0], im.size[1], bands)
    predicted = predict(net, colors, imdata)
    predicted.save(outfile, 'PNG')


def get_image_tile(url, x, y, z):
    image_url = url.replace('{x}', str(x)).replace('{y}', str(y)).replace('{z}', str(z))
    resp = requests.get(image_url)
    if not resp.ok:
        raise TileNotFoundError({'status': resp.status_code, 'content': resp.content})
    return Image.open(StringIO.StringIO(resp.content)).convert('RGB')


def upload_centerlines(filename, output_bucket, prefix):
    uid = ''.join(random.choice('abcdef0123456789') for _ in range(6))
    key = '%s/centerlines.%s-%s.geojson' % (prefix, time.time(), uid)
    click.echo('Uploading geojson %s' % key)
    s3.upload_file(filename, output_bucket, key, ExtraArgs={
        'ContentType': 'application/ndjson'
    })


@click.command()
@click.argument('queue_name')
@click.option('--model', type=str, default='/model/segnet_deploy.prototxt')
@click.option('--weights', type=str, default='/model/weights.caffemodel')
@click.option('--classes', type=str, default='/model/classes.json')
@click.option('--gpu', type=int, default=0)
@click.option('--cpu-only', is_flag=True, default=False)
def run_batch(queue_name, model, weights, classes, gpu, cpu_only):
    net = setup_net(model, weights, gpu, cpu_only)
    classes_file = resolve_s3(classes)

    # read classes metadata
    with open(classes_file) as classes:
        colors = map(lambda x: x['color'][1:], json.load(classes))
        colors.append('000000')
        colors = map(lambda rgbstr: tuple(map(ord, rgbstr.decode('hex'))), colors)

    count = 0
    centerlines = tempfile.NamedTemporaryFile(suffix='.geojson', delete=False)
    click.echo('geojson output: %s' % centerlines.name)

    for message in receive(queue_name):
        try:
            click.echo('processing: %s' % message.body)
            (output_bucket, prefix, image_tiles, z, x, y) = json.loads(message.body)

            image = get_image_tile(image_tiles, x, y, z)

            # run prediction
            predicted = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            make_prediction(net, colors, image, predicted)
            predicted.close()

            # upload raster prediction image
            key = '%s/%s/%s/%s.png' % (prefix, z, x, y)
            s3.upload_file(predicted.name, output_bucket, key, ExtraArgs={
                'ContentType': 'image/png'
            })

            # trace raster -> polygons
            polygonized = tempfile.NamedTemporaryFile(suffix='.geojson', delete=False)
            polygonized.write(json.dumps(vectorize(predicted.name)))
            polygonized.close()

            # upload polygon geojson for this tile
            key = '%s/%s/%s/%s.polygons.geojson' % (prefix, z, x, y)
            s3.upload_file(polygonized.name, output_bucket, key, ExtraArgs={
                'ContentType': 'application/json'
            })

            # polygons => centerlines
            polyspine_args = map(str, [polys_to_lines, polygonized.name, x, y, z, 0.2])
            exitcode = subprocess.call(polyspine_args, stdout=centerlines)

            # clean up tempfiles
            os.remove(predicted.name)
            os.remove(polygonized.name)

            if exitcode != 0:
                raise Exception('Vectorize exited nonzero')

            # upload centerlines geojson to S3 every so often
            count += 1
            if count % 5000 == 0:
                centerlines.close()
                upload_centerlines(centerlines.name, output_bucket, prefix)
                # clear the file out and continue writing
                centerlines = open(centerlines.name, 'w+b')

            # remove message from the queue
            message.delete()
        except TileNotFoundError:
            click.echo('Imagery tile not found.')
            message.delete()
        except Exception as err:
            click.echo(err)
            try:
                message.delete()
            except Exception:
                pass

    centerlines.close()
    upload_centerlines(centerlines.name, output_bucket, prefix)


if __name__ == '__main__':
    run_batch(auto_envvar_prefix='SKYNET')
