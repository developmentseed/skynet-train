"""
This file contains code copied and modified from 'beachfront-py', which is
under the following license:

---

beachfront-py
https://github.com/venicegeo/beachfront-py
Copyright 2016, RadiantBlue Technologies, Inc.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
  http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import numpy
import potrace as _potrace
from PIL import Image
import click
import json


def lines_to_features(lines, source='imagery'):
    """ Create features from lines """
    gid = 0
    features = []
    for line in lines:
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [line]
            },
            'properties': {
                'id': gid,
                'source': source
            }
        }
        features.append(feature)
        gid += 1
    return features


def to_geojson(lines, source='imagery'):
    geojson = {
        'type': 'FeatureCollection',
        'features': lines_to_features(lines, source=source),
    }
    return geojson


def potrace_array(arr, turdsize=10.0, tolerance=0.2):
    """ Trace numpy array using potrace """
    bmp = _potrace.Bitmap(arr)
    polines = bmp.trace(turdsize=turdsize, turnpolicy=_potrace.TURNPOLICY_WHITE,
                        alphamax=0.0, opticurve=1.0, opttolerance=tolerance)
    lines = []
    for line in polines:
        lines.append(line.tesselate().tolist())

    return lines


def vectorize(img_file, turdsize=10.0, tolerance=0.2):
    img = Image.open(img_file)
    arr = numpy.asarray(img)
    arr = numpy.any(arr[:, :, :-1], axis=2)
    lines = potrace_array(arr, turdsize, tolerance)
    return to_geojson(lines)


@click.command()
@click.argument('img_file', default='-')
def vectorize_cmd(img_file):
    click.echo(json.dumps(vectorize(img_file)))


if __name__ == '__main__':
    vectorize_cmd()
