import datetime
import json
import os
from analyzer import analyze_repo
from analyzer.Repository.GithubRepo import GithubRepo
from analyzer.utils import format_date_str
from dotenv import load_dotenv

load_dotenv()

# Latest commit in entire dataset: 2021-07-07 12:00:00

until = datetime.datetime(2021, 7, 7, 12, 0, 0)
start_date = until - datetime.timedelta(days=90)
with open(f'{os.getcwd()}/gha_only.json') as gha_f:
    gha_only = json.loads('\n'.join(gha_f.readlines()))

opts = {
    'detect_only': False,
    'use_cache': True,
    'create_cache': True,
    'out_dir': "./output/gha_only",
    'verbose': True,
    'start_date': format_date_str(start_date),
    'to_date': format_date_str(until)
}

i = 1

for repo in list(gha_only.keys()):
    print("Repo", i, 'of', len(gha_only))
    i += 1
    analyze_repo(GithubRepo(repo), **opts)
