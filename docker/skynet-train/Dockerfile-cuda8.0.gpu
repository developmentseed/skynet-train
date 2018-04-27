FROM developmentseed/caffe-segnet:cuda8
MAINTAINER anand@developmentseed.org

ENV DEBIAN_FRONTEND noninteractive
RUN sudo apt-get update && sudo apt-get install curl -y
RUN curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash - && \
    sudo apt-get install -y nodejs build-essential

RUN pip install boto3 && \
    pip install protobuf && \
    pip install cython && \
    pip install scikit-image

# bsdmainutils is for 'paste' and 'column' commands, used in plot_training_log
RUN pip install awscli && \
    apt-get install -y bsdmainutils

ADD package.json /workspace/package.json
RUN npm install

ADD . /workspace
WORKDIR /workspace

# Expose demo server port
EXPOSE 5000

ENTRYPOINT ["python", "-u", "segnet/train"]
