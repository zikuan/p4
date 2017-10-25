#!/bin/bash

# Print script commands.
set -x
# Exit on errors.
set -e

BMV2_COMMIT="ae84c2f6d5bc3dd6873a62e351f26c39038804da"
PI_COMMIT="f06a4df7d56413849dbe9ab8f9441321ff140bca"
P4C_COMMIT="3ad8d93f334a34d181e8d9d83100d797bac3f65a"
PROTOBUF_COMMIT="tags/v3.0.2"
GRPC_COMMIT="tags/v1.3.0"

NUM_CORES=`grep -c ^processor /proc/cpuinfo`

# Protobuf
git clone https://github.com/google/protobuf.git
cd protobuf
git checkout ${PROTOBUF_COMMIT}
export CFLAGS="-Os"
export CXXFLAGS="-Os"
export LDFLAGS="-Wl,-s"
./autogen.sh
./configure --prefix=/usr
make -j${NUM_CORES}
sudo make install
sudo ldconfig
unset CFLAGS CXXFLAGS LDFLAGS
cd ..

# gRPC
git clone https://github.com/grpc/grpc.git
cd grpc
git checkout ${GRPC_COMMIT}
git submodule update --init
export LDFLAGS="-Wl,-s"
make -j${NUM_CORES}
sudo make install
sudo ldconfig
unset LDFLAGS
cd ..

# BMv2 deps (needed by PI)
git clone https://github.com/p4lang/behavioral-model.git
cd behavioral-model
git checkout ${BMV2_COMMIT}
# From bmv2's install_deps.sh, we can skip apt-get install.
# Nanomsg is required by p4runtime, p4runtime is needed by BMv2...
tmpdir=`mktemp -d -p .`
cd ${tmpdir}
bash ../travis/install-thrift.sh
bash ../travis/install-nanomsg.sh
sudo ldconfig
bash ../travis/install-nnpy.sh
cd ..
sudo rm -rf $tmpdir
cd ..

# PI/P4Runtime
git clone https://github.com/p4lang/PI.git
cd PI
git checkout ${PI_COMMIT}
git submodule update --init --recursive
./autogen.sh
./configure --with-proto
make -j${NUM_CORES}
sudo make install
sudo ldconfig
cd ..

# Bmv2
cd behavioral-model
./autogen.sh
./configure --enable-debugger --with-pi
make -j${NUM_CORES}
sudo make install
sudo ldconfig
# Simple_switch_grpc target
cd targets/simple_switch_grpc
./autogen.sh
./configure
make -j${NUM_CORES}
sudo make install
sudo ldconfig
cd ..
cd ..
cd ..

# P4C
git clone https://github.com/p4lang/p4c
cd p4c
git checkout ${P4C_COMMIT}
git submodule update --init --recursive
mkdir -p build
cd build
cmake ..
make -j${NUM_CORES}
sudo make install
sudo ldconfig
cd ..
cd ..

# Tutorials
pip install crcmod
git clone https://github.com/p4lang/tutorials
sudo mv tutorials /home/p4
sudo chown -R p4:p4 /home/p4/tutorials

# Emacs
sudo cp p4_16-mode.el /usr/share/emacs/site-lisp/
echo "(add-to-list 'auto-mode-alist '(\"\\.p4\\'\" . p4_16-mode))" | sudo tee /home/p4/.emacs
sudo chown p4:p4 /home/p4/.emacs

# Vim
cd /home/vagrant
mkdir .vim
cd .vim
mkdir ftdetect
mkdir syntax
echo "au BufRead,BufNewFile *.p4      set filetype=p4" >> ftdetect/p4.vim
cp /home/vagrant/p4.vim syntax/p4.vim
cd /home/vagrant
sudo mv .vim /home/p4/.vim
sudo chown -R p4:p4 /home/p4/.vim

