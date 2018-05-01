FROM developmentseed/caffe-segnet:gpu
ENV DEBIAN_FRONTEND noninteractive
RUN sudo apt-get update && sudo apt-get install curl -y

# GDAL
RUN sudo apt-get install software-properties-common -y && \
    sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable -y && \
    sudo apt-get update && sudo apt-get install gdal-bin python-gdal libgdal1-dev -y

# Node
RUN curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash - && \
    sudo apt-get install -y nodejs build-essential libagg-dev libpotrace-dev

# Python
RUN pip install numpy==1.14.2

RUN pip install flask && \
    pip install mercantile && \
    pip install rasterio==1.0a12 && \
    pip install boto3 && \
    pip install pyproj && \
    pip install git+https://github.com/flupke/pypotrace.git@master

ADD package.json /workspace/package.json
RUN npm install
ADD . /workspace
EXPOSE 5000
