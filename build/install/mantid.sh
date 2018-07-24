#!/bin/sh

set -e

# Add GPG key and upstream Mantid repo
sudo apt-add-repository "deb [arch=amd64] http://apt.isis.rl.ac.uk $(lsb_release -c | cut -f 2) main" -y
# add the signing key
wget -O - http://apt.isis.rl.ac.uk/2E10C193726B7213.asc -q | sudo apt-key add -
sudo apt-add-repository ppa:mantid/mantid -y

sudo apt-get install mantid
