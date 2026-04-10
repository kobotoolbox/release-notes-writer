# Setup

### 1. Create a virtual environment and install dependencies

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy `env.sample` to `env`, fill in your values, then source it:

```
cp env.sample env
# edit env with your values
source ./env
```

---

# release

One-shot script that runs `create-kobo-release.sh` then `create-gh-releases.py`.

### Prerequisites

Complete the [Setup](#setup) steps above.

`release.sh` will exit with a clear error if `KOBO_BASE_DIR` or `GITHUB_API_TOKEN` are not set.

### Usage:

```
./release.sh <tag>
```

**Example:**

```
./release.sh 2.026.07h
```

---

# create-kobo-release

Tags and updates `kobo-docker` and `kobo-install` for a new release.

### Prerequisites

```
source ./env   # sets KOBO_BASE_DIR
```

### Usage:

```
./create-kobo-release.sh <tag>
```

---

# create-gh-releases

Creates GitHub releases for the following KoboToolbox repositories:

- [kobo-docker](https://github.com/kobotoolbox/kobo-docker/releases) — body links to the KPI release
- [kobo-install](https://github.com/kobotoolbox/kobo-install/releases) — body links to the KPI release
- [KPI](https://github.com/kobotoolbox/kpi/releases) — body uses `CHANGELOG.md` from the `changelog/<tag>` branch, falls back to auto-generated release notes

### Prerequisites

Complete the [Setup](#setup) steps above.

### Usage:

```
python3 create-gh-releases.py <tag>
```

**Example:**

```
python3 create-gh-releases.py 2.026.07h
```

---

> **Deprecated:** `release-notes.py` is no longer maintained. Its documentation is kept below for reference.

<details>
<summary>release-notes.py (deprecated)</summary>

Generates a Markdown or CSV table of PRs merged between two tags for a given repo.

### Prerequisites

Complete the [Setup](#setup) steps above. Also requires `SOURCES_BASE_DIR` to be set in `env` (path where the target repo is `git clone`d).

### Usage:

```
python3 release-notes.py [--markdown] <repo> <previous-tag> <new-tag>
```

**Examples:**

```
python3 release-notes.py kpi 2.025.10 2.026.07h
python3 release-notes.py --markdown kpi 2.025.10 2.026.07h
```

- Without `--markdown`: outputs CSV to stdout
- With `--markdown`: outputs a Markdown table to stdout
- Warnings about missing PRs are printed to stderr

</details>
