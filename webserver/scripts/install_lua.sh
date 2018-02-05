#!/bin/bash
rm -rf ~/.cache/luarocks
apt-get update
apt-get install -y unzip zip
cd ~/deploy/downloads
rm luarocks-2.0.13.tar.gz
wget http://luarocks.org/releases/luarocks-2.0.13.tar.gz
tar -xzvf luarocks-2.0.13.tar.gz
cd luarocks-2.0.13/
./configure --prefix=/usr/local/openresty/luajit \
    --with-lua=/usr/local/openresty/luajit/ \
    --lua-suffix=jit \
    --with-lua-include=/usr/local/openresty/luajit/include/luajit-2.1
make
make install
/usr/local/openresty/luajit/bin/luarocks install lua-sec OPENSSL_LIBDIR=/usr/lib/x86_64-linux-gnu/
/usr/local/openresty/luajit/bin/luarocks install penlight OPENSSL_LIBDIR=/usr/lib/x86_64-linux-gnu/
/usr/local/openresty/luajit/bin/luarocks install lua-requests OPENSSL_LIBDIR=/usr/lib/x86_64-linux-gnu/
/usr/local/openresty/luajit/bin/luarocks install lua-resty-template OPENSSL_LIBDIR=/usr/lib/x86_64-linux-gnu/
/usr/local/openresty/luajit/bin/luarocks install lua-resty-session OPENSSL_LIBDIR=/usr/lib/x86_64-linux-gnu/
/usr/local/openresty/luajit/bin/luarocks install lua-cjson OPENSSL_LIBDIR=/usr/lib/x86_64-linux-gnu/
