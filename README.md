# Welcome to Paper

This backend repo was built off of the package Cookiecutter Django 
https://cookiecutter-django.readthedocs.io

## Installation Requirements
1. Make sure you have Python 3 and Pip installed
2. Have Pipenv package as well to create virtual environments

## Setup
1. Clone or download this repo
2. Run `pipenv shell` to start the virtual environment
3. Run `pip install -r requirements/local.txt` to download required packages into your virtual environment
4. Create a postgres database `createdb paper`
5. Set up postgres `export DATABASE_URL=postgres://postgres:<password>@127.0.0.1:5432/paper` with your password as your regular administrator password
6. Apply migrations `python manage.py migrate`
7. Run the server `python manage.py runserver` to run at default `http://127.0.0.1:8000/`
8. Open up `http://localhost:8000/`

## Django Admin Dashboard
1. Create a superuser for admin purposes `python manage.py createsuperuser`
2. Run the server and navigate to`http://localhost:8000/admin`
3. Loging using your superuser information

## Postgres
1. Run `brew install postgres`
2. Examine database by running `psql` to open up to postgres terminal

## Running tests
1. Run `pytest`
