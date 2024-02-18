#!/bin/bash
# date=$(date '+%Y-%m-%d')
PGPASSWORD="" pg_dump --host 127.0.0.1 --port 5432 -U postgres --format custom --blobs --verbose --file "DB_backup_.bck" hackbu24



