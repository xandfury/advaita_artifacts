# Shared statistical test functions used across analysis notebooks.
# Covers Cochran's Q (binary detection), Friedman (stream counts),
# McNemar pairwise post-hoc, Nemenyi post-hoc, and mean rank tables.

import numpy as np
import pandas as pd
from scipy.stats import chi2, friedmanchisquare, rankdata, chi2_contingency, ncx2
from statsmodels.stats.contingency_tables import mcnemar
from itertools import combinations
import scikit_posthocs as sp



inst_approaches = ['Advaita', 'Aosp-Sci', 'Frida', 'Mitm']

def safe_log_p(p_val):
    """Format p-value as a power-of-10 string for display in Markdown/LaTeX.

    Returns
    -------
    str
        e.g. "$<10^{-29}$" or "$<10^{-99}$" for underflow.
    """
    if p_val <= 0 or np.isinf(np.log10(p_val)):
        return "$<10^{-99}$"
    return f"$<10^{{{int(np.log10(p_val))}}}$"


def get_dr_sets(df, vantage_points):
    """Return a dict mapping each vantage point to its set of detected DRs.

    Parameters
    ----------
    df : DataFrame
        Must contain 'vantage_type' and 'company' columns.
    vantage_points : list of str
        Approach names to include.

    Returns
    -------
    dict of {str: set}
    """
    return {
        v: set(df.loc[df["vantage_type"] == v, "company"].dropna())
        for v in vantage_points
    }

def perform_cochran(stats_df, vantage_points, dropna_cols=None):
    """Cochran's Q test on binary DR detection across instrumentation approaches.

    Parameters
    ----------
    stats_df : DataFrame
        Must contain 'vantage_type' and 'company' columns.
    vantage_points : list of str
        Ordered list of approach names. Ordering determines matrix column order.
    dropna_cols : list of str, optional
        Columns to drop NaN rows on before analysis. Defaults to
        ["http_stream_type", "company"].

    Returns
    -------
    dict with keys:
        binary_matrix, Q, p, W, k, df, N, dr_sets,
        hypothesis, verdict, consequence
    """
    if dropna_cols is None:
        dropna_cols = ["http_stream_type", "company"]

    df = stats_df.dropna(subset=dropna_cols).copy()
    dr_sets = get_dr_sets(df, vantage_points)
    all_drs = sorted(set().union(*dr_sets.values()))

    binary_matrix = pd.DataFrame(
        {v: [1 if dr in dr_sets[v] else 0 for dr in all_drs] for v in vantage_points},
        index=all_drs,
    )

    k = len(vantage_points)
    N = len(all_drs)
    data = binary_matrix.values
    col_sums = data.sum(axis=0)
    row_sums = data.sum(axis=1)
    T = data.sum()
    Q = (k - 1) * (k * np.sum(col_sums**2) - T**2) / (k * T - np.sum(row_sums**2))
    # p = 1 - chi2.cdf(Q, k - 1)
    p = chi2.sf(Q, k - 1)
    W = Q / (N * (k - 1))

    hypothesis = (
        "The proportion of data recipients detected is equal across "
        "all instrumentation approaches."
    )

    if p < 0.05:
        verdict = "Reject $H_0$"
        consequence = (
            "The four approaches differ significantly in which data recipients "
            "they detect. At least one approach observes a structurally different "
            "subset of DRs."
        )
    else:
        verdict = "Fail to reject $H_0$"
        consequence = (
            "No significant difference in binary detection rates across approaches. "
            "The observed variation is consistent with chance."
        )

    return {
        "binary_matrix": binary_matrix,
        "Q": Q,
        "p": p,
        "W": W,
        "k": k,
        "df": k - 1,
        "N": N,
        "dr_sets": dr_sets,
        "hypothesis": hypothesis,
        "verdict": verdict,
        "consequence": consequence,
    }


