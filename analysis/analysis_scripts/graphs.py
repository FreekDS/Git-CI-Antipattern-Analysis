import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import numpy as np
from analysis_gha_only import main_gha_only
from analysis_travis_only import main_travis_only
from analysis_gha_to_travis import main_gha_to_travis
from analysis_travis_to_gha import main_travis_to_gha


def workflow_counts():
    N = 4

    travisci = [0, 26, 4, 18]
    githubactions = [54, 0, 22, 42]

    ind = np.arange(N)
    width = 0.35

    fig, ax = plt.subplots()
    p1 = ax.bar(ind, travisci, width, label="TravisCI")
    p2 = ax.bar(ind, githubactions, width, bottom=travisci, label="Github Actions")
    ax.set_ylabel("Workflow count")
    ax.set_xlabel("Data class")
    ax.set_title("Workflow with builds per CI tool")
    ax.set_xticks(ind, labels=["GHA", "TravisCI", "GHA -> TravisCI", "TravisCI -> GHA"])
    ax.legend()

    lbls = [v if v > 0 else "" for v in p1.datavalues]
    ax.bar_label(p1, labels=lbls, label_type='center')

    lbls = [v if v > 0 else "" for v in p2.datavalues]
    ax.bar_label(p2, labels=lbls, label_type='center')
    ax.bar_label(p2)

    plt.savefig("graphs/workflow_counts.png")
    plt.close()


def slow_builds_dist1(gho, tcio):
    gho_a, gho_t = gho[0:2]
    tcio_a, tcio_t = tcio[0:2]

    # Convert ms to seconds
    gho_a = [v / 1000 for v in gho_a.values()]
    tcio_a = [v / 1000 for v in tcio_a.values()]

    plt.boxplot([gho_a, tcio_a], showfliers=False, labels=["GHA", "TravisCI"], showmeans=True)
    plt.ylabel("Avg build time (s)")
    plt.xlabel("Data class")
    plt.title("Average build duration (s) per repository (without outliers)")
    plt.suptitle("GHA only / TravisCI only")
    plt.savefig("./graphs/sb/one_ci_no.png")
    plt.close()

    # TODO: add values to graph (search google)

    plt.boxplot([gho_a, tcio_a], showfliers=True, labels=["GHA", "TravisCI"], showmeans=True)
    plt.ylabel("Avg build time (s)")
    plt.xlabel("Data class")
    plt.title("Average build duration (s) per repository (with outliers)")
    plt.suptitle("GHA only / TravisCI only")
    plt.savefig("./graphs/sb/one_ci_wo_lin.png")
    plt.close()

    plt.boxplot([gho_a, tcio_a], showfliers=True, labels=["GHA", "TravisCI"], showmeans=True)
    plt.ylabel("Avg build time (s)")
    plt.yscale("symlog")
    plt.gca().set_ylim([-.5, None])
    plt.gca().yaxis.set_major_formatter(ScalarFormatter())
    plt.xlabel("Data class")
    plt.title("Average build duration (s) per repository (with outliers)")
    plt.suptitle("GHA only / TravisCI only")
    plt.savefig("./graphs/sb/one_ci_wo_log.png")
    plt.close()

    # bins = np.linspace(min(gho_a + tcio_a), 1000, 100)
    # plt.hist(gho_a, bins, alpha=0.5, label="Github Actions")
    # plt.hist(tcio_a, bins, alpha=0.5, label="TravisCI")
    # plt.legend()
    # plt.show()


def _prepare_box_plts(data, ylabel, xlabel, labels, title, suptitle, showfliers=True, log=False, miny=-.2):
    bplt = plt.boxplot(data, showfliers=showfliers, labels=labels, showmeans=False)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.title(title)
    if showfliers and log:
        plt.yscale("symlog")
        plt.gca().set_ylim([miny, None])
        plt.gca().yaxis.set_major_formatter(ScalarFormatter())
    plt.suptitle(suptitle)
    return bplt


