#!/usr/bin/env python

# https://github.com/BVLC/caffe/issues/861
import matplotlib
matplotlib.use('Agg')

import argparse
import inspect
import os
import random
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.markers as mks


def get_log_parsing_script():
    currentpath = os.path.abspath(inspect.getfile(inspect.currentframe()))
    dirname = os.path.dirname(currentpath)
    return dirname + '/parse_log.sh'


def get_log_file_suffix():
    return '.log'


def get_chart_type_description_separator():
    return ' vs. '


def is_x_axis_field(field):
    x_axis_fields = ['Iters', 'Seconds']
    return field in x_axis_fields


def is_y_axis_field(field):
    x_axis_only_fields = ['Seconds']
    return not (field in x_axis_only_fields)


def create_field_index():
    train_key = 'Train'
    test_key = 'Test'
    field_index = {train_key: {'Iters': 0, 'Seconds': 1,
                               train_key + ' loss': 2,
                               train_key + ' learning rate': 3},
                   test_key: {'Iters': 0, 'Seconds': 1,
                              test_key + ' accuracy': 2,
                              test_key + ' loss': 3}}
    fields = set()
    for data_file_type in field_index.keys():
        fields = fields.union(set(field_index[data_file_type].keys()))
    fields = list(fields)
    fields.sort()
    return field_index, fields


def get_supported_chart_types():
    field_index, fields = create_field_index()
    num_fields = len(fields)
    supported_chart_types = []
    for i in xrange(num_fields):
        if is_y_axis_field(fields[i]):
            for j in xrange(num_fields):
                if i != j and is_x_axis_field(fields[j]):
                    supported_chart_types.append('%s%s%s' % (
                        fields[i], get_chart_type_description_separator(),
                        fields[j]))
    return supported_chart_types


def get_chart_type_description(chart_type):
    supported_chart_types = get_supported_chart_types()
    chart_type_description = supported_chart_types[chart_type]
    return chart_type_description


def get_data_file_type(chart_type):
    if chart_type == 0:
        return 'Train'
    description = get_chart_type_description(chart_type)
    data_file_type = description.split()[0]
    return data_file_type


def get_data_file(chart_type, path_to_log):
    return os.path.basename(path_to_log) + '.' + \
        get_data_file_type(chart_type).lower()


def get_field_descriptions(chart_type):
    description = get_chart_type_description(chart_type).split(
        get_chart_type_description_separator())
    y_axis_field = description[0]
    x_axis_field = description[1]
    return x_axis_field, y_axis_field


def get_field_indecies(x_axis_field, y_axis_field):
    data_file_type = get_data_file_type(chart_type)
    fields = create_field_index()[0][data_file_type]
    return fields[x_axis_field], fields[y_axis_field]


def load_data(data_file, field_idx0, field_idx1):
    data = [[], []]
    with open(data_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line[0] != '#':
                fields = line.split()
                data[0].append(float(fields[field_idx0].strip()))
                data[1].append(float(fields[field_idx1].strip()))
    return data


def random_marker():
    markers = mks.MarkerStyle.markers
    num = len(markers.values())
    idx = random.randint(0, num - 1)
    return markers.values()[idx]


def get_data_label(path_to_log):
    label = path_to_log[path_to_log.rfind('/') + 1: path_to_log.rfind(
        get_log_file_suffix())]
    return label


def get_legend_loc(chart_type):
    x_axis, y_axis = get_field_descriptions(chart_type)
    loc = 'lower right'
    if y_axis.find('accuracy') != -1:
        pass
    if y_axis.find('loss') != -1 or y_axis.find('learning rate') != -1:
        loc = 'upper right'
    return loc


def runningMeanFast(x, N):
    return np.convolve(np.array(x), np.ones((N,)) / N, 'valid')


def plot_chart(chart_type, path_to_png, path_to_log, smooth):
    os.system('%s %s' % (get_log_parsing_script(), path_to_log))
    data_file = get_data_file(chart_type, path_to_log)
    x_axis_field, y_axis_field = get_field_descriptions(chart_type)
    x, y = get_field_indecies(x_axis_field, y_axis_field)
    data = load_data(data_file, x, y)

    # TODO: more systematic color cycle for lines
    color = [random.random(), random.random(), random.random()]
    label = get_data_label(path_to_log)
    linewidth = 0.75
    # If there too many datapoints, do not use marker.
    # use_marker = False
    if smooth and smooth > 0 and len(data[0]) > smooth:
        data[1] = runningMeanFast(data[1], smooth)
        data[0] = data[0][:len(data[1])]

    plt.plot(data[0], data[1], label=label, color=color,
             linewidth=linewidth)
    os.remove(get_data_file(0, path_to_log))  # remove xxx.log.test file
    os.remove(get_data_file(4, path_to_log))  # remove xxx.log.train file


def plot_charts(chart_type, path_to_png, path_to_log_list, smooth):
    plt.clf()
    x_axis_field, y_axis_field = get_field_descriptions(chart_type)
    legend_loc = get_legend_loc(chart_type)
    for path_to_log in path_to_log_list:
        plot_chart(chart_type, path_to_png, path_to_log, smooth)
    plt.legend(loc=legend_loc, ncol=1)  # adjust ncol to fit the space
    plt.title(get_chart_type_description(chart_type))
    plt.xlabel(x_axis_field)
    plt.ylabel(y_axis_field)
    plt.savefig(path_to_png)
    plt.show()


def print_help():
    print """
Usage:
    ./plot_log.sh chart_type[0-%s] /path/to/output.png /path/to/train.log
      [/path/to/train2.log path/to/train3.log ...]
Notes:
    Log file name must end with the lower-cased "%s".
Supported chart types:""" % (len(get_supported_chart_types()) - 1,
                             get_log_file_suffix())
    supported_chart_types = get_supported_chart_types()
    num = len(supported_chart_types)
    for i in xrange(num):
        print '    %d: %s' % (i, supported_chart_types[i])
    exit()


def is_valid_chart_type(chart_type):
    return chart_type >= 0 and chart_type < len(get_supported_chart_types())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('inputs', metavar='FILE.log', type=str, nargs='+')
    parser.add_argument('--output', type=str)
    parser.add_argument('--type', type=int, default=7)
    parser.add_argument('--smooth', type=int, default=50)
    parser.add_argument('--watch', type=bool, default=False)
    args = parser.parse_args()
    chart_type = args.type
    if not is_valid_chart_type(chart_type):
        print_help()

    if args.output:
        path_to_png = args.output
    else:
        path_to_png = get_chart_type_description(chart_type)
        path_to_png = path_to_png.replace(' ', '-').replace('.', '').lower()
        path_to_png = path_to_png + '.png'

    path_to_log_list = args.inputs
    for path_to_log in path_to_log_list:
        if not os.path.exists(path_to_log):
            print 'Path does not exist: %s' % path_to_log
            exit()
        if not path_to_log.endswith(get_log_file_suffix()):
            print_help()
    delay = 60
    while True:
        print('%s updating chart' %
              time.strftime('%Y-%m-%d %H:%M', time.gmtime()))
        plot_charts(chart_type, path_to_png, path_to_log_list, args.smooth)
        if not args.watch:
            break
        time.sleep(delay)
