#!/bin/bash

set -e

echo "Creating backend .env..."

cat > .env <<EOF
# Подключение к БД (основная)
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5433
DATABASE_USER=${DATABASE_USER}
DATABASE_PASSWORD=${DATABASE_PASSWORD}
DATABASE_DB=${DATABASE_DB}

# Подключение к БД для тестов
TEST_DATABASE_HOST=127.0.0.1
TEST_DATABASE_PORT=5434
TEST_DATABASE_USER=${DATABASE_USER}
TEST_DATABASE_PASSWORD=${DATABASE_PASSWORD}
TEST_DATABASE_DB=stripe

# Ключи Stripe (тестовые)
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}
STRIPE_PUBLIC_KEY=${STRIPE_PUBLIC_KEY}
EOF

echo "Creating frontend/.env..."

cat > frontend/.env <<EOF
VITE_STRIPE_PUBLIC_KEY=${STRIPE_PUBLIC_KEY}
VITE_API_URL=https://shiny-succotash-g9wrrvx7pvphvqww-8000.app.github.dev
EOF

echo "Starting Docker Compose..."

docker compose up -d

echo "Docker Compose started."

docker compose ps