import numpy as np
import skimage.io as io
import tensorflow as tf
import os, sys

CODE_2_MEANING = 'Code 2: invalid arguements'
CODE_1_MEANING = 'Code 1: Absent Data'
tfrecords_filename = 'skynet.tfrecords'



def main(args=None):
    """
    :param args: List of arguments
    :arg -d file path to the data output directory of skynet-data, required. The skynet.tfrecords file will also be put in this directory.
    :returns: Nothing
    side effects: writes file tfrecords file <dataDir>/skynet.tfrecords containing training data
    """
    dataDir = ""
    process = False
    if args == None:
        args = sys.argv
    if isinstance(args, str):
        args = args.split(' ')
    if len(args) == 1 or args[1] == '--help':
        print("Usage:")
        print("python read_skynet_data.py -d path/to/skynet-data/output [-f]")
        sys.exit(0)
    i = 1
    print args
    while i < len(args):
        arg = args[i]
        if arg == '-p':
            process = True
        elif arg == '-d':
            i += 1
            arg = args[i]
            dataDir = arg
        else:
            print('Unrecognized flag ' + arg)
            print(CODE_2_MEANING)
            sys.exit(2)
        i += 1
    if dataDir == "":
        print('You must provide the location of the training data with the -d arg')
        print(CODE_2_MEANING)
        sys.exit(2)
    if not os.path.isdir(dataDir):
        print('The data directory you supplied with the -d arg does not exist or is not a directory')
        print(CODE_2_MEANING)
        sys.exit(2)
    writer = tf.python_io.TFRecordWriter(tfrecords_filename)

    train = open(dataDir + '/train.txt', 'r')
    trainLabels = []
    trainImages = []
    for line in train:
        line = line.split(' ')
        imagePath = line[0]
        labelPath = line[1]
        #remove the /data, which is redundant to dataDir
        imagePath = dataDir + imagePath[5:]
        #also remove the newling
        labelPath = dataDir + labelPath[5:-1]

        image = io.imread(imagePath, as_grey=True)
        image = np.array(image)
        height = image.shape[0]
        width = image.shape[1]

        labelAr = io.imread(labelPath, as_grey=True)
        labelAr = np.array(labelAr)
        #so the really weird thing is that the data values are zero and the nodata values are nonzero?
        #hence the following line
        label = width*height - np.count_nonzero(labelAr)



main("read_skynet_data.py -d /Users/devmcdevlin/skynet-data/data")

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt):
        exit('Received Ctrl + C... Exiting', 1)