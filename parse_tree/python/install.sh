#!/bin/bash

python3 -m venv ./i3-tree-python-venv

source ./i3-tree-python-venv/bin/activate

pip install -U pip

pip install i3ipc

deactivate
