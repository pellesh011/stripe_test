#!/bin/bash

set -e

echo "Starting Docker Compose..."

docker compose up -d

echo "Waiting for PostgreSQL..."

until docker compose exec -T db pg_isready \
    -U "${DATABASE_USER}" \
    -d "${DATABASE_DB}"
do
    sleep 2
done

echo "PostgreSQL is ready."