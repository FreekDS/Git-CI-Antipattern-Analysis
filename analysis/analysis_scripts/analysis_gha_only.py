import json
import os
from analysis_funcs import *


# WHAT TO INVESTIGATE:
# TODO: get total build count somewhere? required for percentage of MEDIUM/HIGH classifications (requires rerun)
# TODO: pick examples with lots of datapoints and create graphics for them (concrete examples)
# TODO: add linear regression line to indicate the trend in those graphics :)

# => Scatter plots
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

# def percent(c, t):
#     return f"{round(c / float(t) * 100, 2)}%"


def read_data():
    fs = os.listdir('./output/gha_only')
    antipattern_data = dict()

    with open(f'{os.getcwd()}/gha_only.json') as gha_f:
        gha_only = json.loads('\n'.join(gha_f.readlines()))

    for r in fs:
        parts = r.split('-')
        slug = parts[0] + '/' + '-'.join(parts[1:])

        if slug not in gha_only.keys():
            if slug == 'react/native-picker-picker':
                del gha_only['react-native-picker/picker']
            elif slug == 'sumup/oss-foundry':
                del gha_only['sumup-oss/foundry']
            else:
                continue
        else:
            del gha_only[slug]

        with open(f'./output/gha_only/{r}/anti-patterns.json') as f:
            antipatterns = json.loads('\n'.join(f.readlines()))

        antipattern_data[slug] = antipatterns
    return antipattern_data


def main_gha_only():
    d = read_data()
    print("SLOW BUILD INFO\n============================")
    sb_a, sb_t = slow_build(d, tool='TravisCI')
    print("============================\n\n")
    print("BROKEN RELEASE INFO\n============================")
    br = broken_release(d, tool='TravisCI')
    print("============================\n\n")
    print("LATE MERGING INFO\n============================")
    lm = late_merging(d)
    print("============================")
    return sb_a, sb_t, br, lm


if __name__ == '__main__':
    main_gha_only()
