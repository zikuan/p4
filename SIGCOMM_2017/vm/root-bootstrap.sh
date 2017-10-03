#!/bin/bash

set -x

sudo add-apt-repository ppa:webupd8team/sublime-text-3
sudo add-apt-repository ppa:webupd8team/atom

apt-get update

DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade

apt-get install -y \
  lubuntu-desktop \
  git \
  vim \
  emacs24 \
  xcscope-el \
  sublime-text-installer \
  atom \
  xterm \
  mininet \
  autoconf \
  automake \
  libtool \
  curl \
  make \
  g++ \
  unzip \
  libgc-dev \
  bison \
  flex \
  libfl-dev \
  libgmp-dev \
  libboost-dev \
  libboost-iostreams-dev \
  pkg-config \
  python \
  python-scapy \
  python-ipaddr \
  tcpdump \
  cmake

useradd -m -d /home/p4 -s /bin/bash p4
echo "p4:p4" | chpasswd
echo "p4 ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/99_p4
chmod 440 /etc/sudoers.d/99_p4

cd /usr/share/lubuntu/wallpapers/
cp /home/vagrant/p4-logo.png .
rm lubuntu-default-wallpaper.png
ln -s p4-logo.png lubuntu-default-wallpaper.png
rm /home/vagrant/p4-logo.png
cd /home/vagrant
sed -i s@#background=@background=/usr/share/lubuntu/wallpapers/1604-lubuntu-default-wallpaper.png@ /etc/lightdm/lightdm-gtk-greeter.conf
