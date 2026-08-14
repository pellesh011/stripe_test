#!/bin/bash

set -e

echo "========================================"
echo "Starting Codespace application"
echo "========================================"

echo ""
echo "Creating backend .env..."

cat > .env <<EOF
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5433
DATABASE_USER=${DATABASE_USER}
DATABASE_PASSWORD=${DATABASE_PASSWORD}
DATABASE_DB=${DATABASE_DB}

TEST_DATABASE_HOST=127.0.0.1
TEST_DATABASE_PORT=5434
TEST_DATABASE_USER=${DATABASE_USER}
TEST_DATABASE_PASSWORD=${DATABASE_PASSWORD}
TEST_DATABASE_DB=stripe

STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}
STRIPE_PUBLIC_KEY=${STRIPE_PUBLIC_KEY}
EOF

echo "Backend .env created."

echo ""
echo "Creating frontend/.env..."

cat > frontend/.env <<EOF
VITE_STRIPE_PUBLIC_KEY=${STRIPE_PUBLIC_KEY}
VITE_API_URL=https://${CODESPACE_NAME}-8000.app.github.dev
EOF

echo "Frontend .env created."

echo ""
echo "Starting Docker Compose..."

docker compose up -d

echo ""
echo "Docker Compose started."

docker compose ps

echo ""
echo "========================================"
echo "Configuring Codespace ports"
echo "========================================"

if ! command -v gh >/dev/null 2>&1; then
    echo "ERROR: GitHub CLI is not installed."
    echo "Install github-cli Dev Container Feature."
    exit 1
fi

echo "GitHub CLI:"
gh --version

echo ""
echo "GitHub authentication:"
gh auth status

echo ""
echo "Setting ports to public..."

gh codespace ports visibility \
    8000:public \
    5173:public \
    --codespace "$CODESPACE_NAME"

echo ""
echo "Current port configuration:"

gh codespace ports \
    --codespace "$CODESPACE_NAME"

echo ""
echo "========================================"
echo "Codespace startup completed"
echo "========================================"