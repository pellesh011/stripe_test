#!/bin/bash

set -Eeuo pipefail

# ============================================================
# LOGGING
# ============================================================

LOG_DIR=".devcontainer/logs"
LOG_FILE="${LOG_DIR}/start.log"

mkdir -p "$LOG_DIR"

touch "$LOG_FILE"

exec > >(tee -a "$LOG_FILE") 2>&1

START_TIME=$(date '+%Y-%m-%d %H:%M:%S')

echo ""
echo "============================================================"
echo "START.SH"
echo "Started: ${START_TIME}"
echo "PID: $$"
echo "============================================================"
echo ""


log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}


on_error() {
    local exit_code=$?

    echo ""
    echo "============================================================"
    echo "START.SH FAILED"
    echo "Exit code: ${exit_code}"
    echo "Line: ${BASH_LINENO[0]:-unknown}"
    echo "Command: ${BASH_COMMAND:-unknown}"
    echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "============================================================"

    echo ""
    echo "================ DOCKER PS ================"

    docker ps -a 2>&1 || true

    echo ""
    echo "================ COMPOSE PS ==============="

    docker compose ps 2>&1 || true

    echo ""
    echo "================ COMPOSE LOGS ============="

    docker compose logs --tail=100 2>&1 || true

    echo ""
    echo "================ CODESPACE PORTS =========="

    if command -v gh >/dev/null 2>&1; then
        gh codespace ports \
            --codespace "${CODESPACE_NAME:-}" \
            2>&1 || true
    fi

    echo ""
    echo "============================================================"
    echo "END ERROR LOG"
    echo "============================================================"

    exit "$exit_code"
}


trap on_error ERR


# ============================================================
# START
# ============================================================

log "Starting Codespace application"

log "Working directory: $(pwd)"
log "User: $(whoami)"
log "Hostname: $(hostname)"
log "CODESPACE_NAME=${CODESPACE_NAME:-<not set>}"


# ============================================================
# ENVIRONMENT
# ============================================================

log "Checking required environment variables..."

required_vars=(
    CODESPACE_NAME
    DATABASE_USER
    DATABASE_PASSWORD
    DATABASE_DB
    STRIPE_SECRET_KEY
    STRIPE_WEBHOOK_SECRET
    STRIPE_PUBLIC_KEY
)

for variable in "${required_vars[@]}"; do
    if [ -z "${!variable:-}" ]; then
        log "ERROR: ${variable} is not set"
        exit 1
    fi

    log "${variable}=<set>"
done


# ============================================================
# BACKEND ENV
# ============================================================

log "Creating backend .env..."

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

log "Backend .env created."


# ============================================================
# FRONTEND ENV
# ============================================================

log "Creating frontend/.env..."

cat > frontend/.env <<EOF
VITE_STRIPE_PUBLIC_KEY=${STRIPE_PUBLIC_KEY}
VITE_API_URL=https://${CODESPACE_NAME}-8000.app.github.dev
EOF

log "Frontend .env created."


# ============================================================
# GITHUB CLI
# ============================================================

log "Checking GitHub CLI..."

if ! command -v gh >/dev/null 2>&1; then
    log "ERROR: GitHub CLI is not installed."
    exit 1
fi

log "GitHub CLI version:"
gh --version

log "Checking GitHub authentication..."

if ! gh auth status >/dev/null 2>&1; then
    log "ERROR: GitHub CLI is not authenticated."
    exit 1
fi

log "GitHub authentication OK."


# ============================================================
# DOCKER
# ============================================================

log "========================================"
log "Waiting for Docker"
log "========================================"

DOCKER_READY=false

for attempt in {1..30}; do

    if docker info >/dev/null 2>&1; then
        log "Docker is ready."

        DOCKER_READY=true

        break
    fi

    log "Docker is not ready yet (${attempt}/30)..."

    sleep 2
done


if [ "$DOCKER_READY" = false ]; then
    log "ERROR: Docker did not become ready."

    docker info 2>&1 || true

    exit 1
fi


log "Docker version:"
docker version 2>&1 || true

log "Docker containers before compose:"
docker ps -a 2>&1 || true


# ============================================================
# DOCKER COMPOSE
# ============================================================

log "========================================"
log "Starting Docker Compose"
log "========================================"

log "Running: docker compose up -d"

docker compose up -d

log "docker compose up -d completed successfully."


log "Docker Compose status:"

docker compose ps


log "All Docker containers:"

docker ps -a


# ============================================================
# APPLICATION LOGS
# ============================================================

log "========================================"
log "Initial application logs"
log "========================================"

docker compose logs --tail=100 || true


# ============================================================
# WAIT FOR LOCAL SERVICES
# ============================================================

BACKEND_LOCAL_URL="http://127.0.0.1:8000"
FRONTEND_LOCAL_URL="http://127.0.0.1:5173"

log "Backend local URL: ${BACKEND_LOCAL_URL}"
log "Frontend local URL: ${FRONTEND_LOCAL_URL}"


