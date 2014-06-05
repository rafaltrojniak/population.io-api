#!/bin/sh
set -e

if [ -e /.installed ]; then
  echo 'Already installed.'

else
  echo ''
  echo 'INSTALLING'
  echo '----------'

  # Update app-get
  apt-get -qq update

  # Install binary packages
  apt-get -qq -y install python-pip python-numpy python-scipy python-pandas python-numexpr python-tables libhdf5-dev git unzip

  echo ''
  echo 'PREPARING PROJECT'
  echo '-----------------'

  # Download the project
  if [ ! -e population.io ]; then
    git clone https://github.com/worldpopulation/population.io-api.git population.io
  fi

  # Install regular Python packages
  pip install --requirement population.io/requirements.txt

  # Extract the data file
  unzip -o population.io/data/WPP2012_INT_F3_Population_By_Sex_Annual_Single_100_Medium.zip -x "__MACOSX/*" -d population.io/data

  # Clean up
  chown -R vagrant:vagrant population.io
  touch /.installed

fi
