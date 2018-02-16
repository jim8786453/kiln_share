#!/bin/bash
apt-get -y update
cd ~/deploy/downloads
wget -c https://github.com/platinummonkey/nginx-jwt/archive/v1.1.0.tar.gz
tar xvf v1.1.0.tar.gz
./nginx-jwt-1.1.0/scripts/build_deps.sh
mv nginx-jwt-1.1.0/nginx-jwt.lua ~/deploy/bin/nginx-jwt.lua
mv lib/* ~/deploy/bin/