def slow_builds_dist2(t2g, g2t):
    t2g_sb_a1, t2g_sb_t1, t2g_sb_a2, t2g_sb_t2 = t2g[0:4]
    g2t_sb_a1, g2t_sb_t1, g2t_sb_a2, g2t_sb_t2 = g2t[0:4]
    t2g_sb_a1 = [v / 1000 for v in t2g_sb_a1.values()]
    t2g_sb_a2 = [v / 1000 for v in t2g_sb_a2.values()]
    g2t_sb_a1 = [v / 1000 for v in g2t_sb_a1.values()]
    g2t_sb_a2 = [v / 1000 for v in g2t_sb_a2.values()]

    # Before comparison

    kwargs = {
        'data': [g2t_sb_a1, t2g_sb_a1],
        'ylabel': "Avg build time (s)",
        'xlabel': "Data class",
        'labels': ["GHA -> TravisCI", "TravisCI -> GHA"],
        'suptitle': "GHA -> TravisCI / TravisCI -> GHA (before change)"
    }

    _prepare_box_plts(**kwargs, title="Average build duration (s) per repository (without outliers)", showfliers=False)
    plt.savefig("./graphs/sb/before_no.png")
    plt.close()
    _prepare_box_plts(**kwargs, title="Average build duration (s) per repository (with outliers)", showfliers=True)
    plt.savefig("./graphs/sb/before_wo_lin.png")
    plt.close()
    _prepare_box_plts(**kwargs, title="Average build duration (s) per repository (with outliers)", showfliers=True,
                      log=True)
    plt.savefig("./graphs/sb/before_wo_log.png")
    plt.close()

    # After comparison
    kwargs['data'] = [g2t_sb_a2, t2g_sb_a2]
    kwargs['suptitle'] = "GHA -> TravisCI / TravisCI -> GHA (after change)"
    _prepare_box_plts(**kwargs, title="Average build duration (s) per repository (without outliers)", showfliers=False)
    plt.savefig("./graphs/sb/after_no.png")
    plt.close()
    _prepare_box_plts(**kwargs, title="Average build duration (s) per repository (with outliers)", showfliers=True)
    plt.savefig("./graphs/sb/after_wo_lin.png")
    plt.close()
    _prepare_box_plts(**kwargs, title="Average build duration (s) per repository (with outliers)", showfliers=True,
                      log=True)
    plt.savefig("./graphs/sb/after_wo_log.png")
    plt.close()

    # Combined comparison
    kwargs['data'] = [g2t_sb_a1 + g2t_sb_a2, t2g_sb_a1 + t2g_sb_a2]
    kwargs['suptitle'] = "GHA -> TravisCI / TravisCI -> GHA (total)"
    _prepare_box_plts(**kwargs, title="Average build duration (s) per repository (without outliers)", showfliers=False)
    plt.savefig("./graphs/sb/combined_no.png")
    plt.close()
    _prepare_box_plts(**kwargs, title="Average build duration (s) per repository (with outliers)", showfliers=True)
    plt.savefig("./graphs/sb/combined_wo_lin.png")
    plt.close()
    _prepare_box_plts(**kwargs, title="Average build duration (s) per repository (with outliers)", showfliers=True,
                      log=True)
    plt.savefig("./graphs/sb/combined_wo_log.png")
    plt.close()

    # BEFORE VS AFTER GRAPHS :)

    kwargs = {
        'ylabel': 'Average build duration (s)',
        'xlabel': '',
        'labels': ['Before', 'After'],
        'title': 'TravisCI -> GHA',
        'suptitle': 'Average build duration (s) before change and after change'
    }

    _prepare_box_plts([t2g_sb_a1, t2g_sb_a2], **kwargs)
    plt.savefig("./graphs/sb/travis2gha_lin.png")
    plt.close()
    _prepare_box_plts([t2g_sb_a1, t2g_sb_a2], **kwargs, log=True)
    plt.savefig("./graphs/sb/travis2gha_log.png")
    plt.close()

    kwargs["title"] = "GHA -> TravisCI"
    _prepare_box_plts([g2t_sb_a1, g2t_sb_a2], **kwargs)
    plt.savefig("./graphs/sb/gha2travis_lin.png")
    plt.close()
    _prepare_box_plts([g2t_sb_a1, g2t_sb_a2], **kwargs, log=True)
    plt.savefig("./graphs/sb/gha2travis_log.png")
    plt.close()


