# -*- coding: utf-8 -*-
import pandas as pd
import os
import re
from datetime import datetime, timedelta

def clean_match_id(val):
    if pd.isnull(val): return ""
    try:
        val_str = str(val).replace('.0', '').strip()
        if val_str.isdigit(): return str(int(val_str)).zfill(6)
        return val_str
    except ValueError:
        return str(val).strip()

def get_join_col(df):
    for c in df.columns:
        if '3' in c and '1.' in c: return c
    return df.columns[1]

def get_email_col(df):
    for c in df.columns:
        if '件' in c and '址' in c: return c
        elif 'mail' in c.lower(): return c
    return None

def filter_attention_check(df, phase_name):
    check_cols = [c for c in df.columns if '請選擇' in c]
    if not check_cols:
        return df
    
    col = check_cols[-1] # Usually the last one if there are multiple, but there is usually one
    match = re.search(r'請選擇「(\d+)」', col)
    if match:
        expected_val = int(match.group(1))
        original_len = len(df)
        df = df[pd.to_numeric(df[col], errors='coerce') == expected_val]
        print(f"\\n{phase_name} Invalid Cleanup: Required {expected_val} for '{col}'. Removed {original_len - len(df)} rows. Kept {len(df)}.")
    return df

def run_longitudinal_analysis():
    print("Loading data...")
    xlsx_path = 'd:/Coding_Project/Research_Scale/Research_Questionaire/職涯發展與工作狀況調查問卷_260227.xlsx'
    
    t1 = pd.read_excel(xlsx_path, sheet_name='第一階段')
    t2 = pd.read_excel(xlsx_path, sheet_name='第二階段')
    t3 = pd.read_excel(xlsx_path, sheet_name='第三階段')

    # Assign clean match ID
    t1['Join_ID'] = t1[get_join_col(t1)].apply(clean_match_id)
    t2['Join_ID'] = t2[get_join_col(t2)].apply(clean_match_id)
    t3['Join_ID'] = t3[get_join_col(t3)].apply(clean_match_id)

    # Convert known emails to lowercase and strip whitespace for precise mapping
    t2_email_col = get_email_col(t2)
    if t2_email_col: t2['clean_email'] = t2[t2_email_col].astype(str).str.lower().str.strip()
    t3_email_col = get_email_col(t3)
    if t3_email_col: t3['clean_email'] = t3[t3_email_col].astype(str).str.lower().str.strip()

    # Manual Overrides from User based directly on given T1 mapping values
    overrides = {
        'jaychen@trendforce.com': '0710588',
        'huang0447@itri.org.tw': '0315587',
        'baoan5669@gmail.com': '1003082',
        'zxcv70103@gmail.com': '0108108',
        'jhenjiahu@gmail.com': '1230016',
        'zxc52040@gmail.com': '0404983'
    }

    print(f"\\nApplying manual Join_ID corrections based on email...")
    # Apply overrides to T2 and T3 based on email mapping
    if t2_email_col:
        for email, new_id in overrides.items():
            t2.loc[t2['clean_email'] == email, 'Join_ID'] = new_id
    if t3_email_col:
        for email, new_id in overrides.items():
            t3.loc[t3['clean_email'] == email, 'Join_ID'] = new_id

    # Add the pre-cleaned T1 list as the baseline
    # User mentioned T1_0105_377_SPSS.csv is old and should be ignored, so we filter Raw T1
    t1_valid = filter_attention_check(t1, 'T1')

    # Filter invalid responses based on Attention Checks
    t2 = filter_attention_check(t2, 'T2')
    t3 = filter_attention_check(t3, 'T3')

    # Drop rows without meaningful Join_ID
    t1_valid = t1_valid[t1_valid['Join_ID'] != ""]
    t2 = t2[t2['Join_ID'] != ""]
    t3 = t3[t3['Join_ID'] != ""]

    # Give all T1 variables a _T1 suffix
    t1_cols_rename = {c: f"{c}_T1" for c in t1_valid.columns if c not in ['Join_ID', 'Custom_UID']}
    t1_valid = t1_valid.rename(columns=t1_cols_rename)
    
    # Give all T2 variables a _T2 suffix
    t2_cols_rename = {c: f"{c}_T2" for c in t2.columns if c not in ['Join_ID', 'clean_email']}
    t2 = t2.rename(columns=t2_cols_rename)
    
    # Give all T3 variables a _T3 suffix
    t3_cols_rename = {c: f"{c}_T3" for c in t3.columns if c not in ['Join_ID', 'clean_email']}
    t3 = t3.rename(columns=t3_cols_rename)

    # 1. Merge T1 and T2 (Inner Join to represent participants who successfully did T1 and T2 cleanly)
    merged_t1_t2 = pd.merge(t1_valid, t2, on='Join_ID', how='inner')
    print(f"\\nSuccessfully matched {len(merged_t1_t2)} respondents between clean T1 and valid T2.")
    
    # 2. Merge T1, T2, T3 (Inner Join to represent pure 3-phase valid retention)
    merged_t1_t2_t3 = pd.merge(merged_t1_t2, t3, on='Join_ID', how='inner')
    print(f"Successfully matched {len(merged_t1_t2_t3)} completely valid respondents who finished ALL 3 phases.")
    
    timestamp = (datetime.utcnow() + timedelta(hours=8)).strftime("%y%m%d%H%M")
    output_dir = f"analysis/{timestamp}_Longitudinal_Results"
    os.makedirs(output_dir, exist_ok=True)
    
    out_file_2phase = os.path.join(output_dir, f"T1_T2_Cleaned_Merged_{timestamp}.csv")
    merged_t1_t2.to_csv(out_file_2phase, index=False, encoding='utf-8-sig')
    print(f"\\n--- Output 1: T1 & T2 兩階段過濾後有效資料儲存至 {out_file_2phase}")

    out_file_3phase = os.path.join(output_dir, f"T1_T2_T3_Cleaned_Merged_{timestamp}.csv")
    merged_t1_t2_t3.to_csv(out_file_3phase, index=False, encoding='utf-8-sig')
    print(f"--- Output 2: T1, T2 & T3 三階段完全過濾後有效資料儲存至 {out_file_3phase}")

if __name__ == "__main__":
    run_longitudinal_analysis()
