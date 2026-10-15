#!/usr/bin/env bash
# ==============================================================================
# MeetFlow Platform - AWS EC2 Automated Deployment Script
# ==============================================================================
# This script is executed on the target AWS EC2 instance by the CI/CD pipeline.
# It safely pulls latest changes, updates dependencies, runs migrations,
# collects static files, reloads process daemons, and verifies health.
# ==============================================================================

set -euo pipefail

# Configuration defaults (overrideable via environment variables)
DEPLOY_DIR="${TARGET_DIR:-/home/ubuntu/meeting-room}"
BRANCH="${TARGET_BRANCH:-main}"
VENV_PATH="${VENV_PATH:-${DEPLOY_DIR}/venv}"
DAPHNE_SERVICE="${DAPHNE_SERVICE:-daphne}"
CELERY_SERVICE="${CELERY_SERVICE:-celery}"
NGINX_SERVICE="${NGINX_SERVICE:-nginx}"
HEALTH_CHECK_URL="${HEALTH_CHECK_URL:-http://127.0.0.1:8000/test-auth/}"

echo "===================================================================="
echo "🚀 Starting MeetFlow Deployment on AWS EC2"
echo "Timestamp : $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "Target Dir: ${DEPLOY_DIR}"
echo "Branch    : ${BRANCH}"
echo "===================================================================="

# 1. Verify Deployment Directory Exists
if [ ! -d "${DEPLOY_DIR}" ]; then
  echo "❌ Error: Target deployment directory '${DEPLOY_DIR}' does not exist."
  exit 1
fi

cd "${DEPLOY_DIR}"

# 2. Update Code from Production Branch
echo "📥 Fetching latest commits from origin/${BRANCH}..."
git fetch origin "${BRANCH}"
git checkout "${BRANCH}"
git pull origin "${BRANCH}"

# 3. Ensure Python Virtual Environment
if [ ! -d "${VENV_PATH}" ]; then
  echo "⚙️ Creating virtual environment at '${VENV_PATH}'..."
  python3 -m venv "${VENV_PATH}"
fi

echo "🐍 Activating Python virtual environment..."
# shellcheck source=/dev/null
source "${VENV_PATH}/bin/activate"

# 4. Install / Upgrade Dependencies
echo "📦 Installing production dependencies from requirements.txt..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 5. Execute Database Migrations
echo "🗄️ Running database migrations..."
python src/manage.py migrate --noinput

# 6. Collect Static Files for Production / WhiteNoise
echo "🎨 Collecting static assets..."
python src/manage.py collectstatic --noinput

# 7. Restart or Reload Application Services
echo "🔄 Reloading application process managers..."

# Restart Daphne / ASGI service
if systemctl is-active --quiet "${DAPHNE_SERVICE}" 2>/dev/null; then
  echo "Restarting ${DAPHNE_SERVICE} systemd service..."
  sudo systemctl restart "${DAPHNE_SERVICE}"
elif systemctl is-active --quiet meetflow 2>/dev/null; then
  echo "Restarting meetflow systemd service..."
  sudo systemctl restart meetflow
elif systemctl is-active --quiet gunicorn 2>/dev/null; then
  echo "Restarting gunicorn systemd service..."
  sudo systemctl restart gunicorn
else
  echo "⚠️ Warning: No recognized systemd service (${DAPHNE_SERVICE}/meetflow/gunicorn) is currently active."
  echo "   If using a custom service name, set DAPHNE_SERVICE in GitHub environment variables."
fi

# Restart Celery if present
if systemctl is-active --quiet "${CELERY_SERVICE}" 2>/dev/null; then
  echo "Restarting ${CELERY_SERVICE} worker service..."
  sudo systemctl restart "${CELERY_SERVICE}"
fi

# Reload Nginx if present
if systemctl is-active --quiet "${NGINX_SERVICE}" 2>/dev/null; then
  echo "Testing and reloading ${NGINX_SERVICE}..."
  sudo nginx -t && sudo systemctl reload "${NGINX_SERVICE}"
fi

# 8. Post-Deployment Verification Health Check
echo "🔍 Performing deployment health check against ${HEALTH_CHECK_URL}..."
sleep 3

MAX_RETRIES=10
RETRY_COUNT=0
HEALTHY=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${HEALTH_CHECK_URL}" || true)
  if [ "${HTTP_STATUS}" = "200" ] || [ "${HTTP_STATUS}" = "302" ]; then
    HEALTHY=true
    echo "✅ Health check PASSED with HTTP status ${HTTP_STATUS}!"
    break
  else
    echo "⏳ Attempt $((RETRY_COUNT + 1))/$MAX_RETRIES: Received HTTP ${HTTP_STATUS}, retrying in 2s..."
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
  fi
done

if [ "$HEALTHY" = false ]; then
  echo "❌ Error: Deployment health check failed after ${MAX_RETRIES} attempts."
  echo "Check systemd service logs: sudo journalctl -u ${DAPHNE_SERVICE} -n 50 --no-pager"
  exit 1
fi

echo "===================================================================="
echo "🎉 MeetFlow Deployment Completed Successfully!"
echo "Timestamp : $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "===================================================================="