def br_pct(d):
    r = list()
    no_release_builds = 0
    for _slug, wfs in d.items():
        denom = sum([v[1] for v in wfs.values()])
        nom = sum(v[0] for v in wfs.values())
        val = nom / float(denom) if denom > 0 else 0
        if denom != 0:
            r.append(val * 100)
        else:
            no_release_builds += 1
    # print("There are", no_release_builds, 'repos without release builds')
    return r


def broken_release_dist1(gho, tcio):
    br_gho = gho[2]
    br_tcio = tcio[2]
    print()

    br_gho_pct = br_pct(br_gho)
    br_tcio_pct = br_pct(br_tcio)

    _prepare_box_plts([br_gho_pct, br_tcio_pct], ylabel="Percentage of broken release builds", xlabel="Data class",
                      labels=["GHA", "TravisCI"], title="Percentage of broken release builds per repository",
                      suptitle="",
                      log=False)
    plt.savefig("./graphs/br/single_ci_lin.png")
    plt.close()


def broken_release_dist2(t2g, g2t):
    br_t2g_1, br_t2g_2 = t2g[4:6]
    br_g2t_1, br_g2t_2 = g2t[4:6]

    br_t2g_1 = br_pct(br_t2g_1)
    br_t2g_2 = br_pct(br_t2g_2)

    br_g2t_1 = br_pct(br_g2t_1)
    br_g2t_2 = br_pct(br_g2t_2)

    kwargs = {
        'ylabel': "Percentage of broken release builds",
        'xlabel': "Data class",
        'labels': ["GHA -> TravisCI", "TravisCI -> GHA"],
        'title': "Before change",
        'suptitle': "Percentage of broken release builds per repository",
        'log': False
    }

    _prepare_box_plts([br_g2t_1, br_t2g_1], **kwargs)
    plt.savefig("./graphs/br/both_before_log.png")
    plt.close()

    kwargs["title"] = "After change"
    _prepare_box_plts([br_g2t_2, br_t2g_2], **kwargs)
    plt.savefig("./graphs/br/both_after_log.png")
    plt.close()

    kwargs["title"] = "Combined"
    _prepare_box_plts([br_g2t_1 + br_g2t_2, br_t2g_1 + br_t2g_2], **kwargs)
    plt.savefig("./graphs/br/both_combined_log.png")
    plt.close()

    kwargs = {
        'ylabel': 'Percentage broken release builds',
        'xlabel': '',
        'labels': ['Before', 'After'],
        'title': 'TravisCI -> GHA',
        'suptitle': 'Percentage broken release builds before change and after change'
    }

    _prepare_box_plts([br_t2g_1, br_t2g_2], **kwargs)
    plt.savefig("./graphs/br/travis2gha_lin.png")
    plt.close()
    _prepare_box_plts([br_t2g_1, br_t2g_2], **kwargs, log=False)
    plt.savefig("./graphs/br/travis2gha_log.png")
    plt.close()

    kwargs["title"] = "GHA -> TravisCI"
    _prepare_box_plts([br_g2t_1, br_g2t_2], **kwargs)
    plt.savefig("./graphs/br/gha2travis_lin.png")
    plt.close()
    _prepare_box_plts([br_g2t_1, br_g2t_2], **kwargs, log=False)
    plt.savefig("./graphs/br/gha2travis_log.png")
    plt.close()


