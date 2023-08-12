#!/bin/sh
daphne  daphne _project.asgi:application -b [::] -p 8000

exec "$@"