from collections import defaultdict
from analyzer.utils import merge_dicts, format_date
from analyzer.AntiPatterns.SlowBuild import SlowBuild


# WHAT TO INVESTIGATE:
# TODO: get total build count somewhere? required for percentage of MEDIUM/HIGH classifications (requires rerun)

# => Scatter plots
#   Slow build:
#   ! slow build is already avg of 1 week
#       - avg
#           * total avg from all workflows combined? First avg workflows, then combine in larger average?
#       - trend
#           * increasing or decreasing for each workflow
#           * percentage of increasing/decreasing workflows per repository?
#       - # classifications (MEDIUM, HIGH) per workflow/per repo (avg?)

#   Broken release
#       - % of broken releases among all workflows
#       - % of repositories with broken releases

# Late merging
#   just give the warnings/averages

def percent(c, t):
    return f"{round(c / float(t) * 100, 2)}%"


def linreg(X, Y):
    """
        return a,b in solution to y = ax + b such that root-mean-square distance between trend line and original points
        is minimized
        https://stackoverflow.com/questions/10048571/python-finding-a-trend-in-a-set-of-numbers
    """
    N = len(X)
    Sx = Sy = Sxx = Syy = Sxy = 0.0
    for x, y in zip(X, Y):
        Sx = Sx + x
        Sy = Sy + y
        Sxx = Sxx + x * x
        Syy = Syy + y * y
        Sxy = Sxy + x * y
    det = Sxx * N - Sx * Sx
    return (Sxy * N - Sy * Sx) / det, (Sxx * Sy - Sx * Sxy) / det


def get_ci_wf_count(ad, tool=None):
    """Get the amount of workflows in the dataset"""
    c = 0
    for _slug, aps in ad.items():
        slow_b_c = aps.get('slow_build', {})
        if tool:
            slow_b_c = {k: v for k, v in slow_b_c.items() if v.get('tool') != tool}

        c += len(slow_b_c.keys())
    return c


def get_repo_count(ad):
    """Get the amount of repositories in the dataset"""
    return len(ad.keys())


def slow_build(ad, tool=None):
    slow_build_trends = defaultdict(dict)
    slow_build_avgs = defaultdict(dict)

    # Workflows or repos that have no data close to the data collection date
    not_run_wfs = list()
    not_run_repo = list()

    increasing_trend = list()
    decreasing_trend = list()
    equal_trend = list()
    # no trend == not_run_wfs

    for slug, antipatterns in ad.items():
        if tool:
            antipatterns = remove_wfs_from_tool(antipatterns, tool)
        for ci_name, data in antipatterns.get('slow_build', {}).items():
            data = data.get('data', {})
            if not data:
                continue
            if len(data) > 1:
                trend_tuple = linreg(
                    list(range(1, len(data.values()) + 1)),
                    list(data.values())
                )
                slow_build_trends[slug][ci_name] = trend_tuple

                if trend_tuple[0] < 0:
                    decreasing_trend.append((slug, ci_name))
                elif trend_tuple[0] > 0:
                    increasing_trend.append((slug, ci_name))
                else:
                    equal_trend.append((slug, ci_name))

            else:
                # print("No trend data for ", slug, ci_name)
                slow_build_trends[slug][ci_name] = False
                not_run_wfs.append((slug, ci_name))
            av = sum(data.values()) / float(len(data.values()))
            slow_build_avgs[slug][ci_name] = av
        if len(antipatterns.get('slow_build', {})) == 0:
            slow_build_avgs[slug] = {'HasData': False}
            slow_build_trends[slug] = {'HasData': False}
            not_run_repo.append(slug)

    slow_build_trends = dict(slow_build_trends)
    slow_build_avgs = dict(slow_build_avgs)

    # REMOVE OUTLIERS
    all_vals = []
    for wf_data in slow_build_avgs.values():
        all_vals += list(wf_data.values())

    all_vals = [v for v in all_vals if v is not False]
    quartile_data = SlowBuild.get_quartiles(all_vals)

    new_slow_build_avgs = dict()
    outlier_count = 0
    for slug, wf_data in slow_build_avgs.items():
        new_slow_build_avgs[slug] = dict()
        for ci, val in wf_data.items():
            if val < quartile_data.get('q3') + 1.5 * quartile_data.get('iqr'):
                new_slow_build_avgs[slug][ci] = val
            else:
                outlier_count += 1
                # print(slug, ",", ci)
    print('dropped', outlier_count, 'outliers\n')
    ##

    avg_per_repo = dict()
    for slug, data in new_slow_build_avgs.items():
        avg_per_repo[slug] = sum(data.values()) / float(len(data.values())) if data else 0

    total_avg_ms = sum(avg_per_repo.values()) / float(len(avg_per_repo.values()))
    total_avg_s = round(total_avg_ms / 1000, 2)
    total_avg_min = round((total_avg_ms / 1000) / 60, 2)
    print(f"Average workflow run time for all repositories is {total_avg_ms}ms")
    print(f"which is {total_avg_s}s")
    print(f"which is {total_avg_min} min")
    print()

    wfs_count = get_ci_wf_count(ad, tool)
    decr_p = percent(len(decreasing_trend), wfs_count)
    incr_p = percent(len(increasing_trend), wfs_count)
    no_info = percent(len(not_run_wfs), wfs_count)

    print(f"{len(decreasing_trend)} of {wfs_count} workflows have a decreasing trend ({decr_p})")
    print(f"{len(increasing_trend)} of {wfs_count} workflows have a increasing trend ({incr_p})")
    print(f"{len(not_run_wfs)} of {wfs_count} only have one data point, and thus have no trend information ({no_info})")

    return avg_per_repo, slow_build_trends


