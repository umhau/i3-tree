#!/bin/bash
# https://jansson.readthedocs.io/en/2.13/gettingstarted.html#compiling-and-installing-jansson

set -e

mkdir -pv build
cd build

sudo xbps-install -u xbps && sudo xbps-install -S autoconf automake libtool

wget https://digip.org/jansson/releases/jansson-2.13.1.tar.gz

tar xvzf jansson-2.13.1.tar.gz

cd jansson-2.13.1

./configure
make
make check
sudo make install
