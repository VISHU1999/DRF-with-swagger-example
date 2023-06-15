#!/bin/bash

set -e

echo "Container's IP address: `awk 'END{print $1}' /etc/hosts`"

function _wait_database () {
  # Wait until the database is up and running.
  # REF: https://docs.docker.com/compose/startup-order/

  RETRIES=10
  until psql postgres --command='\q'; do
    >&2 echo "Waiting for postgres server: Remaining attempts: $((RETRIES--))"
    if [ $RETRIES -eq 0 ]; then
      echo "Waiting for postgres server: Can't access postgres server. Check database logs for errors."
      exit 1
    fi
    sleep 6
  done
  >&2 echo "Waiting for postgres server: Server is up."
}

python manage.py migrate

exec "$@"
