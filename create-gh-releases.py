#!/usr/bin/env python3
import os
import sys

import requests

# Usage: ./create-gh-releases.py [tag]

# Generate a token at https://github.com/settings/tokens
GITHUB_API_TOKEN = os.environ['GITHUB_API_TOKEN']


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

    # Generate the release notes link automatically
    release_notes_link = f'https://github.com/kobotoolbox/kpi/releases/tag/{tag}'

    for repo in repos:
        # For KPI repo: auto-generate changelog, no custom body
        if repo == 'kpi':
            body = ''
            generate_releases_notes = True
        else:
            body = f'For more information, please see {release_notes_link}',
            generate_releases_notes = False

        payload = {
            'tag_name': tag,
            'name': tag,
            'body': '',  # Empty body
            'draft': False,
            'prerelease': False,
            'generate_release_notes': True  # Auto-generate for KPI
        }

        resp = requests.post(
            create_release_endpoint.format(repo=repo),
            json=payload,
            headers=headers,
        )
        if resp.status_code != 201:
            print(resp.text)
        else:
            print(f'GH release for {repo} is created')


if __name__ == '__main__':
    try:
        tag_ = sys.argv[1]
    except IndexError:
        print('Usage: ./create-gh-releases.py [tag]')
        sys.exit(1)

    try:
        GITHUB_API_TOKEN = os.environ['GITHUB_API_TOKEN']
    except KeyError:
        print('`GITHUB_API_TOKEN` is missing, run `source ./env` first!')
        sys.exit(1)

    run(tag_)
