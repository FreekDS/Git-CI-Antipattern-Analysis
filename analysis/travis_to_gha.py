import datetime
import json
import os
from analyzer import analyze_repo
from analyzer.Repository.GithubRepo import GithubRepo
from analyzer.utils import format_date_str, format_date
from dotenv import load_dotenv

load_dotenv()

BEFORE = False

start_date = datetime.datetime(2022, 5, 5, 12) - datetime.timedelta(days=90)
with open(f'{os.getcwd()}/travis_to_gha.json') as gha_f:
    travis_to_gha = json.loads('\n'.join(gha_f.readlines()))

opts = {
    'detect_only': False,
    'verbose': True
}

i = 1
fmt = "%d/%m/%Y %H:%M"
for repo, vals in travis_to_gha.items():

    end_d1 = format_date_str(datetime.datetime.strptime(vals[0]['end'], fmt))
    start_d1 = format_date_str(format_date(end_d1) - datetime.timedelta(days=45))

    start_d2 = format_date_str(datetime.datetime.strptime(vals[1]["start"], fmt))
    end_d2 = format_date_str(format_date(start_d2) + datetime.timedelta(days=45))

    if BEFORE:
        print("Repo", i, '(1) of', len(travis_to_gha))
        analyze_repo(GithubRepo(repo), start_date=start_d1, to_date=end_d1, create_cache=True, use_cache=True,
                     out_dir="./output/travis_to_gha_1", **opts)
    else:
        print("Repo", i, '(2) of', len(travis_to_gha))
        analyze_repo(GithubRepo(repo), start_date=start_d1, to_date=end_d2, create_cache=True, use_cache=True,
                     out_dir="./output/travis_to_gha_2", **opts)
    i += 1
