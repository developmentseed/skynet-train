# Vectorization playground

This code consists of a library of Python functions and a command line tool for creating GeoJSON (Lat/Lon) linestring coordinates of object skeletons from binary raster imagery. A binary raster image is one that consists of two values (0 or 255). The vectorization process will first generate the skeleton of the objects within the image, and then convert that into coordinates.

## Input data

The command line program vectorize.py currently operates on tiles in PNG format, and expects files to be named in the format: `{zoom}-{x}-{y}.png`. vectorize.py can take in either a single filename or directory name containing a series of png files. Only the first band is used for vectorization.

The PNG files can be generated using the tilestitching script in this repo. For zoom level 14:

```
mkdir zoom14
node ../tilestitching/index.js --dir images --zoom 14
cp -a ../tilestitching/out/*.png zoom14/
```


## Installation

To use the vectorize.py Python script some systen dependencies are required that may need to be installed. install the requirements using pip.

```
# on debian
$ sudo apt-get install libgdal-dev swig

# on mac
# brew install gdal swig

# then, on all systems
$ pip install numpy
$ pip install -r requirements.txt
```

Note that NumPy needs to be installed prior to the packages in the requirements.txt.


## Usage

There are currently no tunable parameters in the vectorization, input files are all that's needed. However there are some options:

```
$ ./vectorize.py -h
usage: vectorize.py [-h] (-f FILENAME | -d DIRECTORY) [--outdir OUTDIR]
                    [--verbose VERBOSE] [--version]

Binary image vectorization (v0.1.0)

optional arguments:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        Input PNG tile (default: None)
  -d DIRECTORY, --directory DIRECTORY
                        Input directory (default: None)
  --outdir OUTDIR       Save intermediate files to this dir (otherwise temp)
                        (default: )
  --verbose VERBOSE     0: Quiet, 1: Debug, 2: Info, 3: Warn, 4: Error, 5:
                        Critical (default: 2)
  --version             Print version and exit

```

e.g., run on directory of zoom 14

	$ vectorize.py -d zoom14 --outdir zoom14

Which will put all the outputs next to the input files in the zoom14 directory.


## Output

Two output files are saved for each input file, either in the current directory or in *outdir* if provided. The main output is the GeoJSON file of the same name as the input file but with a .geojson extension. This contains all of the vectorized linestrings, in an EPSG:4326 CRS. The other file is an intermediate GeoTIFF file (same basename with .tif extension) will be saved, containing the proper projection information and with 3 bands:

- Band 1 is the original binary image converted into 0 and 1. 
- Band 2 is the skeletonized image, where the value indicates the number of neighboring non-zero values. For instance, a road endpoint will have one neighbor and thus has a value of 2. A road midpoint has 2 neighbors and has a value of 3. Intersections have values of 4 or more. The numbers are used by the vectorization algorithm.
- Band 3 contains the residuals, that is any points that were not vectorized. This should be an empty image except for single isolated pixels that are ignored.
