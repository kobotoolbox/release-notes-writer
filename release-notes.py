#!/usr/bin/env python3
import csv
import json
import os
import re
import requests
import subprocess
import sys
from collections import OrderedDict

# Usage: ./release-notes.py [repo] [previous release tag] [new release tag]

# You need to have the source code `git clone`d here
SOURCES_BASE_DIR = os.environ['SOURCES_BASE_DIR']
SOURCE_DIR = SOURCES_BASE_DIR.rstrip('/') + '/{repo}'

# Generate a token at https://github.com/settings/tokens
GITHUB_API_TOKEN = os.environ['GITHUB_API_TOKEN']

repo = sys.argv[1]
old_tag = sys.argv[2]
this_tag = sys.argv[3]
base_branch = None
#base_branch = 'master'  # consider only PRs on this branch

commit_prs_endpoint = (
    f'https://api.github.com/repos/kobotoolbox/{repo}/commits/{{commit}}/pulls'
)
headers = {'Accept': 'application/vnd.github.groot-preview+json'}
headers['Authorization'] = f'Token {GITHUB_API_TOKEN}'

substitutions = (
    # Regular expressions based on Zulip's linkifiers
    (
        r'(?P<text>(?P<org>[a-zA-Z0-9_-]+)/(?P<repo>[a-zA-Z0-9_-]+)#(?P<id>[0-9]+))',
        r'[\g<text>](https://github.com/\g<org>/\g<repo>/issues/\g<id>)',
    ),
    (
        r'(?P<text>(?P<repo>[a-zA-Z0-9_-]+)#(?P<id>[0-9]+))',
        r'[\g<text>](https://github.com/kobotoolbox/\g<repo>/issues/\g<id>)',
    ),
    (
        r'\B(?P<text>#(?P<id>[0-9]+))',
        r'[\g<text>](https://github.com/kobotoolbox/{repo}/issues/\g<id>)'.format(repo=repo),
    ),
)

commits = (
    subprocess.check_output(
        ['git', 'log', '--merges', '--pretty=format:%H', f'^{old_tag}', this_tag],
        #['git', 'log', '--pretty=format:%H', f'^{old_tag}', this_tag],
        cwd=SOURCE_DIR.format(repo=repo),
    )
    .decode('utf-8')
    .split('\n')
)

if not commits[0] and len(commits) == 1:
    sys.stderr.write('No commits were found. Bye!\n')
    sys.exit(0)

prs = OrderedDict()
for commit in commits:
    resp = requests.get(
        commit_prs_endpoint.format(commit=commit),
        headers=headers,
    )
    resp.raise_for_status()
    interesting_pr = None
    for pr in resp.json():
        if not pr['merged_at']:
            continue
        if base_branch and pr['base']['ref'] != base_branch:
            continue
        if interesting_pr:
            sys.stderr.write(f'!!! Multiple interesting PRs for {commit}\n')
            break
        interesting_pr = pr
    if interesting_pr:
        prs[pr['number']] = interesting_pr
        sys.stderr.write(f"Found PR {pr['number']} for merge {commit}\n")
    else:
        sys.stderr.write(f"!!! No PR found for merge {commit}\n")

def condense_spaces(s): return re.sub('  +', ' ', s)

def remove_outer_blanks(l):
    start = 0
    end = len(l)
    for i in l:
        if i == '' and start < end:
            start += 1
        else:
            break
    for i in reversed(l):
        if i == '' and end > start:
            end -= 1
        else:
            break
    return l[start:end]

print('| PR | Description | Related Issues |')
print('| - | - | - |')
for number, details in prs.items():
    row = []
    row.append(f"[{repo}#{number}]({details['html_url']})")
    description_lines = []
    related_issues_lines = []
    reading_state = None
    if not details['body']:
        continue
    for line in details['body'].replace('\r', '').split('\n'):
        line = line.strip()
        if line.startswith('## '):
                reading_state = None
        if reading_state is None:
            standardized_line = condense_spaces(line).lower()
            if standardized_line == '## description':
                reading_state = 'description'
            elif standardized_line == '## related issues':
                reading_state = 'related issues'
            continue
        for pattern, repl in substitutions:
            line, sub_count = re.subn(pattern, repl, line)
            if sub_count:
                # Process only the first matching pattern
                break
        if reading_state == 'description':
            description_lines.append(line)
        elif reading_state == 'related issues':
            related_issues_lines.append(line)
    description_lines = remove_outer_blanks(description_lines)
    # always include the title; see
    # https://chat.kobotoolbox.org/#narrow/stream/4-KoBo-Dev/topic/Change.20logs/near/9770
    description_lines.insert(0, details['title'])
    row.append('<br>'.join(description_lines))
    row.append('<br>'.join(remove_outer_blanks(related_issues_lines)))
    print('|', ' | '.join(row), '|')

#import IPython; IPython.embed()
