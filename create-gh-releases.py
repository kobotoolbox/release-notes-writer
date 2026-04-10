#!/usr/bin/env python3
import os
import sys

try:
    import requests
except ImportError:
    print('ERROR: `requests` is not installed. Run: pip install requests')
    sys.exit(1)

# Usage: ./create-gh-releases.py <tag>

# Generate a token at https://github.com/settings/tokens
GITHUB_API_TOKEN = os.environ['GITHUB_API_TOKEN']

CHANGELOG_RAW_URL = (
    'https://raw.githubusercontent.com/kobotoolbox/kpi/changelog/{tag}/CHANGELOG.md'
)


REQUEST_TIMEOUT = 15  # seconds


def fetch_kpi_changelog(tag: str) -> str | None:
    """Fetch CHANGELOG.md from the changelog/<tag> branch. Returns None on failure."""
    url = CHANGELOG_RAW_URL.format(tag=tag)
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.RequestException as exc:
        print(f'WARNING: Could not fetch CHANGELOG.md ({exc})')
        return None

    if resp.status_code == 200:
        return resp.text

    return None


def run(tag: str):

    create_release_endpoint = (
        'https://api.github.com/repos/kobotoolbox/{repo}/releases'
    )
    repos = [
        'kobo-docker',
        'kobo-install',
        'kpi',
    ]

    headers = {
        'Accept': 'application/vnd.github.groot-preview+json',
        'Authorization': f'Bearer {GITHUB_API_TOKEN}',
        'X-GitHub-Api-Version': '2022-11-28'
    }

    kpi_release_link = f'https://github.com/kobotoolbox/kpi/releases/tag/{tag}'
    errors = []

    for repo in repos:
        if repo == 'kpi':
            changelog = fetch_kpi_changelog(tag)
            if changelog:
                print(f'Using CHANGELOG.md from changelog/{tag} branch for kpi')
                payload = {
                    'tag_name': tag,
                    'name': tag,
                    'body': changelog,
                    'draft': False,
                    'prerelease': False,
                    'generate_release_notes': False,
                }
            else:
                print(
                    f'CHANGELOG.md not found at changelog/{tag}, '
                    'falling back to auto-generated release notes for kpi'
                )
                payload = {
                    'tag_name': tag,
                    'name': tag,
                    'body': '',
                    'draft': False,
                    'prerelease': False,
                    'generate_release_notes': True,
                }
        else:
            payload = {
                'tag_name': tag,
                'name': tag,
                'body': f'For more information, please see {kpi_release_link}',
                'draft': False,
                'prerelease': False,
                'generate_release_notes': False,
            }

        try:
            resp = requests.post(
                create_release_endpoint.format(repo=repo),
                json=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )
        except requests.exceptions.RequestException as exc:
            msg = f'ERROR creating release for {repo}: {exc}'
            print(msg)
            errors.append(msg)
            continue

        if resp.status_code != 201:
            msg = f'ERROR creating release for {repo} (HTTP {resp.status_code}): {resp.text}'
            print(msg)
            errors.append(msg)
            continue

        print(f'GH release for {repo} created successfully')

    if errors:
        sys.exit(1)


if __name__ == '__main__':
    try:
        tag_ = sys.argv[1]
    except IndexError:
        print('Usage: ./create-gh-releases.py <tag>')
        sys.exit(1)

    try:
        GITHUB_API_TOKEN = os.environ['GITHUB_API_TOKEN']
    except KeyError:
        print('`GITHUB_API_TOKEN` is missing, run `source ./env` first!')
        sys.exit(1)

    run(tag_)