def perform_friedman(df, vantage_points, pivot_index, unit_description=None):
    """Friedman test on stream counts with Nemenyi post-hoc.

    Parameters
    ----------
    df : DataFrame
        Must contain 'vantage_type' and columns listed in pivot_index.
    vantage_points : list of str
        Ordered list of approach names.
    pivot_index : list of str
        Columns defining the unit of observation
        (e.g. ['company'] or ['company', 'pii_type']).
    unit_description: str, optional
        HTTP request count vs. PII type.

    Returns
    -------
    dict with keys:
        count_pivot, chi2, p, nemenyi, mean_ranks,
        hypothesis, verdict, consequence
    """
    group_cols = pivot_index + ["vantage_type"]
    count_pivot = df.groupby(group_cols).size().reset_index(name="count")
    count_pivot = count_pivot.pivot_table(
        index=pivot_index, columns="vantage_type", values="count", fill_value=0,
    )
    count_pivot = count_pivot.reindex(columns=vantage_points, fill_value=0)

    f_stat, f_p = friedmanchisquare(*[count_pivot[col] for col in count_pivot.columns])

    nemenyi = sp.posthoc_nemenyi_friedman(count_pivot.values)
    nemenyi.columns = count_pivot.columns
    nemenyi.index = count_pivot.columns

    ranks = np.apply_along_axis(rankdata, 1, count_pivot.values)
    mean_ranks = pd.Series(ranks.mean(axis=0), index=count_pivot.columns)

    if unit_description is None:
        unit_description = " x ".join(pivot_index)

    hypothesis = (
        f"The median count per {unit_description} does not differ "
        f"across instrumentation approaches."
    )

    if f_p < 0.05:
        verdict = "Reject $H_0$"
        consequence = (
            f"The median count per {unit_description} differs significantly "
            f"across approaches. Approaches that detect more subjects also "
            f"capture more observations per subject, indicating deeper "
            f"observability rather than mere breadth."
        )
    else:
        verdict = "Fail to reject $H_0$"
        consequence = (
            f"No significant difference in counts per {unit_description} "
            f"across approaches. The tools capture comparable volumes "
            f"per {unit_description}."
        )

    return {
        "count_pivot": count_pivot,
        "chi2": f_stat,
        "p": f_p,
        "nemenyi": nemenyi,
        "mean_ranks": mean_ranks,
        "hypothesis": hypothesis,
        "verdict": verdict,
        "consequence": consequence,
    }


def perform_mcnemar_pairwise(binary_matrix, vantage_points, alpha=0.05):
    """Pairwise McNemar tests with Bonferroni correction.

    Parameters
    ----------
    binary_matrix : DataFrame
        DRs x approaches, 0/1 values (as returned by perform_cochran).
    vantage_points : list of str
        Ordered list of approach names.
    alpha : float
        Family-wise significance level before correction.

    Returns
    -------
    dict with keys:
        results, n_comparisons, corrected_alpha,
        hypothesis, verdict, consequence
    """
    pairs = list(combinations(vantage_points, 2))
    n_comparisons = len(pairs)
    corrected_alpha = alpha / n_comparisons

    results = []
    for a, b in pairs:
        a_vals = binary_matrix[a].values
        b_vals = binary_matrix[b].values
        a_not_b = int(((a_vals == 1) & (b_vals == 0)).sum())
        b_not_a = int(((a_vals == 0) & (b_vals == 1)).sum())

        table = np.array([
            [int(((a_vals == 1) & (b_vals == 1)).sum()), a_not_b],
            [b_not_a, int(((a_vals == 0) & (b_vals == 0)).sum())],
        ])

        result = mcnemar(table, exact=False, correction=True)
        p_corrected = min(result.pvalue * n_comparisons, 1.0)

        results.append({
            "pair": (a, b),
            "a_not_b": a_not_b,
            "b_not_a": b_not_a,
            "statistic": result.statistic,
            "p": result.pvalue,
            "p_corrected": p_corrected,
            "significant": p_corrected < alpha,
        })

    all_significant = all(r["significant"] for r in results)

    hypothesis = (
        "For each pair, the probability of detection by one approach "
        "equals the probability of detection by the other."
    )

    if all_significant:
        verdict = "Reject $H_0$ for all pairs"
        consequence = (
            "Every pairwise comparison is significant after Bonferroni correction. "
            "Each approach detects a statistically distinct set of data recipients."
        )
    else:
        non_sig = [
            f"{r['pair'][0]} vs. {r['pair'][1]}"
            for r in results if not r["significant"]
        ]
        verdict = f"Reject $H_0$ for {n_comparisons - len(non_sig)}/{n_comparisons} pairs"
        consequence = (
            f"The following pairs do not differ significantly: "
            f"{', '.join(non_sig)}."
        )

    return {
        "results": results,
        "n_comparisons": n_comparisons,
        "corrected_alpha": corrected_alpha,
        "hypothesis": hypothesis,
        "verdict": verdict,
        "consequence": consequence,
    }

