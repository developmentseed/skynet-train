#!/usr/bin/env bash

~/caffe-segnet/build/tools/caffe train -gpu ${3-0} -solver $1 2>&1 | tee $2
