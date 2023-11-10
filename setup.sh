#!/bin/bash

# this script sets up a clean machine with the necessary dependencies to run any of the pipelines in this repo

echo -e "\nInstalling dependencies...\n"

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

echo -e "\nInstalling miniforge...\n"

wget -O Miniforge3.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3.sh -b -p "${HOME}/conda"

source "${HOME}/conda/etc/profile.d/conda.sh"
source "${HOME}/conda/etc/profile.d/mamba.sh"

echo -e "\nCreating environment...\n"

mamba env create -f environment.yml 

echo -e "\nActivating environment...\n"

mamba activate pika-datasets

