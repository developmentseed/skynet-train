import os, sys
import re

def convert_to_voc2012(manifest, outfile):
    with open(manifest) as f:
        content = f.readlines()
    content = [re.search('(\d+)([-])(\d+)([-])(\d+)', row).group() for row in content]
    with open(outfile, 'w') as f:
        for item in content:
            print>>f, item


convert_to_voc2012('~/.keras/datasets/dg-goma-2/train.txt', '~/.keras/datasets/dg-goma-2/train-voc.txt')
convert_to_voc2012('~/.keras/datasets/dg-goma-2/val.txt', '~/.keras/datasets/dg-goma-2/val-voc.txt')