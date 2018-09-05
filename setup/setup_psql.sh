#!/bin/bash

echo "You might be prompted to provide your postgres user password..."
sudo -u postgres psql -f setup/user_init.sql
dir=/etc/postgresql/*/main
sudo cp config/pg_hba.conf $dir/
sudo service postgresql restart

