# Experiments

Here are some of the training datasets and trained models that have come out of
our experiments. Trained weights (`.caffemodel` files) are available in the
[requester-pays](http://docs.aws.amazon.com/AmazonS3/latest/dev/RequesterPaysBuckets.html)
S3 bucket `skynet-models` -- see below for specific paths.

# Training Data

The license for the satellite/aerial imagery we used means that we cannot
redistribute the files ourselves, but the
[skynet-data](https://github.com/developmentseed/skynet-data) scripts should
hopefully make it easier for you to create your own. (If you want to reproduce
one of these exactly, see the `/data` directory in this repo for a list of
specific map tiles used for each training set.)

| Set | N | Resolution | Labels | Source | Location |
|-----|---|------------|--------|--------|----------|
| [training-set-7](https://github.com/developmentseed/skynet-train/blob/master/data/training-set-7/sample.geojson) | 3954 | z16 | road (stroke, 5px) | Mapbox Satellite | Northeastern USA and some of CAN |
| [training-set-8](https://github.com/developmentseed/skynet-train/blob/master/data/training-set-8/sample.geojson) | 24747 | z17 | water (fill)<br>building (fill)<br>road (stroke, 5px) | Mapbox Satellite | Continental USA |
| [training-set-9](https://github.com/developmentseed/skynet-train/blob/master/data/training-set-9/sample.geojson) | 6747 | z17 | road (stroke, 5px) | Mapbox Satellite | Seattle, USA |
| [training-set-10](https://github.com/developmentseed/skynet-train/blob/master/data/training-set-10/sample.geojson) | 6914 | z17 | water (fill)<br>building (fill)<br>road (stroke, 5px) | Mapbox Satellite | Seattle, USA |
| [training-set-11](https://github.com/developmentseed/skynet-train/blob/master/data/training-set-11/sample.geojson) | 6841 | z17 | building (fill)<br>road (stroke, 5px) | Mapbox Satellite | Seattle, WA, USA |
| [training-set-12](https://github.com/developmentseed/skynet-train/blob/master/data/training-set-12/sample.geojson) | 6450 | z17 | building (fill)<br>road (stroke, 5px) | Mapbox Satellite | Dar es Salaam, TZA |
| [spacenet-1](https://github.com/developmentseed/skynet-train/blob/master/data/spacenet-1) | 3075 | 50cm | building (fill) | [SpaceNet on AWS](https://aws.amazon.com/public-datasets/spacenet/) | Rio De Janeiro, BRA |


# Trained Models

A model with 'tsX' in the name corresponds to to 'training set X' above.


## segnet-ts7-1

Trained caffemodel files: s3://skynet-models/segnet-ts7-1/manifest.txt



|Iterations|Correctness|Completeness|View Results|
|----------|-----------|------------|------------|
|5000|0.3256573519036912|0.7868625456307186|[view results](https://skynet-results.s3.amazonaws.com/view.html?baseurl=segnet-ts7-1/test_5000/)|


## segnet-ts7-2

Trained caffemodel files: s3://skynet-models/segnet-ts7-2/manifest.txt



|Iterations|Correctness|Completeness|View Results|
|----------|-----------|------------|------------|
|60000|0.5058499453227574|0.6716329348245725|[view results](https://skynet-results.s3.amazonaws.com/view.html?baseurl=segnet-ts7-2/test_60000/)|


## segnet-ts9-1

Trained caffemodel files: s3://skynet-models/segnet-ts9-1/manifest.txt


[Compare results](https://skynet-results.s3.amazonaws.com/view.html?baseurl=segnet-ts9-1/test_init-vgg_5000&baseurl=segnet-ts9-1/test_init-vgg_55000)

|Iterations|Correctness|Completeness|View Results|
|----------|-----------|------------|------------|
|5000|0.518253184652922|0.8573735411419057|[view results](https://skynet-results.s3.amazonaws.com/view.html?baseurl=segnet-ts9-1/test_init-vgg_5000/)|
|55000|0.7707086613419863|0.7196262477292044|[view results](https://skynet-results.s3.amazonaws.com/view.html?baseurl=segnet-ts9-1/test_init-vgg_55000/)|


## segnet-ts10-1

Trained caffemodel files: s3://skynet-models/segnet-ts10-1/manifest.txt


[Compare results](https://skynet-results.s3.amazonaws.com/view.html?baseurl=segnet-ts10-1/test_20K&baseurl=segnet-ts10-1/test_40K)

|Iterations|Correctness|Completeness|View Results|
|----------|-----------|------------|------------|
|20K|0.427194953622606|0.46094955169178686|[view results](https://skynet-results.s3.amazonaws.com/view.html?baseurl=segnet-ts10-1/test_20K/)|
|40K|0.5728470881115866|0.638696209213571|[view results](https://skynet-results.s3.amazonaws.com/view.html?baseurl=segnet-ts10-1/test_40K/)|


## segnet-ts11-1

Trained caffemodel files: s3://skynet-models/segnet-ts11-1/manifest.txt


[Compare results](https://skynet-results.s3.amazonaws.com/view.html?baseurl=segnet-ts11-1/test_10K&baseurl=segnet-ts11-1/test_30K)

|Iterations|Correctness|Completeness|View Results|
|----------|-----------|------------|------------|
|10K|0.6246305164870534|0.6131471814748839|[view results](https://skynet-results.s3.amazonaws.com/view.html?baseurl=segnet-ts11-1/test_10K/)|
|30K|0.7283672440907986|0.45904370319881704|[view results](https://skynet-results.s3.amazonaws.com/view.html?baseurl=segnet-ts11-1/test_30K/)|


## segnet-ts12-1

Trained caffemodel files: s3://skynet-models/segnet-ts12-1/manifest.txt


[Compare results](https://skynet-results.s3.amazonaws.com/view.html?baseurl=segnet-ts12-1/test_15K&baseurl=segnet-ts12-1/test_25K&baseurl=segnet-ts12-1/test_40K)

|Iterations|Correctness|Completeness|View Results|
|----------|-----------|------------|------------|
|15K|0.6706866344254577|0.8394262122454237|[view results](https://skynet-results.s3.amazonaws.com/view.html?baseurl=segnet-ts12-1/test_15K/)|
|25K|0.6006667123465258|0.8542909458638581|[view results](https://skynet-results.s3.amazonaws.com/view.html?baseurl=segnet-ts12-1/test_25K/)|
|40K|0.6372450268591862|0.8168847046209704|[view results](https://skynet-results.s3.amazonaws.com/view.html?baseurl=segnet-ts12-1/test_40K/)|


## spacenet-1.0

Trained caffemodel files: s3://skynet-models/spacenet-1.0/manifest.txt


[Compare results](https://skynet-results.s3.amazonaws.com/view.html?baseurl=spacenet-1.0/snapshots/segnet_iter_5000.results&baseurl=spacenet-1.0/snapshots/segnet_iter_10000.results&baseurl=spacenet-1.0/snapshots/segnet_iter_15000.results&baseurl=spacenet-1.0/snapshots/segnet_iter_20000.results&baseurl=spacenet-1.0/snapshots/segnet_iter_25000.results)

|Iterations|Correctness|Completeness|View Results|
|----------|-----------|------------|------------|
|5000|0.7884645371187057|0.9409724819069966|[view results](https://skynet-results.s3.amazonaws.com/view.html?baseurl=spacenet-1.0/snapshots/segnet_iter_5000.results/)|
|10000|0.7882820153922176|0.9430313923848284|[view results](https://skynet-results.s3.amazonaws.com/view.html?baseurl=spacenet-1.0/snapshots/segnet_iter_10000.results/)|
|15000|0.7902352382903021|0.9457690149692252|[view results](https://skynet-results.s3.amazonaws.com/view.html?baseurl=spacenet-1.0/snapshots/segnet_iter_15000.results/)|
|20000|0.7918245263758488|0.9426878128090946|[view results](https://skynet-results.s3.amazonaws.com/view.html?baseurl=spacenet-1.0/snapshots/segnet_iter_20000.results/)|
|25000|0.7923963798908541|0.9405211082529236|[view results](https://skynet-results.s3.amazonaws.com/view.html?baseurl=spacenet-1.0/snapshots/segnet_iter_25000.results/)|

