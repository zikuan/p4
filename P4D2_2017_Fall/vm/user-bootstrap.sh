#!/bin/bash

set -x

# Bmv2
git clone https://github.com/p4lang/behavioral-model
cd behavioral-model
./install_deps.sh
./autogen.sh
./configure
make
sudo make install
cd ..

# Protobuf
git clone https://github.com/google/protobuf.git
cd protobuf
git checkout v3.0.2
./autogen.sh
./configure
make
sudo make install
sudo ldconfig
cd ..

# P4C
git clone --recursive https://github.com/p4lang/p4c
cd p4c
mkdir build
cd build
cmake ..
make -j4
sudo make install
cd ..
cd ..

# Tutorials
pip install crcmod
git clone https://github.com/p4lang/tutorials
cd tutorials
git checkout sigcomm_17
cd ..
sudo mv tutorials /home/p4
sudo chown -R p4:p4 /home/p4/tutorials

# Emacs
sudo cp p4_16-mode.el /usr/share/emacs/site-lisp/
sudo echo "(add-to-list 'auto-mode-alist '(\"\\.p4\\'\" . p4_16-mode))" >> /home/p4/.emacs
sudo chown p4:p4 /home/p4/.emacs

