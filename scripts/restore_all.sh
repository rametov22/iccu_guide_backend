#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

COMPOSE="${COMPOSE:-docker compose}"
EXEC="${EXEC:-}"
directory="${1:-}"

if [ -z "$directory" ] || [ ! -d "$directory" ]; then
    echo "Usage: ./scripts/restore_all.sh dumps/<timestamp>" >&2
    exit 1
fi
if [ ! -f "$directory/database.sql.gz" ]; then
    echo "Error: ${directory}/database.sql.gz is missing." >&2
    exit 1
fi

gzip -t "$directory/database.sql.gz"
if [ -f "$directory/media.tar.gz" ]; then
    tar -tzf "$directory/media.tar.gz" >/dev/null
fi

echo "Restoring from ${directory}"
echo "  database"
gunzip -c "$directory/database.sql.gz" \
    | $COMPOSE exec -T db sh -c \
        'exec psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -q -v ON_ERROR_STOP=1'

echo "  migrations"
$COMPOSE exec -T $EXEC backend python manage.py migrate --no-input

if [ -f "$directory/media.tar.gz" ]; then
    echo "  media files"
    media_root="$(
        $COMPOSE exec -T $EXEC backend python -c \
            'import os; os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings"); import django; django.setup(); from django.conf import settings; print(settings.MEDIA_ROOT)'
    )"
    $COMPOSE exec -T $EXEC backend sh -c \
        'find "$1" -mindepth 1 -delete && tar -C "$1" -xzf -' \
        sh "$media_root" <"$directory/media.tar.gz"
fi

echo "  static files"
$COMPOSE exec -T $EXEC backend python manage.py collectstatic --no-input

echo "Restore complete."
