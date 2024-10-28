#!/bin/bash

DB_NAME="postgres"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"
LOG_FILE="/var/log/remove_old_carts.log"

psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "SELECT remove_old_carts();" >> "$LOG_FILE" 2>&1