# Base Image
FROM python:3.8-slim-buster

# Python environment setup
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Setting working directory
ENV PROJECT=/home/app
RUN mkdir -p ${PROJECT}
RUN mkdir -p ${PROJECT}/logs
RUN mkdir -p ${PROJECT}/media
WORKDIR ${PROJECT}


# Installing packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libc-dev python3-dev
RUN python -m pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install psycopg2-binary

# Installing requirements
COPY ./requirements.txt ${PROJECT}/requirements.txt
RUN pip install -r ${PROJECT}/requirements.txt

# Copying project
COPY . ${PROJECT}

# Migrations
RUN python manage.py makemigrations
RUN python manage.py migrate

EXPOSE 8000

# Running application
# CMD [ "/bin/sh", "${PROJECT}/entrypoint.sh" ]