def late_merging_dist1(gho, tcio, only=True):
    if only:
        lm_gho = gho[-1]
        lm_tcio = tcio[-1]
    else:
        lm_gho = gho
        lm_tcio = tcio

    branches_gho = [v.get('branch_count', 0) for v in lm_gho.values()]
    branches_tcio = [v.get('branch_count', 0) for v in lm_tcio.values()]

    missed_activity_gho = [v.get('ma_avg', 0) for v in lm_gho.values()]
    missed_activity_tcio = [v.get('ma_avg', 0) for v in lm_tcio.values()]

    branch_deviation_gho = [v.get('bd_avg', 0) for v in lm_gho.values()]
    branch_deviation_tcio = [v.get('bd_avg', 0) for v in lm_tcio.values()]

    unsynced_activity_gho = [v.get('ua_avg', 0) for v in lm_gho.values()]
    unsynced_activity_tcio = [v.get('ua_avg', 0) for v in lm_tcio.values()]

    kwargs = {
        'ylabel': "Amount of branches",
        'xlabel': "Data class",
        'labels': ["GHA", "TravisCI"] if only else ["GHA -> TravisCI", "TravisCI -> GHA"],
        'title': "Branches per repository",
        'suptitle': "",
        'log': False
    }

    save_pre = "./graphs/lm/ci_only_" if only else "./graphs/lm/ci_change_"

    # Branches

    _prepare_box_plts([branches_gho, branches_tcio], **kwargs)
    plt.savefig(f"{save_pre}branches_lin.png")
    plt.close()
    kwargs["log"] = True
    _prepare_box_plts([branches_gho, branches_tcio], **kwargs)
    plt.savefig(f"{save_pre}branches_log.png")
    plt.close()

    # Branch deviation
    kwargs["title"] = "Branch deviation"
    kwargs["ylabel"] = "Amount of days"
    kwargs["log"] = False
    _prepare_box_plts([branch_deviation_gho, branch_deviation_tcio], **kwargs)
    plt.savefig(f"{save_pre}bd_lin.png")
    plt.close()
    kwargs["log"] = True
    _prepare_box_plts([branch_deviation_gho, branch_deviation_tcio], **kwargs)
    plt.savefig(f"{save_pre}only_bd_log.png")
    plt.close()

    # Missed activity
    kwargs["title"] = "Missed activity"
    kwargs["log"] = False
    _prepare_box_plts([missed_activity_gho, missed_activity_tcio], **kwargs)
    plt.savefig(f"{save_pre}ma_lin.png")
    plt.close()
    kwargs["log"] = True
    _prepare_box_plts([missed_activity_gho, missed_activity_tcio], **kwargs)
    plt.savefig(f"{save_pre}ma_log.png")
    plt.close()

    # Unsynced activity
    kwargs["title"] = "Unsynced activity"
    kwargs["log"] = False
    _prepare_box_plts([unsynced_activity_gho, unsynced_activity_tcio], **kwargs, miny=-20)
    plt.savefig(f"{save_pre}ua_lin.png")
    plt.close()
    kwargs["log"] = True
    _prepare_box_plts([unsynced_activity_gho, unsynced_activity_tcio], **kwargs, miny=-20)
    plt.savefig(f"{save_pre}ua_log.png")
    plt.close()


def late_merging_dist2(t2g, g2t):
    t2g_before, t2g_after = t2g[-2:]
    g2t_before, g2t_after = g2t[-2:]

    late_merging_dist1(g2t_before, t2g_before, False)


if __name__ == '__main__':
    workflow_counts()

    gh_only = main_gha_only()
    travis_only = main_travis_only()
    gha_2_travis = main_gha_to_travis()
    travis_2_gha = main_travis_to_gha()

    slow_builds_dist1(gh_only, travis_only)
    slow_builds_dist2(travis_2_gha, gha_2_travis)

    broken_release_dist1(gh_only, travis_only)
    broken_release_dist2(travis_2_gha, gha_2_travis)

    late_merging_dist1(gh_only, travis_only)
    late_merging_dist2(travis_2_gha, gha_2_travis)
