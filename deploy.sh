#!/bin/bash

# Variables
NAME="SEMA_BACKEND"
PROJECT_DIR="/home/app"
DJANGO_WSGI_MODULE="_project.wsgi"
NUM_WORKERS=4
NUM_THREADS=4
TIMEOUT=1800
HOST=0.0.0.0
PORT=8001

# Migrations
python $PROJECT_DIR/manage.py makemigrations
python $PROJECT_DIR/manage.py migrate
python $PROJECT_DIR/manage.py flush --no-input
python $PROJECT_DIR/manage.py runserver $HOST:$PORT