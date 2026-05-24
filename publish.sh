#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR" || exit

python -m pip install --upgrade build twine
rm -rf dist
python -m build
python -m twine upload dist/* --verbose
