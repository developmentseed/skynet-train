#!/bin/sh

monitor/dump-logs.sh &

cd monitor

python -m SimpleHTTPServer 8080
