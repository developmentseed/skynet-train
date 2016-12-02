#!/usr/bin/env bash

# Dump data parsed from caffe logs to stdout

set -eu

SKYNET_TRAIN=${SKYNET_TRAIN:-"."}

MODEL=$1

FIRST=true
for log in $MODEL/train_*.log; do
  $SKYNET_TRAIN/util/parse_log.sh $log
  data="$(basename $log).train"

  # header
  if $FIRST; then head -n 1 $data; fi
  # data
  tail -n +2 $data
  rm $data
  rm ${data/train/test}
done

