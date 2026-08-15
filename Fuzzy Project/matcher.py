"""
Universal Fuzzy Matching Engine
===============================
High-performance, domain-agnostic matching engine using RapidFuzz, candidate
indexing, weighted multi-column scoring, type-aware comparators, and alternative
candidate ranking.
"""

import re
import math
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional, Callable, Union
from rapidfuzz import fuzz, process
from utils import normalize_generic_text, detect_data_type


class MatchingRule:
    """Represents a mapping rule between one sample column and one or more master columns."""
    def __init__(
        self,
        sample_col: str,
        master_col: Union[str, List[str]],
        weight: float,
        mode: str = "automatic"
    ):
        self.sample_col = sample_col
        self.master_col = master_col if isinstance(master_col, list) else [master_col]
        self.weight = float(weight) / 100.0 if weight > 1.0 else float(weight)
        self.mode = mode.lower()


def score_text_field(sample_val: str, master_val: str) -> float:
    """Calculates text similarity score using multiple RapidFuzz token and edit-distance metrics."""
    s = sample_val
    m = master_val

    # Blank value handling
    if not s and not m:
        return 0.0  # Both empty - no meaningful match
    if s and not m:
        return 0.0  # Master is missing required info
    if not s and m:
        return 50.0  # Sample didn't provide this attribute (neutral)

    if s == m:
        return 100.0

    # Token sort / set / Levenshtein ratio
    r_sort = fuzz.token_sort_ratio(s, m)
    r_set = fuzz.token_set_ratio(s, m)
    r_ratio = fuzz.ratio(s, m)
    r_part = fuzz.partial_ratio(s, m)

    # Identical token sets in different order
    s_tokens = set(s.split())
    m_tokens = set(m.split())
    if s_tokens == m_tokens:
        return 100.0

    # Subset of tokens (e.g. single initials dropped or extra word)
    if s_tokens.issubset(m_tokens) or m_tokens.issubset(s_tokens):
        diff = s_tokens ^ m_tokens
        if all(len(d) <= 2 for d in diff):
            return 95.0
        common = s_tokens & m_tokens
        if any(len(w) >= 4 for w in common):
            return 88.0

    return max(r_sort, (r_sort + r_set) / 2.0, r_ratio, r_part * 0.9)


def score_numeric_field(sample_val: str, master_val: str) -> float:
    """Scores numeric fields with tolerance and relative difference."""
    if not sample_val and not master_val:
        return 0.0
    if not sample_val or not master_val:
        return 0.0

    s_clean = re.sub(r'[^\d.-]', '', sample_val)
    m_clean = re.sub(r'[^\d.-]', '', master_val)

    if s_clean and m_clean:
        try:
            s_num = float(s_clean)
            m_num = float(m_clean)
            if s_num == m_num:
                return 100.0
            denom = max(abs(s_num), abs(m_num), 1.0)
            diff = abs(s_num - m_num) / denom
            return max(0.0, 100.0 * (1.0 - diff))
        except ValueError:
            pass

    return score_text_field(sample_val, master_val)


def score_date_field(sample_val: str, master_val: str) -> float:
    """Scores date fields based on temporal proximity."""
    if not sample_val and not master_val:
        return 0.0
    if not sample_val or not master_val:
        return 0.0

    try:
        s_date = pd.to_datetime(sample_val, errors='raise', format='mixed')
        m_date = pd.to_datetime(master_val, errors='raise', format='mixed')
        day_diff = abs((s_date - m_date).days)
        if day_diff == 0:
            return 100.0
        elif day_diff <= 3:
            return 90.0
        elif day_diff <= 7:
            return 80.0
        elif day_diff <= 30:
            return 60.0
        else:
            return max(0.0, 100.0 - day_diff * 2.0)
    except Exception:
        pass

    return score_text_field(sample_val, master_val)


def score_exact_field(sample_val: str, master_val: str) -> float:
    """Exact normalized match scorer."""
    if not sample_val and not master_val:
        return 0.0
    return 100.0 if sample_val == master_val else 0.0


def score_rule_field(
    sample_val: str,
    master_val: str,
    mode: str,
    inferred_type: str
) -> float:
    """Dispatches scoring based on selected or inferred mode."""
    target_mode = mode
    if target_mode == "automatic":
        target_mode = inferred_type

    if target_mode == "exact":
        return score_exact_field(sample_val, master_val)
    elif target_mode == "numeric":
        return score_numeric_field(sample_val, master_val)
    elif target_mode == "date":
        return score_date_field(sample_val, master_val)
    else: # text_fuzzy
        return score_text_field(sample_val, master_val)


