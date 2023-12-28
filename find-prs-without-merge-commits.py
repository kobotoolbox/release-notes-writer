#!/usr/bin/env python3
import os
import pickle
import requests
import sys
import time


# Generate a token at https://github.com/settings/tokens
GITHUB_API_TOKEN = os.environ['GITHUB_API_TOKEN']

repo = sys.argv[1]

prs_endpoint = f'https://api.github.com/repos/kobotoolbox/{repo}/pulls?state=closed&per_page=10&page={{page}}'
commit_endpoint = (
    f'https://api.github.com/repos/kobotoolbox/{repo}/commits/{{commit}}'
)
headers = {'Accept': 'application/vnd.github.groot-preview+json'}
headers['Authorization'] = f'Token {GITHUB_API_TOKEN}'


def fun_out(file_like, out):
    out_len = len(out)
    if fun_out.last_len > out_len:
        out += ' ' * (fun_out.last_len - out_len)
    fun_out.last_len = out_len
    file_like.write('\r' + out)


fun_out.last_len = 0

try:
    with open('benign_prs', 'rb') as f:
        all_benign_prs = pickle.load(f)
except FileNotFoundError:
    all_benign_prs = {}

benign_prs = all_benign_prs.setdefault(repo, [])

page = 1
while True:
    resp = requests.get(
        prs_endpoint.format(page=page),
        headers=headers,
    )
    resp.raise_for_status()
    prs = resp.json()
    if not prs:
        sys.stderr.write('No more PRs!')
        break

    for pr in prs:
        out = f"{pr['number']} {pr['title']}"
        fun_out(sys.stderr, out)
        if not pr['merged_at']:
            continue
        if pr['number'] in benign_prs:
            continue

        resp = requests.get(
            commit_endpoint.format(commit=pr['merge_commit_sha']),
            headers=headers,
        )
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            if resp.status_code == 422:
                fun_out(
                    sys.stdout,
                    f"!! (merge commit has vanished?) {pr['number']} {pr['title']}\n",
                )
                continue

        commit = resp.json()
        if len(commit['parents']) < 2:
            fun_out(sys.stdout, f"!! {pr['number']} {pr['title']}\n")
        else:
            benign_prs.append(pr['number'])

        time.sleep(0.25)

    page += 1
    with open('benign_prs', 'wb') as f:
        pickle.dump(all_benign_prs, f)
