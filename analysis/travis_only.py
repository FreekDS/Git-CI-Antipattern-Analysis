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
with open(f'{os.getcwd()}/travis_only.json') as gha_f:
    travis_only = json.loads('\n'.join(gha_f.readlines()))

opts = {
    'detect_only': False,
    'use_cache': True,
    'create_cache': True,
    'out_dir': "./output/travis_only",
    'verbose': True,
    'start_date': format_date_str(start_date),
    'to_date': format_date_str(until)
}

i = 1

for repo in list(travis_only.keys()):
    print("Repo", i, 'of', len(travis_only))
    i += 1
    res = analyze_repo(GithubRepo(repo), **opts)
    if "Github Actions" in res[0]:
        print("Dataset is outdated :'(")
