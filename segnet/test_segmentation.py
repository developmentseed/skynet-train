# https://github.com/BVLC/caffe/issues/861
import matplotlib
matplotlib.use('Agg')

import numpy as np
import os.path
import re
import json
import scipy
import argparse
caffe_root = os.getenv('CAFFE_ROOT', '/home/ubuntu/caffe-segnet/')
import sys
sys.path.insert(0, caffe_root + 'python')

import caffe

from metrics import complete_and_correct
from inference import predict
from inference import labels_to_image


# Import arguments
parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, required=True)
parser.add_argument('--weights', type=str, required=True)
parser.add_argument('--output', type=str, required=True)
parser.add_argument('--classes', type=str, required=True)
parser.add_argument('--metrics-only', default=False, action='store_true')
parser.add_argument('--gpu', type=int)
args = parser.parse_args()

with open(args.classes) as classes:
    colors = map(lambda x: x['color'][1:], json.load(classes))
    colors.append('000000')
    colors = map(lambda rgbstr: tuple(map(ord, rgbstr.decode('hex'))), colors)

num_classes = len(colors)

model = open(args.model, 'r').read()
m = re.search('source:\s*"(.*)"', model)
test_data = m.group(1)
test_data = open(test_data, 'r').readlines()

caffe.set_mode_gpu()
if args.gpu is not None:
    caffe.set_device(args.gpu)

net = caffe.Net(args.model,
                args.weights,
                caffe.TEST)

pixels_correct = 0
pixels_complete = 0
pixels_predicted_fg = 0
pixels_actual_fg = 0
outputs = []

for i in range(0, len(test_data)):
    prediction_image = predict(net, colors)

    image = net.blobs['data'].data
    image = np.squeeze(image[0, :, :, :])
    label = net.blobs['label'].data
    label = np.squeeze(label)
    predicted = net.blobs['prob'].data
    predicted = np.squeeze(predicted[0, :, :, :])

    metrics = complete_and_correct(predicted, label, 3, 0.5)

    result = {'index': i, 'metrics': metrics}
    print(result)
    outputs.append(result)
    pixels_correct += sum(metrics['pixels_correct'])
    pixels_complete += sum(metrics['pixels_complete'])
    pixels_predicted_fg += sum(metrics['pixels_predicted'][:-1])
    pixels_actual_fg += sum(metrics['pixels_actual'][:-1])
    if args.metrics_only:
        continue

    image = np.transpose(image, (1, 2, 0))
    image = image[:, :, (2, 1, 0)]

    prediction = str(i) + '_prediction.png'
    input_image = str(i) + '_input.png'
    groundtruth = str(i) + '_groundtruth.png'

    prediction_image.save(os.path.join(args.output, prediction))
    labels_to_image(label, colors).save(os.path.join(args.output, groundtruth))
    scipy.misc.toimage(image, cmin=0.0, cmax=255).save(
        os.path.join(args.output, input_image))

    result['input'] = input_image
    result['prediction'] = prediction
    result['groundtruth'] = groundtruth
    result['test_data'] = test_data[i]

with open(os.path.join(args.output, 'index.json'), 'w') as outfile:
    json.dump({
        'correctness': pixels_correct / pixels_predicted_fg,
        'completeness': pixels_complete / pixels_actual_fg,
        'images': outputs
    }, outfile)

print 'Success!'
