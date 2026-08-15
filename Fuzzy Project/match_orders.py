"""
Fuzzy Matching Engine for Customer Orders
==========================================
Matches response survey data against sales master records using RapidFuzz.
"""

import os
import re
import sys
import pandas as pd
from rapidfuzz import fuzz, process

# Ensure proper standard output encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# File paths
SALES_FILES = [
    '1-27jun.csv',
    '5 - 15 aug.csv',
    '20 - 05 aug.csv',
    '28-20july.csv'
]
SAMPLE_FILE = 'Response Data (161).csv'

OUTPUT_EXCEL = 'matched_orders.xlsx'
OUTPUT_CSV = 'matched_orders.csv'
OUTPUT_REVIEW = 'review_required.xlsx'

# Common product typo / variation normalization dictionary
PRODUCT_TYPO_MAP = {
    r'\bsurvical\b': 'cervical',
    r'\bceervical\b': 'cervical',
    r'\bmassager\b': 'massage',
    r'\bmasseger\b': 'massage',
    r'\bmessanfger\b': 'massage',
    r'\bmassger\b': 'massage',
    r'\bmessage\b': 'massage',
    r'\bmoniter\b': 'monitor',
    r'\bmoiter\b': 'monitor',
    r'\bmeter\b': 'monitor',
    r'\bmatter\b': 'mattress',
    r'\bsuppliments\b': 'calm',
    r'\bbracelete\b': 'brace',
    r'\blm\s*ber\b': 'lumbar',
    r'\blmber\b': 'lumbar',
    r'\bdiaper pants\b': 'diaper pant',
}


def clean_text(text):
    """General text cleaner: lowercase, strip, remove punctuation, single space."""
    if not isinstance(text, str) or pd.isna(text):
        return ''
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def clean_customer_name(text):
    """Customer name cleaner: strip honorific suffixes (ji, g), remove punctuation."""
    if not isinstance(text, str) or pd.isna(text):
        return ''
    text = text.lower().strip()
    text = re.sub(r'\b(ji|g)\b$', '', text).strip()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def normalize_product_text(p_text):
    """Apply domain specific typo corrections for product terms."""
    p = clean_text(p_text)
    for pattern, replacement in PRODUCT_TYPO_MAP.items():
        p = re.sub(pattern, replacement, p)
    return re.sub(r'\s+', ' ', p).strip()


def compute_customer_similarity(sample_c, sales_c):
    """
    Computes robust similarity between two customer names.
    Handles exact matches, initials, word ordering, and spelling differences.
    """
    if not sample_c or not sales_c:
        return 0.0
    if sample_c == sales_c:
        return 100.0

    s_tokens = sample_c.split()
    t_tokens = sales_c.split()
    s_set = set(s_tokens)
    t_set = set(t_tokens)

    # Identical tokens in different order
    if s_set == t_set:
        return 100.0

    # Subsets (e.g., initial dropped like 'Unnikrishnan EP' vs 'Unnikrishnan')
    if s_set.issubset(t_set) or t_set.issubset(s_set):
        diff = s_set ^ t_set
        # If difference is only single/double character initials (e.g., 'ep', 'k', 'c')
        if all(len(d) <= 2 for d in diff):
            return 95.0
        # If there is a shared significant token (>= 4 chars)
        common = s_set & t_set
        if any(len(w) >= 4 for w in common):
            return 88.0

    r_ratio = fuzz.ratio(sample_c, sales_c)
    r_sort = fuzz.token_sort_ratio(sample_c, sales_c)
    r_set = fuzz.token_set_ratio(sample_c, sales_c)

    return max(r_ratio, r_sort, (r_sort + r_set) / 2.0)


def compute_product_similarity(sample_p, sales_p, sales_i):
    """
    Computes product similarity comparing sample product against both
    Product_ (category) and item_name (full item description).
    Handles multi-product listings (e.g., comma, 'and', '&').
    """
    if not sample_p:
        return 50.0  # Neutral baseline if sample product is blank

    p_norm = normalize_product_text(sample_p)
    if not p_norm:
        return 50.0

    # Split multi-product strings
    parts = re.split(r'[,;/]|\band\b|\bwith\b|&|\+', p_norm)
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        parts = [p_norm]

    best_score = 0.0
    for part in parts:
        # Category comparison
        s_p_set = fuzz.token_set_ratio(part, sales_p)
        s_p_sort = fuzz.token_sort_ratio(part, sales_p)
        s_p_part = fuzz.partial_ratio(part, sales_p)
        s_p = max(s_p_set, s_p_sort, s_p_part * 0.9)

        # Item name comparison
        s_i_set = fuzz.token_set_ratio(part, sales_i)
        s_i_sort = fuzz.token_sort_ratio(part, sales_i)
        s_i_part = fuzz.partial_ratio(part, sales_i)
        s_i = max(s_i_set, s_i_sort, s_i_part * 0.9)

        part_max = max(s_p, s_i)
        if part_max > best_score:
            best_score = part_max

    # Full string comparisons
    full_p = max(fuzz.token_set_ratio(p_norm, sales_p), fuzz.token_sort_ratio(p_norm, sales_p))
    full_i = max(fuzz.token_set_ratio(p_norm, sales_i), fuzz.token_sort_ratio(p_norm, sales_i))

    return max(best_score, full_p, full_i)