def build_summary_table(binary_matrix, count_pivot, vantage_points):
    """Build the overall detection comparison table (Table 4 in paper).

    Combines binary detection rates (Cochran's Q context) and stream count
    ranks (Friedman context) into a single summary DataFrame.

    Parameters
    ----------
    binary_matrix : DataFrame
        DRs x approaches, 0/1 values.
    count_pivot : DataFrame
        DRs x approaches, stream counts.
    vantage_points : list of str
        Ordered list of approach names.

    Returns
    -------
    dict with keys:
        table            : DataFrame, the summary table sorted by Q rank
        binary_mean_ranks : Series, mean ranks from binary detection
        count_mean_ranks  : Series, mean ranks from stream counts
    """
    N = len(binary_matrix)

    binary_ranks = np.apply_along_axis(rankdata, 1, binary_matrix.values)
    binary_mean_ranks = pd.Series(binary_ranks.mean(axis=0), index=vantage_points)

    count_ranks = np.apply_along_axis(rankdata, 1, count_pivot.values)
    count_mean_ranks = pd.Series(count_ranks.mean(axis=0), index=count_pivot.columns)

    table = pd.DataFrame(
        {
            "DRs Detected": [
                f"{binary_matrix[v].sum()}/{N}" for v in vantage_points
            ],
            "Coverage (%)": [
                round(binary_matrix[v].mean() * 100, 1) for v in vantage_points
            ],
            "Mean Rank (Q)": [
                round(binary_mean_ranks[v], 2) for v in vantage_points
            ],
            "Mean Rank (F)": [
                round(count_mean_ranks[v], 2) for v in vantage_points
            ],
        },
        index=vantage_points,
    )
    table = table.sort_values("Mean Rank (Q)", ascending=False)

    return {
        "table": table,
        "binary_mean_ranks": binary_mean_ranks,
        "count_mean_ranks": count_mean_ranks,
    }


def format_nemenyi_upper(nemenyi):
    """Format a Nemenyi p-value matrix as upper-triangular for display.

    Parameters
    ----------
    nemenyi : DataFrame
        Square pairwise p-value matrix from perform_friedman.

    Returns
    -------
    DataFrame
        Upper-triangular formatted strings; lower triangle and diagonal blank.
    """
    mask = np.triu(np.ones(nemenyi.shape, dtype=bool), k=1)
    upper = nemenyi.where(mask)
    return upper.map(
        lambda x: f"{x:.2e}" if pd.notna(x) and x < 0.01
        else (f"{x:.3f}" if pd.notna(x) else "")
    )


def perform_between_category(df, vantage_points, stratify_col, subject_cols="company"):
    """Per-approach chi-squared: does detection depend on category?

    Unit of observation is one (subject, category) pair. Pass the same
    subject_cols as perform_within_category so both tests use the same rows.
    """
    if isinstance(subject_cols, str):
        subject_cols = [subject_cols]
    key_cols = subject_cols + [stratify_col]

    pairs = df[key_cols].drop_duplicates().reset_index(drop=True)
    for vp in vantage_points:
        vp_sub = df[df["vantage_type"] == vp]
        vp_keys = set(zip(*[vp_sub[c] for c in key_cols]))
        pairs[f"{vp}_detected"] = [
            1 if k in vp_keys else 0
            for k in zip(*[pairs[c] for c in key_cols])
        ]

    results = {}
    for vp in vantage_points:
        ct = pd.crosstab(pairs[stratify_col], pairs[f"{vp}_detected"])
        if ct.shape[1] < 2:
            results[vp] = None
            continue

        chi2_stat, p_val, dof, expected = chi2_contingency(ct)
        no_sig = f"No significant dependence of {vp}'s detection on {stratify_col} at alpha = 0.05. " 
        no_sig += "This approach provides uniform coverage across categories."

        results[vp] = {
            "chi2": chi2_stat,
            "dof": dof,
            "p": p_val,
            "min_expected": expected.min(),
            "N": len(pairs),
            "ct": ct,
            "hypothesis": f"{vp}'s detection rate is independent of {stratify_col}.",
            "verdict": "Reject $H_0$" if p_val < 0.05 else "Fail to reject $H_0$",
            "consequence": (
                f"{vp}'s detection depends on {stratify_col}."
                if p_val < 0.05 else
                no_sig
            ),
        }
        
    return results

