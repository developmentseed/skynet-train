# https://github.com/BVLC/caffe/issues/861
import matplotlib
matplotlib.use('Agg')

import os.path
import sys
from flask import Flask
from flask import request
from flask import send_file
from flask import jsonify
import requests
import numpy as np
from PIL import Image
import argparse
import json
import StringIO
caffe_root = os.getenv('CAFFE_ROOT', '/home/ubuntu/caffe-segnet/')
sys.path.insert(0, caffe_root + 'python')
import caffe

from inference import predict

app = Flask(__name__)

cpu_only_env = bool(os.getenv('CPU_ONLY', False))

# Import arguments
parser = argparse.ArgumentParser()
parser.add_argument('image_tiles', type=str)
parser.add_argument('--model', type=str, default='/model/segnet_deploy.prototxt')
parser.add_argument('--weights', type=str, default='/model/weights.caffemodel')
parser.add_argument('--classes', type=str, default='/model/classes.json')
parser.add_argument('--cpu-mode', action='store_true', default=cpu_only_env)
args = parser.parse_args()

# read classes metadata
with open(args.classes) as classes:
    colors = map(lambda x: x['color'][1:], json.load(classes))
    colors.append('000000')
    colors = map(lambda rgbstr: tuple(map(ord, rgbstr.decode('hex'))), colors)
num_classes = len(colors)

# read model definition
model = open(args.model, 'r').read()

# create net
if args.cpu_mode:
    caffe.set_mode_cpu()
else:
    caffe.set_mode_gpu()

net = caffe.Net(args.model,
                args.weights,
                caffe.TEST)


@app.route('/index.json')
def index():
    return jsonify(tilejson='2.0.0',
                   tiles=[request.url.replace('index.json', '{z}/{x}/{y}/tile.png')])


def send_prediction(im):
    bands = len(im.getbands())
    imdata = np.array(im.getdata()).reshape(im.size[0], im.size[1], bands)
    prediction = predict(net, colors, imdata)
    strio = StringIO.StringIO()
    prediction.save(strio, 'PNG')
    strio.seek(0)
    return send_file(strio, mimetype='image/png')


@app.route('/<int:z>/<int:x>/<int:y>/tile.png')
def tile(x, y, z):
    image_url = args.image_tiles.replace('{x}', str(x)).replace('{y}', str(y)).replace('{z}', str(z))
    resp = requests.get(image_url)
    return send_prediction(Image.open(StringIO.StringIO(resp.content)))


@app.route('/predict', methods=['POST'])
def pred():
    return send_prediction(Image.open(request.files['image']))


app.run(host='0.0.0.0')
