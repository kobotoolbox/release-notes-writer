#!/usr/bin/env bash
set -euo pipefail

# --- Config & validation ------------------------------------------------------
VERSION="${1:-}"
BASE_DIR="${KOBO_BASE_DIR:-}"
KDOCKER="${BASE_DIR}/kobo-docker"
KINSTALL="${BASE_DIR}/kobo-install"
CONFIG_FILE="${KINSTALL}/helpers/config.py"


if [[ -z "${BASE_DIR}" ]]; then
  echo "ERROR: environment variable KOBO_BASE_DIR is not set."
  echo "Please export it first, e.g.:"
  echo "  export KOBO_BASE_DIR=/path/to/kobo"
  exit 1
fi


# Version must look like 2.0DD.DD or 2.0DD.DD<letter>
if [[ -z "${VERSION}" ]]; then
  echo "Usage: $0 <version> [base_dir]"
  exit 1
fi
if ! [[ "${VERSION}" =~ ^2\.0[0-9]{2}\.[0-9]{2}[a-z]?$ ]]; then
  echo "ERROR: version '${VERSION}' does not match ^2\\.0\\d{2}\\.\\d{2}[a-z]?\$"
  exit 1
fi

# --- Helpers ------------------------------------------------------------------
require_clean_worktree() {
  # Ignore untracked files (like -uno) but fail on staged/unstaged changes
  if [[ -n "$(git status --porcelain -uno)" ]]; then
    echo "ERROR: Dirty worktree in $(pwd). Commit/stash changes first."
    git status -sb
    exit 1
  fi
}

ensure_repo_exists() {
  if [[ ! -d "$1/.git" ]]; then
    echo "ERROR: '$1' is not a git repository."
    exit 1
  fi
}

checkout_branch() {
  local branch="$1"
  # Ensure branch exists locally or remotely
  if git rev-parse --verify "$branch" >/dev/null 2>&1; then
    git checkout "$branch" >/dev/null
  else
    # Try track remote branch if exists, else create from current HEAD
    if git ls-remote --exit-code --heads origin "$branch" >/dev/null 2>&1; then
      git checkout -t "origin/${branch}" >/dev/null
    else
      git checkout -b "$branch" >/dev/null
    fi
  fi
}

tag_exists_remote() {
  local tag="$1"
  git ls-remote --exit-code --tags origin "refs/tags/${tag}" >/dev/null 2>&1
}

tag_exists_local() {
  local tag="$1"
  git rev-parse -q --verify "refs/tags/${tag}" >/dev/null 2>&1
}

annotated_tag() {
  local tag="$1"
  local msg="$2"
  if tag_exists_local "${tag}"; then
    echo "Tag ${tag} already exists locally. Skipping tag creation."
  else
    git tag -a "${tag}" -m "${msg}"
  fi
}

# --- 1) kobo-docker: checkout master, pull, tag & push tag --------------------
echo "==> Processing kobo-docker (${KDOCKER})"
ensure_repo_exists "${KDOCKER}"
cd "${KDOCKER}"

require_clean_worktree
checkout_branch master
git pull --ff-only origin master

if tag_exists_remote "${VERSION}"; then
  echo "Tag ${VERSION} already exists on origin for kobo-docker. Skipping push."
else
  annotated_tag "${VERSION}" "Release ${VERSION}"
  git push origin "refs/tags/${VERSION}"
fi

# --- 2) kobo-install: update config, commit, tag, push commit & tag ----------
echo "==> Processing kobo-install (${KINSTALL})"
ensure_repo_exists "${KINSTALL}"
cd "${KINSTALL}"

# require_clean_worktree
checkout_branch master
git pull --ff-only origin master

if [[ ! -f "${CONFIG_FILE}" ]]; then
  echo "ERROR: ${CONFIG_FILE} not found."
  exit 1
fi

# Read previous value and replace it with new VERSION using Python for portability
echo "Updating KOBO_DOCKER_BRANCH in ${CONFIG_FILE} to '${VERSION}'"
sed -i '' -E "s/^( *KOBO_DOCKER_BRANCH *= *')[^']*('.*)/\1${VERSION}\2/" "${CONFIG_FILE}"

# Stage & commit
git add "${CONFIG_FILE}"
git commit -m "Use release ${VERSION} of kobo-docker"

# Tag & push (commit + tag)
if tag_exists_remote "${VERSION}"; then
  echo "Tag ${VERSION} already exists on origin for kobo-install. Skipping tag push."
else
  annotated_tag "${VERSION}" "Release ${VERSION}"
fi
git push origin master --tags

# --- 3) Merge master -> local in both repos, no push --------------------------
merge_master_into_local() {
  local repo_dir="$1"
  echo "Merging master -> local in ${repo_dir} (no push)"
  cd "${repo_dir}"
  require_clean_worktree
  checkout_branch local
  # Merge without creating a fast-forward to keep a record; adjust if you prefer ff
  git merge --no-ff master -m "Merge master into local after release ${VERSION}" || {
    echo "Merge conflict in ${repo_dir}. Resolve manually."
    exit 1
  }
  echo "Merge done for ${repo_dir}. (NOT pushed)"
}

merge_master_into_local "${KDOCKER}"
merge_master_into_local "${KINSTALL}"

echo "✅ All done."
echo "   - Tags pushed:"
echo "       kobo-docker: ${VERSION}"
echo "       kobo-install: ${VERSION} + commit (config updated)"
echo "   - Merged master → local in both repos (no push performed)"

