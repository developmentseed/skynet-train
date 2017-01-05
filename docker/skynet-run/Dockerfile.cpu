FROM developmentseed/caffe-segnet:cpu
ENV DEBIAN_FRONTEND noninteractive
RUN curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash - && \
    sudo apt-get install -y nodejs build-essential libagg-dev libpotrace-dev && \
    pip install flask && \
    pip install mercantile && \
    pip install boto3 && \
    pip install git+https://github.com/flupke/pypotrace.git@master

ADD package.json /workspace/package.json
RUN npm install
ADD . /workspace
EXPOSE 5000

ENV SKYNET_CPU_ONLY=1
