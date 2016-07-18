import os.path
import sys
from flask import Flask
from flask import request
from flask import send_file
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

# Import arguments
parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, required=True)
parser.add_argument('--weights', type=str, required=True)
parser.add_argument('--classes', type=str, required=True)
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
caffe.set_mode_cpu()
net = caffe.Net(args.model,
                args.weights,
                caffe.TEST)


@app.route('/')
def main():
    return ''


@app.route('/predict', methods=['POST'])
def pred():
    im = Image.open(request.files['image'])
    bands = len(im.getbands())
    imdata = np.array(im.getdata()).reshape(im.size[0], im.size[1], bands)
    prediction = predict(net, colors, imdata)
    strio = StringIO.StringIO()
    prediction.save(strio, 'PNG')
    strio.seek(0)
    return send_file(strio, mimetype='image/png')


app.run()