def compute_power(test_statistic, N, k, alpha=0.05):
    """Post-hoc power for Friedman or Cochran's Q test.

    Uses the noncentral chi-squared approximation. The observed test
    statistic serves as the noncentrality parameter.

    Parameters
    ----------
    test_statistic : float
        Observed Q (Cochran) or chi2_F (Friedman).
    N : int
        Number of subjects (DRs or apps).
    k : int
        Number of groups (instrumentation approaches).
    alpha : float
        Significance level.

    Returns
    -------
    dict with keys:
        power      : float, achieved power (1 - beta)
        W          : float, Kendall's W effect size
        effect     : str, qualitative label for W
        noncentrality : float, lambda parameter
        critical_value : float, chi-squared critical value
        interpretation : str, plain-language summary
    """
    df = k - 1
    W = test_statistic / (N * (k - 1))
    noncentrality = test_statistic  # lambda = N * (k-1) * W = Q or chi2_F
    critical_value = chi2.ppf(1 - alpha, df)
    power = 1 - ncx2.cdf(critical_value, df, noncentrality)

    if W < 0.1:
        effect = "negligible"
    elif W < 0.3:
        effect = "weak"
    elif W < 0.7:
        effect = "moderate"
    else:
        effect = "strong"

    interpretation = (
        f"With N={N} subjects, k={k} groups, and observed W={W:.4f} "
        f"({effect} effect), achieved power is {power:.4f}. "
    )
    if power >= 0.80:
        interpretation += (
            "The sample size is sufficient to detect the observed effect "
            "at the conventional 0.80 threshold."
        )
    else:
        interpretation += (
            f"Power falls below the conventional 0.80 threshold. "
            f"The sample size may be insufficient for detecting this effect size."
        )

    return {
        "power": power,
        "W": W,
        "effect": effect,
        "noncentrality": noncentrality,
        "critical_value": critical_value,
        "interpretation": interpretation,
    }


def perform_within_category(df, vantage_points, stratify_col, subject_cols="company"):
    """Cochran's Q on subject pairs within each category.

    Parameters
    ----------
    df : DataFrame
        Must contain 'vantage_type', subject_cols, and stratify_col.
    vantage_points : list of str
        Ordered list of approach names.
    stratify_col : str
        Column to stratify by (e.g. 'http_stream_type' or 'pii_group').
    subject_cols : str or list of str
        Columns defining the unit of observation.
        'company' for HTTP, ['company', 'pii_type'] for PII.

    Returns
    -------
    list of dicts, one per category.
    """
    if isinstance(subject_cols, str):
        subject_cols = [subject_cols]

    categories = sorted(df[stratify_col].dropna().unique())
    results = []

    for cat in categories:
        subset = df[df[stratify_col] == cat]
        pairs = subset[subject_cols].drop_duplicates().copy()

        for vp in vantage_points:
            vp_sub = subset[subset["vantage_type"] == vp]
            vp_pairs = set(zip(*[vp_sub[c] for c in subject_cols]))
            pairs[vp] = [
                1 if p in vp_pairs else 0
                for p in zip(*[pairs[c] for c in subject_cols])
            ]

        binary = pairs[vantage_points].values
        k = len(vantage_points)
        N = len(pairs)

        col_sums = binary.sum(axis=0)
        row_sums = binary.sum(axis=1)
        T = binary.sum()
        denom = k * T - np.sum(row_sums**2)

        if denom == 0 or N == 0:
            Q_val, p_val, W_val = np.nan, np.nan, np.nan
        else:
            Q_val = (k - 1) * (k * np.sum(col_sums**2) - T**2) / denom
            # p_val = 1 - chi2.cdf(Q_val, k - 1)
            p_val = chi2.sf(Q_val, k - 1)
            W_val = Q_val / (N * (k - 1))

        rates = {}
        for i, vp in enumerate(vantage_points):
            rates[vp] = col_sums[i] / N * 100 if N > 0 else 0.0

        hypothesis = (
            f"Detection rates do not differ across approaches "
            f"for {cat}."
        )
        if np.isnan(p_val):
            verdict = "Test not applicable"
            consequence = f"No discordance observed for {cat}."
        elif p_val < 0.05:
            verdict = "Reject $H_0$"
            consequence = (
                f"Approaches differ significantly in {cat} detection. "
                f"The observability gap persists within this category."
            )
        else:
            verdict = "Fail to reject $H_0$"
            consequence = (
                f"No significant difference across approaches for {cat}. "
                f"All tools achieve comparable detection for this category."
            )

        results.append({
            "category": cat,
            "N": N,
            "Q": Q_val,
            "p": p_val,
            "W": W_val,
            "df": k - 1,
            "rates": rates,
            "binary_matrix": pairs[vantage_points],
            "hypothesis": hypothesis,
            "verdict": verdict,
            "consequence": consequence,
        })

    return results
