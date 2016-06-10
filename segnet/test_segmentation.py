# https://github.com/BVLC/caffe/issues/861
import matplotlib
matplotlib.use('Agg')

import numpy as np
import matplotlib.pyplot as plt
import os.path
import re
import json
import scipy
import argparse
import math
import pylab
from sklearn.preprocessing import normalize
caffe_root = os.getenv('CAFFE_ROOT', '/home/ubuntu/caffe-segnet/')
import sys
sys.path.insert(0, caffe_root + 'python')

import caffe

# Import arguments
parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, required=True)
parser.add_argument('--weights', type=str, required=True)
parser.add_argument('--output', type=str, required=True)
parser.add_argument('--classes', type=str, required=True)
args = parser.parse_args()

with open(args.classes) as classes:
	colors = map(lambda x : x['color'][1:], json.load(classes))
	colors.append('000000')
	colors = map(lambda rgbstr : tuple(map(ord, rgbstr.decode('hex'))), colors)

model = open(args.model, 'r').read()
m = re.search('source:\s*"(.*)"', model)
test_data = m.group(1)
test_data = open(test_data, 'r').readlines()

caffe.set_mode_gpu()

net = caffe.Net(args.model,
                args.weights,
                caffe.TEST)


outputs = []

for i in range(0, len(test_data)):

	net.forward()

	image = net.blobs['data'].data
	label = net.blobs['label'].data
	predicted = net.blobs['prob'].data
	image = np.squeeze(image[0,:,:,:])
	output = np.squeeze(predicted[0,:,:,:])
	ind = np.argmax(output, axis=0)

	r = ind.copy()
	g = ind.copy()
	b = ind.copy()
	r_gt = label.copy()
	g_gt = label.copy()
	b_gt = label.copy()

	label_colours = np.array(colors)
	for l in range(0,len(colors)):
		r[ind==l] = label_colours[l,0]
		g[ind==l] = label_colours[l,1]
		b[ind==l] = label_colours[l,2]
		r_gt[label==l] = label_colours[l,0]
		g_gt[label==l] = label_colours[l,1]
		b_gt[label==l] = label_colours[l,2]

	rgb = np.zeros((ind.shape[0], ind.shape[1], 3))
	rgb[:,:,0] = r
	rgb[:,:,1] = g
	rgb[:,:,2] = b
	rgb_gt = np.zeros((ind.shape[0], ind.shape[1], 3))
	rgb_gt[:,:,0] = r_gt
	rgb_gt[:,:,1] = g_gt
	rgb_gt[:,:,2] = b_gt

	image = np.transpose(image, (1,2,0))
	output = np.transpose(output, (1,2,0))
	image = image[:,:,(2,1,0)]

	prediction = str(i) + '_prediction.png'
	input_image = str(i) + '_input.png'
	groundtruth = str(i) + '_groundtruth.png'
	scipy.misc.toimage(rgb, cmin=0.0, cmax=255).save(os.path.join(args.output, prediction))
	scipy.misc.toimage(image, cmin=0.0, cmax=255).save(os.path.join(args.output, input_image))
	scipy.misc.toimage(rgb_gt, cmin=0.0, cmax=255).save(os.path.join(args.output, groundtruth))
	outputs.append({
		'index': i,
		'input': input_image,
		'prediction': prediction,
		'groundtruth': groundtruth,
		'test_data': test_data[i]
	})

with open(os.path.join(args.output, 'index.json'), 'w') as outfile:
	json.dump(outputs, outfile)

print 'Success!'

