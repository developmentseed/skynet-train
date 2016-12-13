# https://github.com/BVLC/caffe/issues/861
import matplotlib
matplotlib.use('Agg')

import re
import os
import os.path
import sys
import requests
import numpy as np
from PIL import Image
import click
import json
import StringIO
import tempfile
from boto3.session import Session
caffe_root = os.getenv('CAFFE_ROOT', '/home/ubuntu/caffe-segnet/')
sys.path.insert(0, caffe_root + 'python')
import caffe

from inference import predict
from queue import receive

aws_session = Session()
s3 = aws_session.client('s3')


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


def setup_net(model, weights, cpu_only):
    model_file = resolve_s3(model)
    weights_file = resolve_s3(weights)
    if not os.path.isfile(model) and os.path.isdir('/model'):
        caffemodels = filter(lambda x: x.endswith('.caffemodel'), os.listdir('/model'))
        if len(caffemodels) == 0:
            raise 'No .caffemodel files found in /model.'
        model_file = caffemodels[0]

    # read model definition
    model = open(model_file, 'r').read()
    # create net
    if cpu_only:
        caffe.set_mode_cpu()
    else:
        caffe.set_mode_gpu()

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
    return Image.open(StringIO.StringIO(resp.content))


@click.command()
@click.argument('queue_name')
@click.option('--image-tiles', type=str)
@click.option('--model', type=str, default='/model/segnet_deploy.prototxt')
@click.option('--weights', type=str, default='/model/weights.caffemodel')
@click.option('--classes', type=str, default='/model/classes.json')
@click.option('--cpu-only', is_flag=True, default=False)
def run_batch(queue_name, image_tiles, model, weights, classes, cpu_only):
    net = setup_net(model, weights, cpu_only)
    classes_file = resolve_s3(classes)
    # read classes metadata
    with open(classes_file) as classes:
        colors = map(lambda x: x['color'][1:], json.load(classes))
        colors.append('000000')
        colors = map(lambda rgbstr: tuple(map(ord, rgbstr.decode('hex'))), colors)

    for message in receive(queue_name):
        click.echo('processing: %s' % message.body)
        (output_bucket, prefix, z, x, y) = json.loads(message.body)

        image = get_image_tile(image_tiles, x, y, z)

        with tempfile.NamedTemporaryFile(suffix='.png') as predicted:
            # run the net and upload result
            make_prediction(net, colors, image, predicted)
            key = '%s/%s/%s/%s.png' % (prefix, z, x, y)
            s3.upload_fileobj(predicted, output_bucket, key, ExtraArgs={
                'ContentType': 'image/png'
            })
        # remove message from the queue
        message.delete()


if __name__ == '__main__':
    run_batch(auto_envvar_prefix='SKYNET')
