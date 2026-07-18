#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

COMPOSE="${COMPOSE:-docker compose}"
EXEC="${EXEC:-}"
WITH_MEDIA=0
for argument in "$@"; do
    case "$argument" in
        media | --media) WITH_MEDIA=1 ;;
    esac
done

timestamp="$(date +%Y-%m-%d_%H-%M-%S)"
directory="dumps/${timestamp}"
mkdir -p "$directory"
chmod 700 "$directory"

echo "Backing up to ${directory}"
echo "  database"
$COMPOSE exec -T db sh -c \
    'exec pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner --no-privileges' \
    | gzip >"${directory}/database.sql.gz"
gzip -t "${directory}/database.sql.gz"

if [ "$WITH_MEDIA" -eq 1 ]; then
    echo "  media files"
    media_root="$(
        $COMPOSE exec -T $EXEC backend python -c \
            'import os; os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings"); import django; django.setup(); from django.conf import settings; print(settings.MEDIA_ROOT)'
    )"
    $COMPOSE exec -T $EXEC backend tar -C "$media_root" -czf - . \
        >"${directory}/media.tar.gz"
    tar -tzf "${directory}/media.tar.gz" >/dev/null
fi

echo "Backup complete:"
du -sh "$directory"/* 2>/dev/null || true
