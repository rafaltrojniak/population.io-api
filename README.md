population_io
=============

Django project for population.io

## Requirements

* Python 2.7
* pip 1.5+ (see http://pip.readthedocs.org/en/latest/installing.html for installation instructions)
* NumPy 1.7.0+, Pandas 0.13.1+ (see http://www.scipy.org/install.html for installation instructions)
* further dependencies are installed with pip from a requirements file into a virtualenv

If you're using apt-get as a package manager, the recommended set of initial packages is: `apt-get install unzip python-virtualenv python-pip python-pandas python-numpy`

## Project setup for development

```shell
# Create a virtualenv to isolate our package dependencies locally, but use system packages,
# because NumPy/Pandas are often better installed by external package managers
virtualenv --system-site-packages env

# Activate the new virtualenv
source env/bin/activate   # On Windows use `env\Scripts\activate`

# Install dependencies
pip install --requirement requirements.txt

# Decompress the data files
unzip "data/*.zip" -d data

# Run development server
python manage.py runserver
```

## Running unit tests

Run all unit tests with `python manage.py test`. 

## Extrapolation table cache

Many API requests require an extrapolation table (based on sex and country) to do their work. Generating this table can take a while (up to 20s on an average machine). 

By default, the extrapolation tables will be generated on-demand and then pickled into the `data` subdirectory as a cache. When the same extrapolation table is requested again, the cache will be checked first and only if the corresponding pickle file can't be found, the table will be generated again. Note that this cache can grow to many GiB in size over time if you request a lot of different tables.

This behavior can be configured with two environment variables:

* `POPULATIONIO_DATASTORE_LOCATION`: can be set to an alternative local directory to use as the pickle file cache location.
* `POPULATIONIO_DATASTORE_WRITABLE`: can be set to `false` (default: `true`) to deactivate pickle file caching. Deactivating this effectively means that extrapolation tables will be generated on-demand on every single API call.

## Prebuilding all extrapolation tables

If you have about 25 GiB to spare, you might want to generate all of these ahead of time, making the API calls really snappy (far below 1s).

Run `python manage.py buildtables` to rebuild all tables. Expect this to take about 2-4 hours. 

To just update the CSVs in the data store without rebuilding the tables, run `python manage.py reloadcsv`.

## Running on Vagrant

* Install Vagrant: https://www.vagrantup.com/.
* Run `vagrant up` in the `/vagrant` subdirectory of the project.
* View the API docs of your app at `http://localhost:9999/`.

## Deployment status
### Destination deployment

The destination deployment is going to be done using chef (http://chef.io/)
The cookbook is here (https://github.com/rafaltrojniak/population-io) and the recipes are quite self-documenting (see here https://github.com/rafaltrojniak/population-io/blob/master/recipes/node.rb)

The stack will consist of :
- Load balancer part with caching
 - Done based on nginx server
 - Simple HTTP caching will be done on API calls
- API server
-- The code is checked out as `populationio` user
 - The application is running as `populationio_app` user so it won't have write access to code or data
 - Daemon will be managed by supervisor instance
 - There will be many gunicorn daemons with single process each, so nginx can load-balance work on that level

### Temporary deployment on rackspace
This is done in manual way but simmilar to destination :
- the serparate user was created and application is running there
- The nginx works as http proxy and caching server
- Supervisord manages single gunicorn instance with 7 processes     
