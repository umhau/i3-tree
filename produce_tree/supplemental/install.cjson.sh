#!/bin/bash

sudo xbps-install -S cmake

rm -rfv ./cJSON
git clone https://github.com/DaveGamble/cJSON.git
cd ./cJSON

mkdir build
cd build
cmake ..
make
sudo make install
