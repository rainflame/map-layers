#!/bin/bash

echo -e "\nInstalling dependencies...\n"

apt-get update

apt-get install -y \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    python3-dev \
    python3-pip \
    python3-venv \
    build-essential \
    libsqlite3-dev \
    zlib1g-dev

echo -e "\nInstalling tippecanoe...\n"

cd ..
git clone https://github.com/mapbox/tippecanoe.git
cd tippecanoe
make -j
make install 
cd ..
rm -rf tippecanoe


echo -e "\nInstalling pmtiles...\n"

# TODO