def calculate_final_score(c_score, p_score, has_sample_product):
    """
    Calculates weighted final score prioritizing strong customer match + product match.
    """
    if not has_sample_product:
        # If product was not provided in the survey response
        return c_score * 0.90
    if c_score >= 85 and p_score >= 70:
        return c_score * 0.55 + p_score * 0.45
    elif c_score >= 85 and p_score < 50:
        # Strong customer match, but mismatched product description
        return c_score * 0.60 + p_score * 0.40
    elif c_score < 70 and p_score >= 85:
        # Product match alone cannot override a poor customer match
        return c_score * 0.70 + p_score * 0.30
    else:
        return c_score * 0.60 + p_score * 0.40


def main():
    print("=" * 70)
    print("Starting Order Fuzzy Matching Pipeline...")
    print("=" * 70)

    # 1. Load and combine Sales Master CSV files
    print("\n[Step 1/5] Loading Sales Master Data...")
    sales_cols = ['sale_order_code', 'Product_', 'item_name', 'Customer_Name', 'Order_Date']
    sales_dataframes = []
    
    for f in SALES_FILES:
        if not os.path.exists(f):
            print(f"Error: Sales file '{f}' not found in current directory.")
            sys.exit(1)
        df_part = pd.read_csv(
            f,
            usecols=sales_cols,
            dtype=str,
            encoding='utf-8',
            encoding_errors='replace'
        )
        sales_dataframes.append(df_part)
        print(f"  - Loaded '{f}': {len(df_part):,} records")

    df_sales = pd.concat(sales_dataframes, ignore_index=True)
    print(f"Total Sales Master Records: {len(df_sales):,}")

    # 2. Load Sample CSV
    print(f"\n[Step 2/5] Loading Sample Survey Data from '{SAMPLE_FILE}'...")
    if not os.path.exists(SAMPLE_FILE):
        print(f"Error: Sample file '{SAMPLE_FILE}' not found in current directory.")
        sys.exit(1)

    df_sample = pd.read_csv(
        SAMPLE_FILE,
        usecols=[1, 2],
        header=0,
        dtype=str,
        encoding='utf-8',
        encoding_errors='replace'
    )
    df_sample.columns = ['Customer Name', 'Which Product (Catagory)']
    print(f"Total Sample Records to Match: {len(df_sample)}")

    # 3. Clean Text Columns
    print("\n[Step 3/5] Cleaning Customer and Product Text Fields...")
    df_sales['clean_customer'] = df_sales['Customer_Name'].apply(clean_customer_name)
    df_sales['clean_product'] = df_sales['Product_'].apply(clean_text)
    df_sales['clean_item'] = df_sales['item_name'].apply(clean_text)

    df_sample['clean_customer'] = df_sample['Customer Name'].apply(clean_customer_name)
    df_sample['clean_product'] = df_sample['Which Product (Catagory)'].apply(clean_text)

    # Build an inverted index mapping cleaned customer name -> list of sales dataframe row indices
    customer_to_indices = {}
    for idx, c_name in enumerate(df_sales['clean_customer']):
        if c_name:
            customer_to_indices.setdefault(c_name, []).append(idx)

    unique_sales_customers = list(customer_to_indices.keys())
    print(f"Indexed {len(unique_sales_customers):,} unique customer names from sales records.")

    # 4. Perform Candidate Extraction & Matching
    print("\n[Step 4/5] Running RapidFuzz Matching...")
    matched_results = []
    high_confidence_count = 0
    review_count = 0
    no_match_count = 0

    for s_idx, s_row in df_sample.iterrows():
        orig_cust = s_row['Customer Name']
        orig_prod = s_row['Which Product (Catagory)']
        clean_cust = s_row['clean_customer']
        clean_prod = s_row['clean_product']
        has_prod = bool(clean_prod)

        if not clean_cust:
            matched_results.append({
                'Original Customer Name': orig_cust,
                'Original Product': orig_prod,
                'Matched Customer_Name': None,
                'Matched Product_': None,
                'Matched item_name': None,
                'sale_order_code': None,
                'Order_Date': None,
                'Customer Score': 0.0,
                'Product Score': 0.0,
                'Final Score': 0.0,
                'Match Status': 'NO MATCH'
            })
            no_match_count += 1
            continue

        # Extract top candidate customer names using token_sort_ratio and WRatio
        cands_sort = process.extract(
            clean_cust,
            unique_sales_customers,
            scorer=fuzz.token_sort_ratio,
            limit=30,
            score_cutoff=50.0
        )
        cands_w = process.extract(
            clean_cust,
            unique_sales_customers,
            scorer=fuzz.WRatio,
            limit=20,
            score_cutoff=65.0
        )

        candidate_name_set = set([c[0] for c in cands_sort] + [c[0] for c in cands_w])

        best_match_record = None
        best_final_score = -1.0
        best_cust_score = 0.0
        best_prod_score = 0.0

        for cand_name in candidate_name_set:
            c_score = compute_customer_similarity(clean_cust, cand_name)
            if c_score < 55.0:
                continue

            sales_indices = customer_to_indices[cand_name]
            for s_i in sales_indices:
                sales_rec = df_sales.iloc[s_i]
                p_score = compute_product_similarity(
                    clean_prod,
                    sales_rec['clean_product'],
                    sales_rec['clean_item']
                )

                final_score = calculate_final_score(c_score, p_score, has_prod)

                if final_score > best_final_score:
                    best_final_score = final_score
                    best_cust_score = c_score
                    best_prod_score = p_score
                    best_match_record = sales_rec

        # Determine Match Status
        if best_final_score >= 90.0:
            match_status = 'HIGH CONFIDENCE'
            high_confidence_count += 1
        elif best_final_score >= 75.0:
            match_status = 'REVIEW'
            review_count += 1
        else:
            match_status = 'NO MATCH'
            no_match_count += 1

        matched_results.append({
            'Original Customer Name': orig_cust,
            'Original Product': orig_prod,
            'Matched Customer_Name': best_match_record['Customer_Name'] if best_match_record is not None else None,
            'Matched Product_': best_match_record['Product_'] if best_match_record is not None else None,
            'Matched item_name': best_match_record['item_name'] if best_match_record is not None else None,
            'sale_order_code': best_match_record['sale_order_code'] if best_match_record is not None else None,
            'Order_Date': best_match_record['Order_Date'] if best_match_record is not None else None,
            'Customer Score': round(best_cust_score, 1),
            'Product Score': round(best_prod_score, 1),
            'Final Score': round(best_final_score, 1) if best_final_score > 0 else 0.0,
            'Match Status': match_status
        })

    df_output = pd.DataFrame(matched_results)

    # 5. Export Output Files
    print("\n[Step 5/5] Writing Output Files...")
    
    # Full results (Excel and CSV)
    df_output.to_excel(OUTPUT_EXCEL, index=False, engine='openpyxl')
    print(f"  -> Successfully generated '{OUTPUT_EXCEL}'")

    df_output.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    print(f"  -> Successfully generated '{OUTPUT_CSV}'")

    # Review required results (REVIEW and NO MATCH only)
    df_review = df_output[df_output['Match Status'].isin(['REVIEW', 'NO MATCH'])].copy()
    df_review.to_excel(OUTPUT_REVIEW, index=False, engine='openpyxl')
    print(f"  -> Successfully generated '{OUTPUT_REVIEW}' ({len(df_review)} rows)")

    # Final Summary Statistics
    total_records = len(df_sample)
    success_rate = ((high_confidence_count + review_count) / total_records) * 100.0

    print("\n" + "=" * 70)
    print("FINAL MATCHING SUMMARY")
    print("=" * 70)
    print(f"Total Sample Records       : {total_records}")
    print(f"HIGH CONFIDENCE (>= 90)    : {high_confidence_count} ({high_confidence_count/total_records*100:.1f}%)")
    print(f"REVIEW (75 - 89)           : {review_count} ({review_count/total_records*100:.1f}%)")
    print(f"NO MATCH (< 75)            : {no_match_count} ({no_match_count/total_records*100:.1f}%)")
    print(f"Percentage Matched         : {success_rate:.1f}%")
    print("=" * 70)

    print("\nFirst 10 Matched Results:")
    cols_to_preview = [
        'Original Customer Name',
        'Original Product',
        'Matched Customer_Name',
        'Matched item_name',
        'sale_order_code',
        'Customer Score',
        'Product Score',
        'Final Score',
        'Match Status'
    ]
    print(df_output[cols_to_preview].head(10).to_string(index=False))


if __name__ == '__main__':
    main()
