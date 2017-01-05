#!/bin/bash
while :
do
    segnet/extract-log-data.sh /output > monitor/training.csv
    echo "Updated data from logs: $(cat monitor/training.csv | wc -l) observations"
    sleep 60
done
