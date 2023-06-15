FROM python:3.8-slim-buster

# Python environments
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Packages required for setting up WSGI
RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc libc-dev python3-dev

# Install psycopg dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Make project
ENV PROJECT=/home/app
RUN mkdir -p $PROJECT
WORKDIR $PROJECT

# Install requirements
RUN pip install --upgrade pip
COPY ./requirements.txt $PROJECT/requirements.txt 
RUN pip install -r $PROJECT/requirements.txt --default-timeout=100 future

# Add files to container
COPY . $PROJECT

# Make deployments scripts executable
RUN chmod +x ./deploy.sh
