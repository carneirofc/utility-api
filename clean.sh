#!/bin/sh
set -eux
find  -H -type d -regex '.*__pycache__' -exec rm -rf {} +;
find  -H -type f -regex '.*\.pyc' -exec rm -f {} +;
