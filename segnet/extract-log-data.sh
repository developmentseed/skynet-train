#!/usr/bin/env bash

# Dump data parsed from caffe logs to stdout

set -eu

SKYNET_TRAIN=${SKYNET_TRAIN:-"."}

MODEL=$1
NAME=${2:-$(basename $MODEL)}
TO_CSV="sed -re s/[[:blank:]]+/,/g"
PREPEND_NAME="sed s/^/$NAME,/"


FIRST=true
for log in $MODEL/train_*.log; do
  $SKYNET_TRAIN/util/parse_log.sh $log
  data="$(basename $log).train"

  # header
  if $FIRST; then head -n 1 $data | $TO_CSV | sed s/^/Model,/; fi
  # data
  tail -n +2 $data | $TO_CSV | $PREPEND_NAME

  rm $data
  rm "$(basename $log).test"
  FIRST=false
done

