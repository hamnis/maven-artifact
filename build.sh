#!/bin/bash

./clean.sh

python setup.py bdist_wheel --universal
