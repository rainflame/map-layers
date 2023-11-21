#!/bin/bash

# this script sets up a clean ubuntu machine with the necessary dependencies to run any of the pipelines in this repo
# assuming this is run from $HOME/pika-datasets

echo "Creating swapfile..."

# create a swapfile. here we use 4GB but adjust as necessary
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
# make swap permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

echo "Installing dependencies..."

export NEEDRESTART_MODE=a
export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y \
    libpq-dev \
    python3-dev \
    python3-pip \
    python3-venv \
    build-essential \
    libsqlite3-dev \
    zlib1g-dev

echo "Installing miniforge..."

wget -O Miniforge3.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3.sh -b -p "${HOME}/conda"
rm Miniforge3.sh

echo -e 'source "${HOME}/conda/etc/profile.d/conda.sh"' >> ~/.bashrc 
echo -e 'source "${HOME}/conda/etc/profile.d/mamba.sh"' >> ~/.bashrc 
source "${USER}/.bashrc"

echo "Creating conda environment..."

mamba env create -f environment.yml 

echo "Installing rclone..."

sudo -v ; curl https://rclone.org/install.sh | sudo bash

cp rclone.conf "/${USER}/.config/rclone/rclone.conf"

echo "Done!"