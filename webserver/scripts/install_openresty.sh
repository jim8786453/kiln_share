#!/bin/bash
apt-get -y update
cd ~/deploy/downloads
wget -c https://openresty.org/download/openresty-1.11.2.2.tar.gz
tar zxvf openresty-1.11.2.2.tar.gz
cd openresty-1.11.2.2
apt-get install -y libreadline-dev libncurses5-dev libpcre3-dev \
    libssl-dev perl make build-essential curl
apt-get install -y libjson0 libjson0-dev
./configure -j2 \
--with-luajit \
--with-pcre-jit \
--with-ipv6

make -j2
make install
