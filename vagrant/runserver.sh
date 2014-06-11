#!/bin/sh

echo ''
echo 'UPDATING AND RUNNING SERVER'
echo '---------------------------'

# Shut down existing gunicorns
ps aux | grep -ie gunicorn | awk '{print $2}' | xargs kill

# Update project
cd ~/population.io
git pull

# Run gunicorn server forked
. venv/bin/activate
gunicorn -b 0.0.0.0:8000 population_io.wsgi:application
