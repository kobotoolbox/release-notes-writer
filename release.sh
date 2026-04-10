#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Validate env vars --------------------------------------------------------
missing=()
[[ -z "${KOBO_BASE_DIR:-}" ]] && missing+=('KOBO_BASE_DIR')
[[ -z "${GITHUB_API_TOKEN:-}" ]] && missing+=('GITHUB_API_TOKEN')

if [[ ${#missing[@]} -gt 0 ]]; then
  echo "ERROR: The following environment variables are not set:"
  for var in "${missing[@]}"; do
    echo "  - ${var}"
  done
  echo ""
  echo "Run 'source ${SCRIPT_DIR}/env' first (copy env.sample if you don't have one)."
  exit 1
fi

# --- Validate argument --------------------------------------------------------
VERSION="${1:-}"

if [[ -z "${VERSION}" ]]; then
  echo "Usage: $0 <version>"
  echo "Example: $0 2.026.07h"
  exit 1
fi

# --- Run steps ----------------------------------------------------------------
echo "==> Step 1: Tagging and updating kobo-docker & kobo-install"
bash "${SCRIPT_DIR}/create-kobo-release.sh" "${VERSION}"

echo ""
echo "==> Step 2: Creating GitHub releases"
python3 "${SCRIPT_DIR}/create-gh-releases.py" "${VERSION}"
