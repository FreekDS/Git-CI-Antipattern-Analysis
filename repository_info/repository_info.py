import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

HEADER = {
    'Authorization': f'token {os.environ.get("GH_TOKEN_1")}',
    'User-Agent': 'FreekDS/git-ci-analyzer',
}


def read_repos(fn):
    with open(fn, 'r') as file:
        jo = json.loads('\n'.join(file.readlines()))
        return list(jo.keys())


def gh_request(*url_path, query=None, get_response=False):
    query = query if query else []
    if query:
        query = f"?{'&'.join(query)}"
    else:
        query = ''
    parts = '/'.join(url_path)
    response = requests.get(f"https://api.github.com/repos/{parts}{query}", headers=HEADER)
    return response if get_response else response.json()


def get_star_count(repos):
    star_count = {}
    for rt, rs in repos.items():
        star_count[rt] = list()
        for r in rs:
            resp = gh_request(r)
            star_count[rt].append(int(resp.get('stargazers_count', 0)))
    return star_count


def get_contributor_count(repos):
    contributor_count = {}
    for rt, rs in repos.items():
        contributor_count[rt] = list()
        for r in rs:
            resp = gh_request(r, 'contributors', query=['per_page=1'], get_response=True)
            last_url = resp.links.get('last', {}).get('url')
            if not last_url:
                contributor_count[rt].append(0)
                continue
            number = int(last_url.split('page=')[-1])
            contributor_count[rt].append(number)
    return contributor_count


def get_commit_count(repos):
    commit_count = {}
    for rt, rs in repos.items():
        commit_count[rt] = list()
        for r in rs:
            resp = gh_request(r, 'commits', query=['per_page=1'], get_response=True)
            last_url = resp.links.get('last', {}).get('url')
            if not last_url:
                commit_count[rt].append(0)
                continue
            number = int(last_url.split('page=')[-1])
            commit_count[rt].append(number)
    return commit_count


def get_issue_and_pr_count(repos):
    issue_count = {}
    pr_count = {}
    for rt, rs in repos.items():
        issue_count[rt] = list()
        pr_count[rt] = list()
        for r in rs:
            resp = gh_request(r, 'issues', query=['per_page=1'], get_response=True)
            last_url = resp.links.get('last', {}).get('url')
            if not last_url:
                issues = 0
            else:
                issues = int(last_url.split('page=')[-1])

            resp = gh_request(r, 'pulls', query=['per_page=1'], get_response=True)
            last_url = resp.links.get('last', {}).get('url')

            if not last_url:
                pulls_count = 0
            else:
                pulls_count = int(last_url.split('page=')[-1])
            pr_count[rt].append(pulls_count)
            issue_count[rt].append(issues - pulls_count)
    return issue_count, pr_count


repositories = {
    'gha_only': read_repos('./gha_only.json'),
    'travis_only': read_repos('./travis_only.json'),
    'travis2gha': read_repos('./travis_to_gha.json'),
    'gha2travis': read_repos('./gha_to_travis.json')
}

stars = get_star_count(repositories)
contributors = get_contributor_count(repositories)
commits = get_commit_count(repositories)
issues, pull_requests = get_issue_and_pr_count(repositories)

import matplotlib.pyplot as plt


def plot(d, p):
    plt.boxplot(d.values(), labels=d.keys(), showfliers=False)
    plt.ylabel(p)
    plt.xlabel('data class')
    plt.savefig(f"./repo-info/{p}.png")
    plt.close()


plot(stars, 'stars')
plot(contributors, 'contributors')
plot(commits, 'commits')
plot(issues, 'issues')
plot(pull_requests, 'pulls')
