#!/bin/bash

#Installing apt packages first
sudo apt-get install -y postgresql

#Installing redis server
sudo apt-get install -y redis-server

#Setup Postgres
./setup_psql.sh

mkdir venv && cd venv && virtualenv assignment and source assignment/bin/activate

#Install pip packages
pip install -r requirements.txt

cd assignment && ./manage.py migrate && ./manage.py loaddata initial_data
