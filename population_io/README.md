population_io
=============

Django project for population.io

## Requirements

* Python 2.7
* pip 1.5+
* NumPy 1.7.0+, SciPy 0.11.0+, Pandas 0.13.1+ (see http://www.scipy.org/install.html for installation instructions)
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

## Deploying to Heroku

Deployment to Heroku requires a custom buildpack, because _NumPy_ and _SciPy_ have some binary dependencies which can't be installed through pip. See https://blog.dbrgn.ch/2013/6/18/heroku-buildpack-numpy-scipy-scikit-learn/ for more information.

Follow these steps to run your own testing instance on Heroku:

* Set up Heroku account, install the Heroku toolbelt and log in. See: https://devcenter.heroku.com/articles/quickstart.
* Run `heroku create --buildpack https://github.com/dbrgn/heroku-buildpack-python-sklearn/`. Note the URL of your new app and the Heroku git repo URL.
* If Heroku didn't create a git remote for you, run `git remote add heroku <git_repo_url>`.
* Run `git subtree push --prefix population_io heroku master` to deploy to Heroku and run your app. Make yourself a cup of coffee, because compiling the _pandas_ dependency will take a while...
* View the API docs of your app at `http://<heroku_app_name>.herokuapp.com/api/docs/`.
