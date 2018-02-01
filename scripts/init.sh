#!/usr/bin/env bash

pip install -r dev-requirements.txt

virtualenv -p `pyenv which python3` venv
source venv/bin/activate