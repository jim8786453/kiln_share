#!/bin/bash
apt-get -y update
cd ~/deploy/downloads
wget -c https://github.com/auth0/nginx-jwt/releases/download/v1.0.1/nginx-jwt.tar.gz
tar xvf nginx-jwt.tar.gz -C ~/deploy/bin/nginx-jwt/
