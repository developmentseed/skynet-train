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


# Import arguments
parser = argparse.ArgumentParser()
parser.add_argument('image', type=str)
parser.add_argument('--model', type=str, required=True)
parser.add_argument('--weights', type=str, required=True)
parser.add_argument('--classes', type=str, required=True)
parser.add_argument('--output', type=str, required=True)
args = parser.parse_args()

with open(args.classes) as classes:
    colors = map(lambda x: x['color'][1:], json.load(classes))
    colors.append('000000')
    colors = map(lambda rgbstr: tuple(map(ord, rgbstr.decode('hex'))), colors)

num_classes = len(colors)

model = open(args.model, 'r').read()
m = re.search('source:\s*"(.*)"', model)

caffe.set_mode_gpu()

net = caffe.Net(args.model,
                args.weights,
                caffe.TEST)

outputs = []

image = caffe.io.load_image(args.image)
image = image.transpose((2, 0, 1))
net.blobs['data'].data[0] = image
net.forward()

predicted = net.blobs['prob'].data
output = np.squeeze(predicted[0, :, :, :])

# only use the max-probability non-background class if its probability is
# above some threshold
ind = np.argmax(output, axis=0)
fg = output[:-1, :, :]  # foreground classes only
bg = np.full(ind.shape, num_classes - 1)
ind = np.where(np.max(fg, axis=0) > 0.5, ind, bg)

r = ind.copy()
g = ind.copy()
b = ind.copy()
a = np.zeros(ind.shape)

label_colours = np.array(colors)
for l in range(0, len(colors)):
    r[ind == l] = label_colours[l, 0]
    g[ind == l] = label_colours[l, 1]
    b[ind == l] = label_colours[l, 2]

max_prob = np.max(output, axis=0)
a[ind != num_classes - 1] = max_prob[ind != num_classes - 1] * 255

rgb = np.zeros((ind.shape[0], ind.shape[1], 4))
rgb[:, :, 0] = r
rgb[:, :, 1] = g
rgb[:, :, 2] = b
rgb[:, :, 3] = a

output = np.transpose(output, (1, 2, 0))

scipy.misc.toimage(rgb, cmin=0.0, cmax=255, mode='RGBA').save(args.output)

print 'Success!'
