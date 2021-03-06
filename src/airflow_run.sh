#!/bin/sh


set -o errexit
set -o nounset


echo "airflow database init ...."

airflow initdb

sleep 5

echo "airflow app started ...."

airflow webserver -p 5050 & sleep 2 & airflow scheduler