def run_fuzzy_matching(
    df_sample: pd.DataFrame,
    df_master: pd.DataFrame,
    rules: List[MatchingRule],
    return_cols: List[str],
    high_threshold: float = 90.0,
    review_threshold: float = 75.0,
    source_col: str = "Source Master File",
    progress_callback: Optional[Callable[[float, str], None]] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Executes domain-agnostic fuzzy matching with candidate indexing,
    weighted scoring, explanation tracking, and alternative candidate ranking.
    """
    if not rules:
        raise ValueError("At least one matching rule must be specified.")

    total_weight = sum(r.weight for r in rules)
    if not math.isclose(total_weight, 1.0, rel_tol=1e-2, abs_tol=1e-2):
        raise ValueError(f"Total matching weights must equal 100%. Current total: {total_weight * 100:.1f}%")

    # 1. Pre-normalize required columns
    sample_norm_cols = {}
    for r in rules:
        s_col = r.sample_col
        if s_col not in sample_norm_cols:
            sample_norm_cols[s_col] = df_sample[s_col].apply(normalize_generic_text).tolist()

    master_norm_cols = {}
    master_inferred_types = {}
    for r in rules:
        for m_col in r.master_col:
            if m_col not in master_norm_cols:
                master_norm_cols[m_col] = df_master[m_col].apply(normalize_generic_text).tolist()
                master_inferred_types[m_col] = detect_data_type(df_master[m_col])

    # 2. Build candidate indexing on highest-weight rule
    sorted_rules = sorted(rules, key=lambda x: x.weight, reverse=True)
    primary_rule = sorted_rules[0]
    primary_s_col = primary_rule.sample_col
    primary_m_cols = primary_rule.master_col

    # Inverted index on primary master column
    primary_m_col = primary_m_cols[0]
    master_primary_vals = master_norm_cols[primary_m_col]

    val_to_master_indices: Dict[str, List[int]] = {}
    for m_idx, m_val in enumerate(master_primary_vals):
        if m_val:
            val_to_master_indices.setdefault(m_val, []).append(m_idx)

    unique_master_primary_vals = list(val_to_master_indices.keys())

    # 3. Matching loop
    results = []
    total_samples = len(df_sample)
    high_conf_count = 0
    review_count = 0
    no_match_count = 0

    for s_idx in range(total_samples):
        if progress_callback and s_idx % 10 == 0:
            progress_callback(
                (s_idx + 1) / total_samples,
                f"Matching sample record {s_idx + 1} of {total_samples}..."
            )

        sample_primary_val = sample_norm_cols[primary_s_col][s_idx]

        # Gather candidate master indices
        candidate_master_indices = set()

        if sample_primary_val:
            # 1. Exact normalized matches
            if sample_primary_val in val_to_master_indices:
                for idx in val_to_master_indices[sample_primary_val]:
                    candidate_master_indices.add(idx)

            # 2. Fuzzy candidates from RapidFuzz
            cands_sort = process.extract(
                sample_primary_val,
                unique_master_primary_vals,
                scorer=fuzz.token_sort_ratio,
                limit=35,
                score_cutoff=45.0
            )
            for c_val, _, _ in cands_sort:
                for idx in val_to_master_indices[c_val]:
                    candidate_master_indices.add(idx)

            cands_w = process.extract(
                sample_primary_val,
                unique_master_primary_vals,
                scorer=fuzz.WRatio,
                limit=20,
                score_cutoff=60.0
            )
            for c_val, _, _ in cands_w:
                for idx in val_to_master_indices[c_val]:
                    candidate_master_indices.add(idx)

        # Fallback: if no candidates found on primary column, evaluate against small sample
        if not candidate_master_indices:
            # If sample primary was blank, search across second rule if available
            if len(sorted_rules) > 1:
                sec_rule = sorted_rules[1]
                sec_s_col = sec_rule.sample_col
                sec_m_col = sec_rule.master_col[0]
                sec_s_val = sample_norm_cols[sec_s_col][s_idx]
                if sec_s_val:
                    sec_unique = list(set(master_norm_cols[sec_m_col]))
                    sec_cands = process.extract(
                        sec_s_val,
                        sec_unique,
                        scorer=fuzz.token_sort_ratio,
                        limit=25,
                        score_cutoff=50.0
                    )
                    for c_val, _, _ in sec_cands:
                        for m_i, m_v in enumerate(master_norm_cols[sec_m_col]):
                            if m_v == c_val:
                                candidate_master_indices.add(m_i)

        # Evaluate candidate master rows
        evaluated_candidates = []

        for m_idx in candidate_master_indices:
            rule_scores = {}
            weighted_score = 0.0
            non_blank_rules = 0

            for rule in rules:
                s_val = sample_norm_cols[rule.sample_col][s_idx]
                
                # If rule has multiple master columns (e.g. category + item name), pick best
                best_m_score = 0.0
                for m_col in rule.master_col:
                    m_val = master_norm_cols[m_col][m_idx]
                    inf_type = master_inferred_types.get(m_col, 'text')
                    score = score_rule_field(s_val, m_val, rule.mode, inf_type)
                    if score > best_m_score:
                        best_m_score = score

                rule_scores[rule.sample_col] = best_m_score
                weighted_score += best_m_score * rule.weight
                if s_val:
                    non_blank_rules += 1

            # Penalty if sample provided fields but master had 0 score on dominant rule
            if rules[0].sample_col in rule_scores and rule_scores[rules[0].sample_col] < 40.0:
                weighted_score = min(weighted_score, 65.0)

            evaluated_candidates.append({
                'master_idx': m_idx,
                'weighted_score': weighted_score,
                'rule_scores': rule_scores
            })

        # Sort candidates by weighted score descending
        evaluated_candidates.sort(key=lambda x: x['weighted_score'], reverse=True)

        best_cand = evaluated_candidates[0] if evaluated_candidates else None
        best_score = best_cand['weighted_score'] if best_cand else 0.0
        best_m_idx = best_cand['master_idx'] if best_cand else None

        # Determine Match Status
        if best_score >= high_threshold:
            status = 'HIGH CONFIDENCE'
            high_conf_count += 1
        elif best_score >= review_threshold:
            status = 'REVIEW'
            review_count += 1
        else:
            status = 'NO MATCH'
            no_match_count += 1

        # Format Top 3 alternative candidates for review
        alt_candidates = []
        for cand in evaluated_candidates[:3]:
            c_idx = cand['master_idx']
            c_score = cand['weighted_score']
            c_master_row = df_master.iloc[c_idx]
            alt_info = {
                'Score': round(c_score, 1),
                'Source': c_master_row.get(source_col, ''),
                'Values': {col: c_master_row[col] for col in return_cols if col in c_master_row}
            }
            # Add matching field values
            for r in rules:
                for mc in r.master_col:
                    alt_info['Values'][mc] = c_master_row.get(mc, '')
            alt_candidates.append(alt_info)

        # Build Explanation String
        if best_cand:
            explanation_parts = [
                f"{col}: {score:.0f}%"
                for col, score in best_cand['rule_scores'].items()
            ]
            explanation = f"Matched ({', '.join(explanation_parts)}) -> Final: {best_score:.1f}%"
        else:
            explanation = "No viable candidate found."

        # Build Result Row
        result_row = {
            'Sample Row #': s_idx + 1
        }

        # Original Sample Columns
        for r in rules:
            result_row[f"Sample: {r.sample_col}"] = df_sample.iloc[s_idx][r.sample_col]

        # Matched Master Columns
        for r in rules:
            if best_m_idx is not None and status != 'NO MATCH':
                # Show first master target column value
                primary_target = r.master_col[0]
                result_row[f"Matched: {primary_target}"] = df_master.iloc[best_m_idx][primary_target]
            else:
                result_row[f"Matched: {r.master_col[0]}"] = None

        # Return Columns (Blank if NO MATCH)
        for ret_col in return_cols:
            if best_m_idx is not None and status != 'NO MATCH':
                result_row[ret_col] = df_master.iloc[best_m_idx].get(ret_col, None)
            else:
                result_row[ret_col] = None

        # Individual Rule Scores
        for r in rules:
            if best_cand:
                result_row[f"Score: {r.sample_col}"] = round(best_cand['rule_scores'].get(r.sample_col, 0.0), 1)
            else:
                result_row[f"Score: {r.sample_col}"] = 0.0

        result_row['Final Score'] = round(best_score, 1)
        result_row['Match Status'] = status
        result_row['Source Master File'] = df_master.iloc[best_m_idx].get(source_col, '') if best_m_idx is not None else ''
        result_row['Explanation'] = explanation
        result_row['_alternative_candidates'] = alt_candidates

        results.append(result_row)

    if progress_callback:
        progress_callback(1.0, "Matching completed successfully!")

    df_results = pd.DataFrame(results)

    summary = {
        'total_samples': total_samples,
        'high_confidence': high_conf_count,
        'review': review_count,
        'no_match': no_match_count,
        'match_rate': round(((high_conf_count + review_count) / total_samples) * 100.0, 1) if total_samples > 0 else 0.0,
        'high_confidence_rate': round((high_conf_count / total_samples) * 100.0, 1) if total_samples > 0 else 0.0
    }

    return df_results, summary
