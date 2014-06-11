#!/bin/sh
set -e

echo ''
echo 'CONFIGURING SYSTEM'
echo '------------------'

# Update app-get
apt-get -qq update

# Install binary packages
apt-get -qq -y install git unzip python-virtualenv python-pip python-scipy python-pandas python-numexpr python-tables libhdf5-dev
