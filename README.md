population_io
=============

Django project for population.io

## Requirements

* Python 2.7
* pip 1.5+
* NumPy 1.7.0+, SciPy 0.11.0+, Pandas 0.13.1+ (see http://www.scipy.org/install.html for installation instructions)
* PyTables 3.1+
* further dependencies can be installed with pip from a requirements file

## Project setup for development

```shell
# Create a virtualenv to isolate our package dependencies locally
virtualenv env
source env/bin/activate  # On Windows use `env\Scripts\activate`

# Install dependencies
pip install --requirement requirements.txt

# Run development server
python manage.py runserver
```

You will also have to unpack the CSV data files in the `data` subdirectory.

## Running unit tests

Run all unit tests with `python manage.py test`. 

## Prebuilding all extrapolation tables

Many API requests require an extrapolation table (based on sex and country) to do their work. Generating this table can take a while (up to 20s on an average machine). Therefore, if you have about 25 GiB to spare, you might want to generate all of these ahead of time making the API calls really snappy (far below 1s).

Run `python manage.py buildtables` to rebuild all tables. Expect this to take about 2-4 hours. 

To just update the CSVs in the data store without rebuilding the tables, run `python manage.py reloadcsv`.

## Running on Vagrant

* Install Vagrant: https://www.vagrantup.com/.
* Run `vagrant up` in the `/vagrant` subdirectory of the project.
* View the API docs of your app at `http://localhost:9999/api/docs/`.

## Running in production

When running on production, you should set the environment variable `POPULATIONIO_DEBUG` to `False`. This deactivates the display of internal exceptions and also disables caching of the extrapolation tables in memory, which does not scale in production.
