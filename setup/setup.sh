#!/bin/bash

#Installing apt packages first
sudo apt-get install -y postgresql

#Installing redis server
sudo apt-get install -y redis-server

sudo apt-get install -y python-pip

sudo pip install virtualenv

#Setup Postgres
sh setup/setup_psql.sh

mkdir -p venv && virtualenv venv/assignment && source "venv/assignment/bin/activate"

#Install pip packages
pip install -r requirements.txt 

cd assignment && ./manage.py migrate && ./manage.py loaddata initial_data