wait_for_local_http() {
    local name="$1"
    local url="$2"
    local attempts="${3:-60}"

    log "Waiting for ${name}: ${url}"

    for attempt in $(seq 1 "$attempts"); do

        if curl \
            --silent \
            --show-error \
            --location \
            --max-time 5 \
            --output /dev/null \
            "$url"
        then
            log "${name} is ready."

            return 0
        fi

        log "${name} is not ready yet (${attempt}/${attempts})"

        sleep 2
    done

    log "WARNING: ${name} did not become ready."

    log "${name} Docker logs:"

    docker compose logs \
        --tail=100 \
        2>&1 || true

    return 1
}


log "Checking backend..."

wait_for_local_http \
    "Django backend" \
    "$BACKEND_LOCAL_URL" \
    60 || true


log "Checking frontend..."

wait_for_local_http \
    "React frontend" \
    "$FRONTEND_LOCAL_URL" \
    60 || true


# ============================================================
# CODESPACE PORTS
# ============================================================

log "========================================"
log "Current Codespace ports"
log "========================================"

gh codespace ports \
    --codespace "$CODESPACE_NAME" \
    2>&1 || true


log "========================================"
log "Waiting for forwarded ports"
log "========================================"

PORTS_READY=false

for attempt in {1..30}; do

    log "Port check ${attempt}/30"

    PORTS="$(
        gh codespace ports \
            --codespace "$CODESPACE_NAME" \
            --json sourcePort,visibility 2>&1 \
        || true
    )"

    echo "$PORTS"

    HAS_8000=false
    HAS_5173=false

    if echo "$PORTS" | grep -q '"sourcePort":8000'; then
        HAS_8000=true
    fi

    if echo "$PORTS" | grep -q '"sourcePort":5173'; then
        HAS_5173=true
    fi

    if [ "$HAS_8000" = true ] &&
       [ "$HAS_5173" = true ]
    then
        log "Ports 8000 and 5173 detected."

        PORTS_READY=true

        break
    fi

    log "Required ports are not available yet."

    sleep 3
done


if [ "$PORTS_READY" = false ]; then
    log "ERROR: Ports 8000 and 5173 were not detected."

    exit 1
fi


# ============================================================
# SET PUBLIC
# ============================================================

log "========================================"
log "Setting ports to PUBLIC"
log "========================================"

log "Executing:"
log "gh codespace ports visibility 8000:public 5173:public"

gh codespace ports visibility \
    8000:public \
    5173:public \
    --codespace "$CODESPACE_NAME"


log "Port visibility command completed."


# ============================================================
# VERIFY PUBLIC VISIBILITY
# ============================================================

log "========================================"
log "Verifying port visibility"
log "========================================"

VISIBILITY_READY=false

for attempt in {1..10}; do

    log "Visibility check ${attempt}/10"

    PORTS="$(
        gh codespace ports \
            --codespace "$CODESPACE_NAME" \
            --json sourcePort,visibility
    )"

    echo "$PORTS"

    PORT_8000_PUBLIC=false
    PORT_5173_PUBLIC=false

    if echo "$PORTS" |
        grep -q '"sourcePort":8000' &&
       echo "$PORTS" |
        grep -q '"visibility":"public"'
    then
        PORT_8000_PUBLIC=true
    fi

    if echo "$PORTS" |
        grep -q '"sourcePort":5173' &&
       echo "$PORTS" |
        grep -q '"visibility":"public"'
    then
        PORT_5173_PUBLIC=true
    fi

    if [ "$PORT_8000_PUBLIC" = true ] &&
       [ "$PORT_5173_PUBLIC" = true ]
    then
        log "Both ports are PUBLIC."

        VISIBILITY_READY=true

        break
    fi

    log "Ports are not public yet."

    if [ "$attempt" -lt 10 ]; then

        sleep 3

        log "Retrying visibility..."

        gh codespace ports visibility \
            8000:public \
            5173:public \
            --codespace "$CODESPACE_NAME"
    fi
done


if [ "$VISIBILITY_READY" = false ]; then
    log "ERROR: Could not make ports public."

    exit 1
fi


# ============================================================
# FINAL STATUS
# ============================================================

log "========================================"
log "FINAL STATUS"
log "========================================"

log "Docker Compose:"

docker compose ps


log "Docker containers:"

docker ps -a


log "Recent application logs:"

docker compose logs --tail=50 || true


log "Codespace ports:"

gh codespace ports \
    --codespace "$CODESPACE_NAME"


log "Frontend:"
log "https://${CODESPACE_NAME}-5173.app.github.dev"

log "Backend:"
log "https://${CODESPACE_NAME}-8000.app.github.dev"

log "Admin:"
log "https://${CODESPACE_NAME}-8000.app.github.dev/admin/"


echo ""
echo "============================================================"
echo "START.SH COMPLETED SUCCESSFULLY"
echo "Finished: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"