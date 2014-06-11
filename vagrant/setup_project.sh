#!/bin/sh
set -e

echo ''
echo 'PREPARING PROJECT'
echo '-----------------'

# Download the project
if [ ! -e population.io ]; then
git clone https://github.com/worldpopulation/population.io-api.git population.io
fi
cd population.io

# Prepare virtualenv
virtualenv --system-site-packages venv
. venv/bin/activate

# Install regular Python packages
pip install --requirement requirements.txt

# Extract the data files
unzip -o data/WPP2012_INT_F3_Population_By_Sex_Annual_Single_100_Medium.zip -x "__MACOSX/*" -d data/
unzip -o data/life_expectancy_ages.zip -x "__MACOSX/*" -d data/
