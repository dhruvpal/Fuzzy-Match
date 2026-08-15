"""
Universal File Loader
====================
Provides robust loading and combining of CSV and Excel datasets with
automatic encoding detection, multi-file concatenation, and source file tracking.
"""

import io
import os
import pandas as pd
from typing import List, Tuple, Union, Any, Optional

ENCODINGS_TO_TRY = ['utf-8', 'utf-8-sig', 'cp1252', 'latin1', 'iso-8859-1']


def read_tabular_file(
    file_input: Any,
    filename: Optional[str] = None
) -> Tuple[pd.DataFrame, str]:
    """
    Reads a CSV or Excel file from a file path or file-like object (e.g. Streamlit UploadedFile).
    
    Returns:
        (DataFrame, filename_str)
    """
    # Determine filename
    if filename is None:
        if hasattr(file_input, 'name'):
            filename = file_input.name
        elif isinstance(file_input, str):
            filename = os.path.basename(file_input)
        else:
            filename = "uploaded_file"

    lower_name = filename.lower()

    # Excel Files
    if lower_name.endswith(('.xlsx', '.xls', '.xlsm')):
        if isinstance(file_input, str):
            df = pd.read_excel(file_input, dtype=str)
        else:
            file_input.seek(0)
            df = pd.read_excel(file_input, dtype=str)
        return df, filename

    # CSV / Text Files
    if isinstance(file_input, str):
        # File path
        last_err = None
        for enc in ENCODINGS_TO_TRY:
            try:
                df = pd.read_csv(
                    file_input,
                    dtype=str,
                    encoding=enc,
                    encoding_errors='replace',
                    low_memory=False
                )
                return df, filename
            except Exception as e:
                last_err = e
        raise ValueError(f"Could not read CSV file '{filename}': {last_err}")
    else:
        # File-like object / Streamlit UploadedFile
        last_err = None
        for enc in ENCODINGS_TO_TRY:
            try:
                file_input.seek(0)
                content = file_input.read()
                # If bytes, decode with current encoding
                if isinstance(content, bytes):
                    text_stream = io.StringIO(content.decode(enc, errors='replace'))
                else:
                    text_stream = io.StringIO(content)
                df = pd.read_csv(
                    text_stream,
                    dtype=str,
                    low_memory=False
                )
                return df, filename
            except Exception as e:
                last_err = e
        raise ValueError(f"Could not read uploaded CSV '{filename}': {last_err}")


def load_sample_dataset(file_input: Any, filename: Optional[str] = None) -> Tuple[pd.DataFrame, dict]:
    """
    Loads the sample dataset and returns (DataFrame, metadata_dict).
    """
    df, fname = read_tabular_file(file_input, filename)
    meta = {
        'filename': fname,
        'rows': len(df),
        'columns_count': len(df.columns),
        'columns': list(df.columns)
    }
    return df, meta


def load_and_combine_master_datasets(
    file_inputs: List[Any],
    source_col_name: str = "Source Master File"
) -> Tuple[pd.DataFrame, dict]:
    """
    Loads one or multiple master dataset files, adds source tracking column,
    and combines them into a single consolidated DataFrame.
    """
    if not file_inputs:
        raise ValueError("No master files provided.")

    dfs = []
    file_info = []

    for f_input in file_inputs:
        df_part, fname = read_tabular_file(f_input)
        df_part[source_col_name] = fname
        dfs.append(df_part)
        file_info.append({
            'filename': fname,
            'rows': len(df_part),
            'columns_count': len(df_part.columns) - 1
        })

    # Combine all DataFrames
    combined_df = pd.concat(dfs, ignore_index=True)

    meta = {
        'files_count': len(file_inputs),
        'file_details': file_info,
        'total_rows': len(combined_df),
        'columns_count': len(combined_df.columns) - 1, # Exclude source col from schema count
        'columns': [c for c in combined_df.columns if c != source_col_name],
        'source_col': source_col_name
    }
    return combined_df, meta
