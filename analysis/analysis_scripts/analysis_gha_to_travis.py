import json
import os
from analysis_funcs import *


# WHAT TO INVESTIGATE:
# TODO: get total build count somewhere? required for percentage of MEDIUM/HIGH classifications (requires rerun)
# TODO: filter out travis/gha when required

# => Scatter plots todo
#   Slow build:
#   ! slow build is already avg of 1 week
#       - avg
#           * total avg from all workflows combined? First avg workflows, then combine in larger average?
#       - trend
#           * increasing or decreasing for each workflow
#           * percentage of increasing/decreasing workflows per repository?
#       - # classifications (MEDIUM, HIGH) per workflow/per repo (avg?) todo

#   Broken release
#       - % of broken releases among all workflows
#       - % of repositories with broken releases

# Late merging
#   just give the warnings/averages todo

def percent(c, t):
    return f"{round(c / float(t) * 100, 2)}%"


def read_data(num):
    fs = os.listdir(f'./output/gha_to_travis_{num}')
    antipattern_data = dict()

    with open(f'{os.getcwd()}/gha_to_travis.json') as gha_f:
        gha_only = json.loads('\n'.join(gha_f.readlines()))

    for r in fs:
        parts = r.split('-')
        slug = parts[0] + '/' + '-'.join(parts[1:])

        if slug not in gha_only.keys():
            if slug == 'airdcpp/web-airdcpp-webui':
                del gha_only['airdcpp-web/airdcpp-webui']
            elif slug == 'enqueuer/land-enqueuer-plugin-kafka':
                del gha_only['enqueuer-land/enqueuer-plugin-kafka']
            elif slug == 'uc/cdis-guppy':
                del gha_only['uc-cdis/guppy']
            elif slug == 'xenit/eu-finder-utils':
                del gha_only['xenit-eu/finder-utils']
            elif slug == 'electrode/io-xarc-run':
                del gha_only['electrode-io/xarc-run']
            elif slug == 't/rekttt-tinchi-api':
                del gha_only['t-rekttt/tinchi-api']
            else:
                continue
        else:
            del gha_only[slug]

        with open(f'./output/gha_to_travis_{num}/{r}/anti-patterns.json') as f:
            antipatterns = json.loads('\n'.join(f.readlines()))

        antipattern_data[slug] = antipatterns
    return antipattern_data


def main_gha_to_travis():
    d = read_data(1)
    d2 = read_data(2)

    print("SLOW BUILD INFO\n============================")
    print('BEFORE===')
    sb_a1, sb_t1 = slow_build(d, tool='TravisCI')
    print('AFTER===')
    sb_a2, sb_t2 = slow_build(d2, tool='Github Actions')
    print("============================\n\n")
    print("BROKEN RELEASE INFO\n============================")
    print('BEFORE===')
    br1 = broken_release(d, tool='TravisCI')
    print('AFTER===')
    br2 = broken_release(d2, tool='Github Actions')
    print("============================\n\n")
    print("LATE MERGING INFO\n============================")
    print('BEFORE===')
    lm1 = late_merging(d)
    print('AFTER===')
    lm2 = late_merging(d2)
    print("============================")
    return sb_a1, sb_t1, sb_a2, sb_t2, br1, br2, lm1, lm2


if __name__ == '__main__':
    main_gha_to_travis()
