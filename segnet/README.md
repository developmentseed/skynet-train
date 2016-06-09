
# Testing the Trained Network

(Adapted from http://mi.eng.cam.ac.uk/projects/segnet/tutorial.html)
## Batch Normalization

The Batch Normalisation layers [3] in SegNet shift the input feature maps
according to their mean and variance statistics for each mini batch during
training. At test time we must use the statistics for the entire dataset. To do
this run the script Scripts/compute_bn_statistics.py using the following
commands. Make sure you change the training weight file to the one which you
wish to use.

```sh
python compute_bn_statistics.py train.prototxt weights.caffemodel /path/to/weights/output
```

The script saves the final test weights in the output directory as test_weights.caffemodel

## Test Outputs
`test_segmentation_camvid.py` will display the input image, ground truth and
segmentation prediction for each test image, prefixing the filenames as
specified in the arguments.

```sh
python test_segmentation_camvid.py --model inference.prototxt --weights /path/to/weights/output/test_weights.caffemodel --iter XXX --output /path/to/results/output/image_prefix_
```
