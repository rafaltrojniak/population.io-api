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

## Running on Vagrant box

* Install Vagrant: https://www.vagrantup.com/.
* Run `vagrant up` in the `/vagrant` subdirectory of the project.
* View the API docs of your app at `http://localhost:9999/api/docs/`.
