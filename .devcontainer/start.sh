#!/bin/bash

set -e

echo "========================================"
echo "Starting Codespace application"
echo "========================================"

echo ""
echo "Codespace: ${CODESPACE_NAME}"

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
    exit 1
fi

echo ""
echo "GitHub CLI:"
gh --version

echo ""
echo "GitHub authentication:"
gh auth status

echo ""
echo "Waiting for forwarded ports..."

PORTS_READY=false

for attempt in {1..20}; do
    echo ""
    echo "Port check ${attempt}/20..."

    PORTS="$(gh codespace ports \
        --codespace "$CODESPACE_NAME" \
        --json sourcePort,visibility 2>/dev/null || true)"

    echo "$PORTS"

    if echo "$PORTS" | grep -q '"sourcePort":8000' &&
       echo "$PORTS" | grep -q '"sourcePort":5173'
    then
        echo ""
        echo "Required ports detected."

        PORTS_READY=true
        break
    fi

    echo "Ports are not ready yet."

    if [ "$attempt" -lt 20 ]; then
        sleep 3
    fi
done

if [ "$PORTS_READY" = false ]; then
    echo ""
    echo "ERROR: Ports 8000 and/or 5173 were not detected."
    exit 1
fi

echo ""
echo "Setting ports to public..."

gh codespace ports visibility \
    8000:public \
    5173:public \
    --codespace "$CODESPACE_NAME"

echo ""
echo "Checking final port configuration..."

for attempt in {1..10}; do
    PORTS="$(gh codespace ports \
        --codespace "$CODESPACE_NAME" \
        --json sourcePort,visibility)"

    echo "$PORTS"

    PORT_8000_PUBLIC=false
    PORT_5173_PUBLIC=false

    if echo "$PORTS" | grep -q '"sourcePort":8000' &&
       echo "$PORTS" | grep -q '"visibility":"public"'
    then
        PORT_8000_PUBLIC=true
    fi

    if echo "$PORTS" | grep -q '"sourcePort":5173' &&
       echo "$PORTS" | grep -q '"visibility":"public"'
    then
        PORT_5173_PUBLIC=true
    fi

    if [ "$PORT_8000_PUBLIC" = true ] &&
       [ "$PORT_5173_PUBLIC" = true ]
    then
        echo ""
        echo "========================================"
        echo "Ports are PUBLIC"
        echo "========================================"

        break
    fi

    echo ""
    echo "Visibility has not been applied yet."

    if [ "$attempt" -lt 10 ]; then
        echo "Retrying..."

        sleep 3

        gh codespace ports visibility \
            8000:public \
            5173:public \
            --codespace "$CODESPACE_NAME"
    fi
done

echo ""
echo "========================================"
echo "Final port configuration"
echo "========================================"

gh codespace ports \
    --codespace "$CODESPACE_NAME"

echo ""
echo "========================================"
echo "Codespace startup completed"
echo "========================================"