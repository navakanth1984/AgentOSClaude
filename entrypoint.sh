#!/bin/sh
set -e

# Download models dynamically if the models directory is empty
if [ ! -d "/app/models" ] || [ -z "$(ls -A /app/models 2>/dev/null)" ]; then
    echo "Models directory is empty. Downloading weights..."
    python download_models.py
else
    echo "Model weights found. Skipping download."
fi

# Execute CLI wrapper or launch API
if [ "$1" = "qualify" ]; then
    shift
    exec python -m agent_os.cli qualify "$@"
elif [ "$1" = "doctor" ]; then
    shift
    exec python -m agent_os.cli doctor "$@"
elif [ "$1" = "cli" ]; then
    shift
    exec python -m agent_os.cli "$@"
else
    exec "$@"
fi
