#!/usr/bin/env bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)

echo "SCRIPT_DIR: ${SCRIPT_DIR}"

echo "Activating venv"
source ${SCRIPT_DIR}/venv/bin/activate
echo "Launching Alarm Clock Pi"
pushd ${SCRIPT_DIR}
python3 ./acp.py
popd