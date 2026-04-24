#!/bin/sh
set -eu

APP_DIR="/app"
DATA_DIR="${DATA_DIR:-/data}"
SQLITE_PATH="${SQLITE_PATH:-$DATA_DIR/db.sqlite3}"
MEDIA_ROOT="${MEDIA_ROOT:-$DATA_DIR/media}"
BUNDLED_MEDIA_ROOT="${BUNDLED_MEDIA_ROOT:-$APP_DIR/media}"

mkdir -p "$DATA_DIR" "$(dirname "$SQLITE_PATH")" "$MEDIA_ROOT"

if [ -d "$BUNDLED_MEDIA_ROOT" ]; then
  echo "Syncing bundled media into persistent media volume..."
  cp -an "$BUNDLED_MEDIA_ROOT"/. "$MEDIA_ROOT"/
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ "${DJANGO_LOAD_SAMPLE_DATA:-1}" = "1" ]; then
  if ! python manage.py shell -c "from pastpaper.models import Subject; raise SystemExit(0 if Subject.objects.exists() else 1)"; then
    echo "Loading initial sample data..."
    python populate_data_v2.py
  fi
fi

if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  echo "Ensuring Django superuser exists..."
  python manage.py shell <<'PY'
import os

from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ["DJANGO_SUPERUSER_USERNAME"]
password = os.environ["DJANGO_SUPERUSER_PASSWORD"]
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")

user, created = User.objects.get_or_create(
    username=username,
    defaults={
        "email": email,
        "is_staff": True,
        "is_superuser": True,
    },
)

dirty = created
if email and user.email != email:
    user.email = email
    dirty = True
if not user.is_staff:
    user.is_staff = True
    dirty = True
if not user.is_superuser:
    user.is_superuser = True
    dirty = True
if created or not user.check_password(password):
    user.set_password(password)
    dirty = True

if dirty:
    user.save()
PY
fi

exec "$@"
