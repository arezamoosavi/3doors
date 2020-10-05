#!/bin/sh


set -o errexit
set -o nounset


sleep 30

echo "airflow database init ...."

airflow initdb

sleep 5

echo "airflow app started ...."

airflow webserver -p 5050 & sleep 5 & airflow scheduler