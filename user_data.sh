#!/bin/bash

## Install docker (ubuntu Xenial 16.04 (LTS))
## https://docs.docker.com/engine/installation/linux/ubuntulinux/
apt-get update
apt-get install apt-transport-https ca-certificates -y
apt-key adv \
               --keyserver hkp://ha.pool.sks-keyservers.net:80 \
               --recv-keys 58118E89F3A912897C070ADBF76221572C52609D

echo "deb https://apt.dockerproject.org/repo ubuntu-xenial main" | tee /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install linux-image-extra-$(uname -r) linux-image-extra-virtual -y
apt-get update
apt-get install docker-engine -y
service docker start

# Install NVIDIA drivers 361.42
# Install nvidia-docker and nvidia-docker-plugin
# https://github.com/NVIDIA/nvidia-docker/wiki/Deploy-on-Amazon-EC2
apt-get install --no-install-recommends -y gcc make libc-dev
wget -P /tmp http://us.download.nvidia.com/XFree86/Linux-x86_64/361.42/NVIDIA-Linux-x86_64-361.42.run
wget -P /tmp https://github.com/NVIDIA/nvidia-docker/releases/download/v1.0.0/nvidia-docker_1.0.0-1_amd64.deb
sh /tmp/NVIDIA-Linux-x86_64-361.42.run --silent
dpkg -i /tmp/nvidia-docker*.deb && rm /tmp/nvidia-docker*.deb

# Install Node
# https://nodejs.org/en/download/package-manager/#debian-and-ubuntu-based-linux-distributions
curl -sL https://deb.nodesource.com/setup_6.x | -E bash -
apt-get install -y nodejs

# Install awscli
apt-get install awscli -y
