#!/bin/bash

# Use this to install production dependencies on a new cloud server.
# Tested with Ubuntu 18.04 on AWS.

set -ex

sudo apt -y update
sudo apt -y upgrade

# Setup git, Docker & docker-compose

sudo apt-get -y install \
    apt-transport-https \
    ca-certificates \
    git \
    gnupg-agent \
    software-properties-common \
    wget

wget -q -O - "https://download.docker.com/linux/ubuntu/gpg" | sudo apt-key add -
sudo apt-add-repository -y "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

sudo apt-get -y install docker-ce

sudo wget -q -O /usr/local/bin/docker-compose "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)"
sudo chmod +x /usr/local/bin/docker-compose

sudo gpasswd -a "$USER" docker  # You'll need to restart your session for this to take effect
