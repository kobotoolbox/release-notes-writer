# release-notes-writer
Compile release notes as a Markdown table from PR titles and descriptions

This is pre-alpha software: in effect, it's just a utility script to decrease
slightly the amount of manual work needed to publish KoboToolbox release
notes at https://community.kobotoolbox.org/tags/c/announcements/7/release-notes

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

Complete the [Setup](#setup) steps above.

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
