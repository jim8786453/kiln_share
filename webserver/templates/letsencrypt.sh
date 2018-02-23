#!/bin/bash
cd ~/deploy/
apt-get update
apt-get install -y letsencrypt
sudo letsencrypt certonly \
     --webroot \
     --webroot-path /home/{{user}}/deploy/www \
     --renew-by-default \
     --email jim@kohlstudios.co.uk \
     --text \
     --agree-tos \
     -d {{server_name}}
openssl dhparam -out dhparams.pem 2048
