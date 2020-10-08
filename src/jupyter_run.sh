#!/bin/sh


set -o errexit
set -o nounset

sleep 30

jupyter lab --port=1100 --no-browser --ip=0.0.0.0 --allow-root