def broken_release(ad, tool=None):
    broken_release_count = 0
    broken_release_cases_all = list()

    br_release_info = defaultdict(dict)

    repos_without_releases = 0

    for slug, antipatterns in ad.items():
        if tool:
            antipatterns = remove_wfs_from_tool(antipatterns, tool)
        # Broken release information
        br = 0
        br_release_info[slug] = dict()
        has_builds = False
        for ci_name, data in antipatterns.get('broken_release', {}).items():
            rbuild_count = data.get('release_build_count', 0)
            data = data.get('data', [])
            if not has_builds:
                has_builds = rbuild_count > 0
            br += len(data)
            br_release_info[slug][ci_name] = (len(data), rbuild_count)
            if data:
                broken_release_cases_all.append((slug, ci_name, len(data)))
        if not has_builds:
            repos_without_releases += 1
        if br != 0:
            broken_release_count += 1

    wfs = get_ci_wf_count(ad, tool)

    print(f"There are {len(broken_release_cases_all)} workflows with broken releases in total (total amount {wfs})")
    print(f"Percentage of broken release workflows: "
          f"{percent(len(broken_release_cases_all), wfs)}")
    print("Percentage of repositories with broken releases: "
          f"{percent(broken_release_count, get_repo_count(ad))}")

    print("There are", repos_without_releases, 'repos without release builds')

    return dict(br_release_info)


def late_merging(ad):
    results = defaultdict(dict)

    ua_c = 0
    bd_c = 0
    ma_c = 0

    for slug, antipatterns in ad.items():

        branch_count = None

        for lm_type, data in antipatterns.get('late_merging', {}).items():
            if lm_type == "build_count":
                continue
            classification = data.get('classification', {})
            cl_ma = classification.get('missed activity', {})
            cl_bd = classification.get('branch deviation', {})
            cl_ua = classification.get('unsynced activity', {})

            if not branch_count:
                branch_count = len(data.keys())
                results[slug]['branch_count'] = branch_count

            # missed activity
            if lm_type == "missed activity":
                ma = data
                a = sum(ma.values()) / float(len(ma.values()))
                ma_c += a
                results[slug]['ma_avg'] = a
                results[slug]['ma_ms'] = len(cl_ma.get('medium_severity', [])) / branch_count
                results[slug]['ma_hs'] = len(cl_ma.get('high_severity', [])) / branch_count

            # branch deviation
            if lm_type == "branch deviation":
                bd = data
                a = sum(bd.values()) / float(len(bd.values()))
                bd_c += a
                results[slug]['bd_avg'] = a
                results[slug]['bd_ms'] = len(cl_bd.get('medium_severity', [])) / branch_count
                results[slug]['bd_hs'] = len(cl_bd.get('high_severity', [])) / branch_count

            # Un-synced activity
            if lm_type == "unsynced activity":
                ua = data
                a = sum(ua.values()) / float(len(ua.values()))
                ua_c += a
                results[slug]['ua_avg'] = a
                results[slug]['ua_ms'] = len(cl_ua.get('medium_severity', [])) / branch_count
                results[slug]['ua_hs'] = len(cl_ua.get('high_severity', [])) / branch_count

    results = dict(results)
    total = len(results.keys())

    total_branch_count = 0
    for _slug, data in results.items():
        total_branch_count += data.get('branch_count')

    print(f"Average branch count: {round(total_branch_count / float(total), 2)} branches")
    print(f"Average missed activity: {round(ma_c / float(total), 2)} days")
    print(f"Average branch deviation: {round(bd_c / float(total), 2)} days")
    print(f"Average unsynced activity: {round(ua_c / float(total), 2)} days")

    return results


def remove_wfs_from_tool(ad, tool) -> dict:
    new_dict = defaultdict(dict)
    for t, td in ad.items():
        match t:
            case 'slow_build':
                new_slow_build = dict()
                for ci, ci_data in td.items():
                    if ci_data.get('tool') != tool:
                        new_slow_build[ci] = ci_data
                new_dict['slow_build'] = new_slow_build
            case 'late_merging':
                new_dict['late_merging'] = td
            case 'broken_release':
                new_broken_release = dict()
                for ci, ci_data in td.items():
                    if ci_data.get('tool') != tool:
                        new_broken_release[ci] = ci_data
                new_dict['broken_release'] = new_broken_release
            case 'skip_failing_tests':
                new_dict['skip_failing_tests'] = td

    return dict(new_dict)


def check_repo_dates(ad1, ad2):
    def get_d(ad, ci_w):
        sb = list(ad.get('slow_build', {}).get(ci_w, {}).get('data', {}).keys())[0]
        if sb:
            return format_date(sb)
        else:
            return None

    for ci in ad1.get('slow_build', {}).keys():
        if ci in ad2.get('slow_build', {}).keys():
            if len(ad2.get('slow_build').get(ci).get('data')) == 0:
                continue
            date1 = get_d(ad1, ci)
            date2 = get_d(ad2, ci)

            if date1 is None or date2 is None:
                continue

            return date1 < date2
    return False


def combine(ad1, ad2):
    new_d = dict()
    for key, val in ad1.items():
        val2 = ad2.get(key)
        if check_repo_dates(val, val2):
            new_d[key] = merge_dicts(val, val2)
        else:
            new_d[key] = merge_dicts(val2, val)
    return new_d
