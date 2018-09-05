#!/bin/bash

prev_user=$USER
sudo -s
su postgres
su prev_user

sudo mv /etc/postgresql/10/main/pg_hba.conf /etc/postgresql/10/main/pg_hba_default.conf
sudo cp ../config/pg_hba.conf /etc/postgresql/10/main/
sudo service postgresql restart

