#!/bin/bash
echo "Sourcing environment variables from creds.env..."

if [ -f /app/creds.env ]; then
    set -o allexport
    source /app/creds.env
    set +o allexport
    echo "Environment variables loaded!"
else
    echo "creds.env file not found!"
fi

exec "$@"
