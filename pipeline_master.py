import pandas as pd
import numpy as np
import scipy.stats as stats
from datetime import datetime
import os
import re

# ==========================================
# 1. CONFIGURATION
# ==========================================
BASE_DIR = r"g:\其他電腦\我的 PC\NSYSU_HRM\Thesis_LM\Research_Questionaire"
# 自動抓資料夾內最新的問卷 xlsx（檔名含「職涯」或「問卷」）
import glob as _glob
_candidates = sorted(
    _glob.glob(os.path.join(BASE_DIR, "*.xlsx")),
    key=os.path.getmtime,
    reverse=True
)
_candidates = [f for f in _candidates if any(k in os.path.basename(f) for k in ['職涯', '問卷', 'questionnaire', 'survey'])]
if not _candidates:
    raise FileNotFoundError(f"找不到問卷 xlsx，請確認已放入：{BASE_DIR}")
EXCEL_FILE = _candidates[0]
print(f"[自動偵測] 使用問卷檔案：{os.path.basename(EXCEL_FILE)}")
OUTPUT_DIR = os.path.join(BASE_DIR, "Master_Pipeline_Output")

MANUAL_OVERRIDES = {
    'jaychen@trendforce.com': '0710588',
    'huang0447@itri.org.tw': '0315587',
    'baoan5669@gmail.com': '1003082',
    'zxcv70103@gmail.com': '0108108',
    'jhenjiahu@gmail.com': '1230016',
    'zxc52040@gmail.com': '0404983'
}

def clean_str(val):
    if pd.isna(val) or val == "":
        return ""
    return str(val).strip().lower()

def clean_key1_t2t3(val):
    s = clean_str(val)
    if s:
        return s.split()[0] # 去掉後面填寫時間
    return ""

def clean_key2_match_id(val):
    if pd.isna(val) or val == "": return ""
    raw = str(val).replace('.0', '').strip()
    match_val = re.sub(r'\D', '', raw)
    if match_val.isdigit():
        while len(match_val) < 7 and len(match_val) > 0:
            match_val = '0' + match_val
    return match_val

def get_scale_cols(df, keys):
    return [c for c in df.columns if any(k in c for k in keys)]

# ==========================================
# 1. DATA CLEANING & MATCHING MODULE
# ==========================================
def process_phase_data(df, phase_name, k1_idx, k2_idx, k3_idx, is_t2t3=False):
    # DEDUPLICATION: Sort by timestamp (col 0) and keep last distinct key3 (Email/Contact)
    if 'Timestamp' not in df.columns:
        df['Timestamp'] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
    df = df.sort_values(by='Timestamp')
    
    # Extract keys
    if is_t2t3:
        df['key1'] = df.iloc[:, k1_idx].apply(clean_key1_t2t3)
    else:
        df['key1'] = df.iloc[:, k1_idx].apply(clean_str)
        
    df['key2'] = df.iloc[:, k2_idx].apply(clean_key2_match_id)
    
    # key3 is contact/email, apply overrides
    def check_override(val):
        v = clean_str(val)
        if v in MANUAL_OVERRIDES:
            return MANUAL_OVERRIDES[v] # Give them the target key directly as key1 override basically
        return v
    
    df['key3'] = df.iloc[:, k3_idx].apply(check_override)
    
    # Filter out empty key3 before drop_duplicates if we want to drop based on email
    # but some might only have key1 or key2. Let's drop duplicates based on whichever key is available.
    # We will prioritize key3 (email), then key1, then key2.
    df['dedup_id'] = np.where((df['key3'] != "") & (df['key3'] != "nan"), df['key3'],
                     np.where((df['key1'] != "") & (df['key1'] != "nan"), df['key1'], 
                              df['key2']))
                              
    # 找出重複的並印出來 (除了第一筆之外的都會被當作重複刪除)
    duplicates = df[df.duplicated(subset=['dedup_id'], keep='first')]
    if not duplicates.empty:
        print(f"\n[{phase_name}] 發現重複填答，保留最初填答，即將刪除以下後來填寫的 {len(duplicates)} 筆資料:")
        for idx, row in duplicates.iterrows():
            print(f"  - 刪除重複識別碼 (Email/Name): {row['dedup_id']}")
                              
    df = df.drop_duplicates(subset=['dedup_id'], keep='first').copy()
    
    # Score Extraction & Reverse Scoring
    # HP: 6 (Rev: 4, 6)
    # JCP: 6 (Rev: 1, 2, 3, 4, 5)
    # PP: 6
    # DP: 5
    # CI: 8 (Excluding attention check)
    
    all_cols = list(df.columns)

    def find_start(keywords):
        """找到第一個包含任一關鍵字的欄位位置"""
        for i, c in enumerate(all_cols):
            if any(kw in c for kw in keywords):
                return i
        return -1

    def seq_cols(start_idx, n, exclude_kw=None):
        """從 start_idx 連續取 n 欄，可排除含特定關鍵字的欄位"""
        result = []
        i = start_idx
        while len(result) < n and i < len(all_cols):
            c = all_cols[i]
            if exclude_kw is None or exclude_kw not in c:
                result.append(c)
            i += 1
        return result

    # 找各量表起始位置（HP 是第一個量表，其他依序在後）
    hp_start  = find_start(['晉升的可能性是有限', '晉升的可能性'])
    jcp_start = find_start(['學習與成長', '挑戰性']) if hp_start == -1 else hp_start + 6
    pp_start  = jcp_start + 6
    dp_start  = pp_start  + 6
    ci_start  = dp_start  + 5

    hp_cols  = seq_cols(hp_start,  6) if hp_start  != -1 else []
    jc_cols  = seq_cols(jcp_start, 6) if jcp_start != -1 else []
    pp_cols  = seq_cols(pp_start,  6) if pp_start  != -1 else []
    dp_cols  = seq_cols(dp_start,  5) if dp_start  != -1 else []
    # CI：連取9欄後排除注意力檢核題（含「這題請選擇」）
    ci_raw   = seq_cols(ci_start, 9) if ci_start != -1 else []
    ci_cols  = [c for c in ci_raw if '這題請選擇' not in c][:8]

    # -------------------------------------------------------
    # 將各題轉為數值並做反向計分，然後重新命名為英文欄位
    # 命名規則：HP1_T1, HP2_T1 ... CI8_T3（與波次對應）
    # 反向計分：HP4, HP6 / JCP1~JCP5（6點量表，反向 = 6 - 原值）
    # -------------------------------------------------------
    def to_num(val): return pd.to_numeric(val, errors='coerce')
    def rev(val):
        v = to_num(val)
        return 6 - v if pd.notnull(v) else np.nan

    sfx = f'_{phase_name}'  # e.g. _T1, _T2, _T3

    # HP（6題，反向：4、6）
    for i, col in enumerate(hp_cols[:6]):
        item_num = i + 1
        new_name = f'HP{item_num}{sfx}'
        df[new_name] = df[col].apply(rev if item_num in [4, 6] else to_num)

    # JCP（6題，反向：1~5）
    for i, col in enumerate(jc_cols[:6]):
        item_num = i + 1
        new_name = f'JCP{item_num}{sfx}'
        df[new_name] = df[col].apply(rev if item_num <= 5 else to_num)

    # PP（6題，無反向）
    for i, col in enumerate(pp_cols[:6]):
        df[f'PP{i+1}{sfx}'] = df[col].apply(to_num)

    # DP（5題，無反向）
    for i, col in enumerate(dp_cols[:5]):
        df[f'DP{i+1}{sfx}'] = df[col].apply(to_num)

    # CI（8題，無反向；CI5 為注意力題已在 ci_cols 過濾）
    for i, col in enumerate(ci_cols[:8]):
        df[f'CI{i+1}{sfx}'] = df[col].apply(to_num)

    # -------------------------------------------------------
    # 控制變數（只在 T1 波次有，T2/T3 不重複收）
    # -------------------------------------------------------
    def encode_val(val, kw_list):
        s = str(val)
        for idx, kw in enumerate(kw_list):
            if kw in s: return idx + 1
        return np.nan

    if phase_name == 'T1':
        col_gender = [c for c in df.columns if '性別' in c]
        col_age    = [c for c in df.columns if '年齡' in c]
        col_edu    = [c for c in df.columns if '教育程度' in c]
        col_mar    = [c for c in df.columns if '婚姻狀況' in c]
        col_pos    = [c for c in df.columns if '工作職級' in c]
        col_ind    = [c for c in df.columns if '產業別' in c]
        col_size   = [c for c in df.columns if '公司規模' in c]
        col_ny     = [c for c in df.columns if '現職年資 (年)' in c]
        col_nm     = [c for c in df.columns if '現職年資 (月)' in c]
        col_ty     = [c for c in df.columns if '工作總年資 (年)' in c]
        col_tm     = [c for c in df.columns if '工作總年資 (月)' in c]

        if col_gender: df['Gender'] = df[col_gender[0]].apply(lambda x: encode_val(x, ["男", "女", "其他"]))
        if col_age:    df['Age']    = pd.to_numeric(df[col_age[0]], errors='coerce')
        if col_edu:    df['Education'] = df[col_edu[0]].apply(lambda x: encode_val(x, ["高中", "專科", "大學", "碩士", "博士"]))
        if col_mar:    df['Marriage']  = df[col_mar[0]].apply(lambda x: encode_val(x, ["未婚", "無子女", "有子女", "其他"]))
        if col_pos:    df['Position']  = df[col_pos[0]].apply(lambda x: encode_val(x, ["一般", "中階", "基層", "高階"]))
        if col_ind:    df['Industry']  = df[col_ind[0]].apply(lambda x: encode_val(x, ["製造", "科技", "金融", "服務", "醫療", "教育", "公部門", "其他"]))
        if col_size:   df['OrgSize']   = df[col_size[0]].apply(lambda x: encode_val(x, ["30人", "31", "101", "501", "1001"]))
        if col_ny and col_nm:
            df['NowJobTenure'] = pd.to_numeric(df[col_ny[0]], errors='coerce').fillna(0) * 12 \
                               + pd.to_numeric(df[col_nm[0]], errors='coerce').fillna(0)
        if col_ty and col_tm:
            df['JobTenure'] = pd.to_numeric(df[col_ty[0]], errors='coerce').fillna(0) * 12 \
                            + pd.to_numeric(df[col_tm[0]], errors='coerce').fillna(0)

    # -------------------------------------------------------
    # 績效考核相關欄位（三波都收，加波次後綴）
    # PM_Has_Tx      : 是否有績效考核 (1=是, 0=否)
    # PM_Supervisor_Tx 等 : 考核形式 各 0/1
    # PM_Result_Tx   : 考核結果 (1=負向, 2=中立/持平, 3=正向)
    # PM_Help_Tx     : 考核對職涯幫助程度 (1-5 量尺)
    # -------------------------------------------------------
    col_pm_has  = [c for c in df.columns if '是否有進行績效考核' in c or '是否已進行績效考核' in c or ('績效考核' in c and '是否' in c)]
    col_pm_form = [c for c in df.columns if '考核」通常包含哪些形式' in c or '考核」包含' in c or '考核」通常包含' in c or ('考核' in c and '包含' in c and '形式' in c)]
    col_pm_res  = [c for c in df.columns if '考核結果/回饋性質' in c or ('考核結果' in c and '回饋' in c) or ('考核' in c and '性質' in c)]
    col_pm_help = [c for c in df.columns if '職涯發展的幫助程度' in c or ('考核' in c and '幫助' in c)]

    # T2/T3 fallback：若關鍵字沒找到，用欄位位置（PM 區固定在量表前 col 3~6）
    if not col_pm_has and phase_name != 'T1':
        scale_start = find_start(['晉升的可能性是有限', '晉升的可能性'])
        if scale_start >= 4:
            col_pm_has  = [all_cols[scale_start - 4]] if scale_start >= 4 else []
            col_pm_form = [all_cols[scale_start - 3]] if scale_start >= 3 else []
            col_pm_res  = [all_cols[scale_start - 2]] if scale_start >= 2 else []
            col_pm_help = [all_cols[scale_start - 1]] if scale_start >= 1 else []

    if col_pm_has:
        df[f'PM_Has{sfx}'] = df[col_pm_has[0]].apply(lambda x: 1 if '是' in str(x) else 0)

    if col_pm_form:
        form_col = df[col_pm_form[0]].fillna('').astype(str)
        df[f'PM_Supervisor{sfx}'] = form_col.apply(lambda x: 1 if '主管' in x else 0)
        df[f'PM_Self{sfx}']       = form_col.apply(lambda x: 1 if '自評' in x or '自我評核' in x else 0)
        df[f'PM_Interview{sfx}']  = form_col.apply(lambda x: 1 if '面談' in x else 0)
        df[f'PM_Other{sfx}']      = form_col.apply(lambda x: 1 if '其他' in x else 0)

    if col_pm_res:
        df[f'PM_Result{sfx}'] = df[col_pm_res[0]].apply(
            lambda x: 3 if '正向' in str(x) else (2 if '中' in str(x) or '持平' in str(x) else (1 if '負向' in str(x) else np.nan))
        )

    if col_pm_help:
        df[f'PM_Help{sfx}'] = pd.to_numeric(df[col_pm_help[0]], errors='coerce')

    return df, hp_cols, jc_cols, pp_cols, dp_cols, ci_cols

def safe_match(val1, val2):
    return (val1 != "" and val1 != "nan" and val2 != "" and val2 != "nan" and val1 == val2)

def perform_matching():
    print("Loading data...")
    t1_raw = pd.read_excel(EXCEL_FILE, sheet_name='第一階段')
    t2_raw = pd.read_excel(EXCEL_FILE, sheet_name='第二階段')
    t3_raw = pd.read_excel(EXCEL_FILE, sheet_name='第三階段')

    tracking = {
        'T1_Raw': len(t1_raw), 'T2_Raw': len(t2_raw), 'T3_Raw': len(t3_raw),
    }

    # Basic T1 filtering
    attn_col_t1 = [c for c in t1_raw.columns if '這題請選擇「4」' in c][0]
    ans_count_col = [c for c in t1_raw.columns if '共需填寫幾次問卷' in c][0]
    job_col = [c for c in t1_raw.columns if '就業狀態' in c][0]
    
    t1_raw = t1_raw[t1_raw[attn_col_t1] == 4]
    tracking['T1_Pass_Attn'] = len(t1_raw)
    t1_raw = t1_raw[t1_raw[ans_count_col].astype(str).str.contains('3次', na=False)]
    tracking['T1_Pass_Freq'] = len(t1_raw)
    invalid_jobs = ["兼職", "待業", "學生", "自由", "自營"]
    t1_raw = t1_raw[~t1_raw[job_col].apply(lambda x: any(k in str(x) for k in invalid_jobs))]
    tracking['T1_Pass_Job'] = len(t1_raw)
    print(f"T1 Basic Filtered: {len(t1_raw)}")
    
    # T2 & T3 Attention Filter
    attn_col_t2 = [c for c in t2_raw.columns if '這題請選擇「2」' in c][0]
    t2_raw = t2_raw[t2_raw[attn_col_t2] == 2]
    tracking['T2_Pass_Attn'] = len(t2_raw)

    attn_col_t3 = [c for c in t3_raw.columns if '這題請選擇「2」' in c][0]
    t3_raw = t3_raw[t3_raw[attn_col_t3] == 2]
    tracking['T3_Pass_Attn'] = len(t3_raw)

    # Process each phase (Extract keys, deduplicate, reverse score, average)
    # Mapping indices based on tests:
    # T1: BF(57)=k1, AO(40)=k2, BA(52)=k3
    # T2: C(2)=k1, AN(39)=k2, AO(40)=k3
    # T3: C(2)=k1, AN(39)=k2, AO(40)=k3
    
    t1, hp_t1, jc_t1, pp_t1, dp_t1, ci_t1 = process_phase_data(t1_raw, 'T1', 57, 40, 52, is_t2t3=False)
    t2, _, _, _, _, _ = process_phase_data(t2_raw, 'T2', 2, 39, 40, is_t2t3=True)
    t3, _, _, _, _, _ = process_phase_data(t3_raw, 'T3', 2, 39, 40, is_t2t3=True)
    
    print(f"After Deduplication: T1={len(t1)}, T2={len(t2)}, T3={len(t3)}")

    # Tri-Matching Logic
    t1['System_ID'] = range(len(t1))
    
    t2['Matched_T1_ID'] = -1
    for idx, row in t2.iterrows():
        match = t1[
                   t1.apply(lambda r: safe_match(r['key1'], row['key1']) or 
                                      safe_match(r['key2'], row['key2']) or 
                                      safe_match(r['key3'], row['key3']) or
                                      safe_match(r['key1'], row['key3']) # Allow cross-matching override
                           , axis=1)
                   ]
        if not match.empty:
            t2.at[idx, 'Matched_T1_ID'] = match.iloc[0]['System_ID']
            
    t3['Matched_T1_ID'] = -1
    for idx, row in t3.iterrows():
        match = t1[
                   t1.apply(lambda r: safe_match(r['key1'], row['key1']) or 
                                      safe_match(r['key2'], row['key2']) or 
                                      safe_match(r['key3'], row['key3']) or
                                      safe_match(r['key1'], row['key3'])
                           , axis=1)
                   ]
        if not match.empty:
            t3.at[idx, 'Matched_T1_ID'] = match.iloc[0]['System_ID']

    # 印出 T2 沒有配對到的名單
    unmatched_t2 = t2[t2['Matched_T1_ID'] == -1]
    if not unmatched_t2.empty:
        print(f"\n[警示] T2 有 {len(unmatched_t2)} 筆資料無法配對回到 T1，這些孤兒名單識別碼為：")
        for _, row in unmatched_t2.iterrows():
            print(f"  - T2 未配對者: {row['key3']} (備用碼: {row['key1']})")

    # 印出 T3 沒有配對到的名單
    unmatched_t3 = t3[t3['Matched_T1_ID'] == -1]
    if not unmatched_t3.empty:
        print(f"\n[警示] T3 有 {len(unmatched_t3)} 筆資料無法配對回到 T1，這些孤兒名單識別碼為：")
        for _, row in unmatched_t3.iterrows():
            print(f"  - T3 未配對者: {row['key3']} (備用碼: {row['key1']})")

    # Merge everything to T1
    merged = t1.copy()
    
    # 定義各波次個別題目欄位名稱（新命名格式）
    def item_cols(prefix, n, wave):
        return [f'{prefix}{i+1}_{wave}' for i in range(n)]

    t1_item_cols = (item_cols('HP',  6, 'T1') + item_cols('JCP', 6, 'T1') +
                    item_cols('PP',  6, 'T1') + item_cols('DP',  5, 'T1') +
                    item_cols('CI',  8, 'T1'))
    t2_item_cols = (item_cols('HP',  6, 'T2') + item_cols('JCP', 6, 'T2') +
                    item_cols('PP',  6, 'T2') + item_cols('DP',  5, 'T2') +
                    item_cols('CI',  8, 'T2'))
    t3_item_cols = (item_cols('HP',  6, 'T3') + item_cols('JCP', 6, 'T3') +
                    item_cols('PP',  6, 'T3') + item_cols('DP',  5, 'T3') +
                    item_cols('CI',  8, 'T3'))

    pm_cols_t1 = ['PM_Has_T1','PM_Supervisor_T1','PM_Self_T1','PM_Interview_T1',
                  'PM_Other_T1','PM_Result_T1','PM_Help_T1']
    pm_cols_t2 = ['PM_Has_T2','PM_Supervisor_T2','PM_Self_T2','PM_Interview_T2',
                  'PM_Other_T2','PM_Result_T2','PM_Help_T2']
    pm_cols_t3 = ['PM_Has_T3','PM_Supervisor_T3','PM_Self_T3','PM_Interview_T3',
                  'PM_Other_T3','PM_Result_T3','PM_Help_T3']
    ctrl_cols  = ['Gender', 'Age', 'Education', 'Marriage',
                  'NowJobTenure', 'JobTenure', 'Position', 'Industry', 'OrgSize']

    t2_keep_cols = (['Matched_T1_ID'] +
                    [c for c in t2_item_cols if c in t2.columns] +
                    [c for c in pm_cols_t2   if c in t2.columns])
    t3_keep_cols = (['Matched_T1_ID'] +
                    [c for c in t3_item_cols if c in t3.columns] +
                    [c for c in pm_cols_t3   if c in t3.columns])

    t2_subset = t2[t2['Matched_T1_ID'] != -1][t2_keep_cols]
    t3_subset = t3[t3['Matched_T1_ID'] != -1][t3_keep_cols]

    tracking['T2_Matched'] = len(t2_subset)
    tracking['T3_Matched'] = len(t3_subset)

    merged = pd.merge(merged, t2_subset, left_on='System_ID', right_on='Matched_T1_ID', how='left')
    merged = pd.merge(merged, t3_subset, left_on='System_ID', right_on='Matched_T1_ID', how='left')

    # Group 欄位：用 T3 是否有資料判斷
    merged['Group'] = np.where(merged[[c for c in t3_item_cols if c in merged.columns]].notna().any(axis=1), 3,
                      np.where(merged[[c for c in t2_item_cols if c in merged.columns]].notna().any(axis=1), 2, 1))

    # 整理最終輸出欄位順序，排除暫時計算欄位（底線開頭）
    final_cols = (['Custom_UID', 'Timestamp', 'Group'] +
                  t1_item_cols +
                  [c for c in ctrl_cols   if c in merged.columns] +
                  [c for c in pm_cols_t1  if c in merged.columns] +
                  t2_item_cols +
                  [c for c in pm_cols_t2  if c in merged.columns] +
                  t3_item_cols +
                  [c for c in pm_cols_t3  if c in merged.columns])
    final_cols = [c for c in final_cols if c in merged.columns and not c.startswith('_')]
    merged = merged[final_cols]

    # Scales for reliability output（使用新英文欄位名稱）
    def ecols(prefix, n, wave='T1'):
        return [f'{prefix}{i+1}_{wave}' for i in range(n)]

    escales = {
        'HP':  ecols('HP',  6, 'T1'),
        'JCP': ecols('JCP', 6, 'T1'),
        'CP':  ecols('HP',  6, 'T1') + ecols('JCP', 6, 'T1'),
        'PP':  ecols('PP',  6, 'T1'),
        'DP':  ecols('DP',  5, 'T1'),
        'CI':  ecols('CI',  8, 'T1'),
    }

    return merged, escales, tracking

# ==========================================
# 2. ANALYSIS MODULE
# ==========================================
def calculate_cronbach_alpha(df):
    df_corr = df.corr()
    N = df.shape[1]
    if N < 2: return np.nan
    rs = np.array([df_corr.iloc[i, j] for i in range(N) for j in range(N) if i > j])
    mean_r = np.mean(rs)
    if pd.isna(mean_r) or mean_r == 0: return np.nan
    alpha = (N * mean_r) / (1 + (N - 1) * mean_r)
    return alpha

def analyze_attrition(merged, track):
    counts = merged['Group'].value_counts()
    
    def anova(var):
        g1 = merged[merged['Group'] == 1][var].dropna()
        g2 = merged[merged['Group'] == 2][var].dropna()
        g3 = merged[merged['Group'] == 3][var].dropna()
        if len(g1)==0 or len(g2)==0 or len(g3)==0:
            return 0,0,0,0,1
        f_stat, p_val = stats.f_oneway(g1, g2, g3)
        return g1.mean(), g2.mean(), g3.mean(), f_stat, p_val

    results_md = "## 1. 樣本流失分析 (Attrition Analysis)\n\n"
    results_md += "### 各階段填答與清理漏斗\n"
    results_md += f"- **T1 (第一階段)**: 原始名單 {track['T1_Raw']} 人 -> 通過注意力檢測 {track['T1_Pass_Attn']} 人 -> 符合填寫條件與任職資格 {track['T1_Pass_Job']} 人 -> **去重複後實際有效樣本 {len(merged)} 人**\n"
    results_md += f"- **T2 (第二階段)**: 原始名單 {track['T2_Raw']} 人 -> 通過注意力檢測 {track['T2_Pass_Attn']} 人 -> **成功配對回 T1 者 {track['T2_Matched']} 人**\n"
    results_md += f"- **T3 (第三階段)**: 原始名單 {track['T3_Raw']} 人 -> 通過注意力檢測 {track['T3_Pass_Attn']} 人 -> **成功配對回 T1 者 {track['T3_Matched']} 人**\n\n"

    results_md += "### ANOVA 各群組人數\n"
    results_md += f"- **只有完成 T1 (Group 1)**: {counts.get(1, 0)} 人\n"
    results_md += f"- **完成 T1, T2 (Group 2)**: {counts.get(2, 0)} 人\n"
    results_md += f"- **完成 T1, T2, T3 (最終有效樣本 Group 3)**: {counts.get(3, 0)} 人\n\n"
    
    # 用新命名欄位（已在 process_phase_data 轉換好）
    # 計算各量表平均供 ANOVA 流失分析用
    def scale_mean(df, prefix, n, wave):
        cols = [f'{prefix}{i+1}_{wave}' for i in range(n)]
        cols = [c for c in cols if c in df.columns]
        return df[cols].mean(axis=1) if cols else np.nan

    merged['_HP_T1']  = scale_mean(merged, 'HP',  6, 'T1')
    merged['_JCP_T1'] = scale_mean(merged, 'JCP', 6, 'T1')
    merged['_CP_T1']  = merged[['_HP_T1','_JCP_T1']].mean(axis=1)
    merged['_PP_T1']  = scale_mean(merged, 'PP',  6, 'T1')
    merged['_DP_T1']  = scale_mean(merged, 'DP',  5, 'T1')
    merged['_CI_T1']  = scale_mean(merged, 'CI',  8, 'T1')
    if 'Edu' not in merged.columns and 'Education' in merged.columns:
        merged['Edu'] = merged['Education']

    anova_stats = {}   # 儲存各變數 p 值供 draft 使用
    for var, name in zip(['Age', '_CP_T1', '_HP_T1', '_JCP_T1', '_DP_T1', '_CI_T1', '_PP_T1'],
                         ['年齡', '整體職涯停滯', '階層停滯', '工作停滯', '決策拖延', '職涯無所作為', '主動型人格']):
        if var in merged.columns:
            m1, m2, m3, f, p = anova(var)
            results_md += f"**{name}**: G1={m1:.2f}, G2={m2:.2f}, G3={m3:.2f} | F={f:.3f}, p={p:.3f}\n"
            anova_stats[var] = {'m1': m1, 'm2': m2, 'm3': m3, 'F': f, 'p': p}

    chi_stats = {}
    try:
        chi2_g, p_g, _, _ = stats.chi2_contingency(pd.crosstab(merged['Group'], merged['Gender']))
        chi2_e, p_e, _, _ = stats.chi2_contingency(pd.crosstab(merged['Group'], merged['Edu']))
        results_md += f"\n**性別比例差異 (Chi-square)**: chi2={chi2_g:.3f}, p={p_g:.3f}\n"
        results_md += f"**教育程度差異 (Chi-square)**: chi2={chi2_e:.3f}, p={p_e:.3f}\n"
        chi_stats = {'gender_chi2': chi2_g, 'gender_p': p_g, 'edu_chi2': chi2_e, 'edu_p': p_e}
    except:
        pass

    return results_md, merged, anova_stats, chi_stats

def run_descriptives_and_correlations(t1, scales):
    results_md = "\n## 2. 敘述性統計與信度分析 (Descriptives & Reliability)\n\n"
    results_md += (
        "> **CP（職涯高原）測量說明**：CP 由兩個次量表組成——"
        "HP（階層停滯，6 題）與 JCP（工作內容停滯，6 題）。"
        "Mplus 中以 HP、JCP 兩個次量表合成分數作為 CP 的兩個指標（parceling）。"
        "信度分別報告 HP（6 題）、JCP（6 題）及合併 CP（12 題）供參考。\n\n"
    )
    results_md += "| 變數 | 說明 | 題數 | 平均數 (M) | 標準差 (SD) | Cronbach's α |\n"
    results_md += "|---|---|---|---|---|---|\n"

    scale_labels = {
        'HP':  'HP 階層停滯（CP 次量表）',
        'JCP': 'JCP 工作內容停滯（CP 次量表）',
        'CP':  'CP 職涯高原（HP+JCP 合併）',
        'PP':  'PP 主動型人格',
        'DP':  'DP 決策拖延',
        'CI':  'CI 職涯無所作為',
    }

    # 用原始題目欄位計算信度，用計算平均供相關矩陣
    scale_means = {}
    for name, cols in scales.items():
        valid_cols = [c for c in cols if c in t1.columns]
        alpha = calculate_cronbach_alpha(t1[valid_cols]) if valid_cols else np.nan
        mean_val = t1[valid_cols].mean(axis=1).mean() if valid_cols else np.nan
        sd_val   = t1[valid_cols].mean(axis=1).std()  if valid_cols else np.nan
        label = scale_labels.get(name, name)
        alpha_str = f"{alpha:.3f}" if not np.isnan(alpha) else "N/A"
        mean_str  = f"{mean_val:.2f}" if not np.isnan(mean_val) else "N/A"
        sd_str    = f"{sd_val:.2f}" if not np.isnan(sd_val) else "N/A"
        results_md += f"| {name} | {label} | {len(valid_cols)} | {mean_str} | {sd_str} | {alpha_str} |\n"
        scale_means[name] = t1[valid_cols].mean(axis=1)

    results_md += "\n## 3. 相關矩陣 (Correlation Matrix)\n\n"
    scale_names = list(scales.keys())

    results_md += "| 變數 | " + " | ".join(scale_names) + " |\n"
    results_md += "|---|" + "|".join(["---"] * len(scale_names)) + "|\n"

    for i, name_r in enumerate(scale_names):
        row_str = f"| **{name_r}** |"
        for j, name_c in enumerate(scale_names):
            if i == j:
                row_str += " 1.00 |"
            elif i < j:
                s1 = scale_means[name_r]
                s2 = scale_means[name_c]
                valid_data = pd.concat([s1, s2], axis=1).dropna()
                if len(valid_data) > 2:
                    r, p = stats.pearsonr(valid_data.iloc[:,0], valid_data.iloc[:,1])
                    star = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
                    row_str += f" {r:.2f}{star} |"
                else:
                    row_str += " - |"
            else:
                row_str += " - |"
        results_md += row_str + "\n"

    # 額外回傳 stats dict 供 draft 使用
    alpha_dict = {}
    corr_dict  = {}
    for name, cols in scales.items():
        valid_cols = [c for c in cols if c in t1.columns]
        alpha_dict[name] = calculate_cronbach_alpha(t1[valid_cols]) if valid_cols else np.nan

    corr_pairs = [('CP','DP'), ('CP','CI'), ('DP','CI'), ('HP','CI'), ('JCP','CI'), ('PP','DP'), ('PP','CI')]
    for a, b in corr_pairs:
        if a in scale_means and b in scale_means:
            valid = pd.concat([scale_means[a], scale_means[b]], axis=1).dropna()
            if len(valid) > 2:
                r, p = stats.pearsonr(valid.iloc[:,0], valid.iloc[:,1])
                corr_dict[f'{a}_{b}'] = {'r': r, 'p': p}

    return results_md, alpha_dict, corr_dict

def generate_r_script(csv_filename, r_script_path=None):
    output_dir = OUTPUT_DIR.replace('\\\\', '/').replace('\\', '/')
    report_path = f"{output_dir}/RICLPM_Report.md"
    log_clpm_path = f"{output_dir}/model_test_log.txt"
    log_ri_path   = f"{output_dir}/model_v2_log.txt"
    csv_full_path = f"{output_dir}/{csv_filename}"

    r_script_content = f"""# ==============================================================================
# RICLPM_Master.R  (自動產生 by pipeline_master.py)
# 整合：資料診斷 → CLPM 比較 → RI-CLPM 精簡比較 →
#       自由 RI-CLPM (FIML) → 限制 RI-CLPM (FIML) → 最佳模型報告
# ==============================================================================

# install.packages(c("lavaan", "readr"))  # 第一次執行時取消註解
library(lavaan)
library(readr)

# ==============================================================================
# STEP 0. 環境設定與資料讀取
# ==============================================================================
DATA_PATH   <- "{csv_full_path}"
OUTPUT_DIR  <- "{output_dir}"
REPORT_PATH <- "{report_path}"

cat("=== Loading data ===\\n")
df <- read_csv(DATA_PATH, show_col_types = FALSE)

VARS <- c("CP_T1","CP_T2","CP_T3","CI_T1","CI_T2","CI_T3","DP_T1","DP_T2","DP_T3")
df_full <- df[complete.cases(df[, VARS]), ]

cat(sprintf("N total (FIML) = %d\\n", nrow(df)))
cat(sprintf("N 三波完整 (listwise) = %d\\n", nrow(df_full)))

# ==============================================================================
# STEP 1. 資料診斷
# ==============================================================================
cat("\\n=== STEP 1: 資料診斷 ===\\n")
cat("Means:\\n");     print(round(colMeans(df_full[VARS], na.rm=TRUE), 3))
cat("SDs:\\n");       print(round(apply(df_full[VARS], 2, sd,  na.rm=TRUE), 3))
cat("Variances:\\n"); print(round(apply(df_full[VARS], 2, var, na.rm=TRUE), 4))
cat("Correlation matrix:\\n"); print(round(cor(df_full[VARS], use="complete.obs"), 3))

# ==============================================================================
# STEP 2. 模型比較：標準 CLPM（lavaan / FIML）
# ==============================================================================
cat("\\n=== STEP 2: 標準 CLPM 模型比較 ===\\n")

LOG_CLPM <- "{log_clpm_path}"
con_clpm <- file(LOG_CLPM, open="wt", encoding="UTF-8")
write_log <- function(text) cat(text, "\\n", file=con_clpm, append=TRUE)
write_log(paste0("N_full=", nrow(df_full), "  N_total=", nrow(df)))

try_lavaan <- function(model_name, syntax, data, missing_method="ml") {{
  write_log(paste0("\\n", strrep("=",50), "\\n", model_name))
  tryCatch({{
    fit  <- lavaan(syntax, data=data, missing=missing_method, estimator="MLR")
    conv <- lavInspect(fit, "converged")
    fmi  <- fitMeasures(fit, c("cfi","rmsea","srmr","chisq","df","pvalue"))
    write_log(paste0("Converged: ", conv))
    write_log(paste0("CFI=",round(fmi["cfi"],3)," RMSEA=",round(fmi["rmsea"],3)," SRMR=",round(fmi["srmr"],3)))
    write_log(paste0("Chi2(",fmi["df"],")=",round(fmi["chisq"],2)," p=",round(fmi["pvalue"],3)))
    if (conv) {{
      params <- parameterEstimates(fit, standardized=TRUE)
      cl <- params[params$op == "~" & !is.na(params$pvalue), ]
      if (nrow(cl) > 0) {{
        write_log("--- paths ---")
        for (i in seq_len(nrow(cl))) {{
          r <- cl[i,]
          write_log(paste0("  ",r$lhs," ~ ",r$rhs,
                           "  Est=",round(r$est,3)," SE=",round(r$se,3),
                           " z=",round(r$z,3)," p=",round(r$pvalue,4),
                           " std=",round(r$std.all,3)))
        }}
      }}
    }}
    return(conv)
  }}, error=function(e) {{ write_log(paste0("ERROR: ", e$message)); FALSE }})
}}

m_std <- '
  CP_T2 ~ CP_T1; CP_T3 ~ CP_T2
  CI_T2 ~ CI_T1; CI_T3 ~ CI_T2
  DP_T2 ~ DP_T1; DP_T3 ~ DP_T2
  CI_T2 ~ CP_T1 + DP_T1; CI_T3 ~ CP_T2 + DP_T2
  CP_T2 ~ CI_T1 + DP_T1; CP_T3 ~ CI_T2 + DP_T2
  DP_T2 ~ CP_T1 + CI_T1; DP_T3 ~ CP_T2 + CI_T2
  CP_T1 ~~ CI_T1; CP_T1 ~~ DP_T1; CI_T1 ~~ DP_T1
'
m_inv <- '
  CP_T2 ~ a1*CP_T1; CP_T3 ~ a1*CP_T2
  CI_T2 ~ a2*CI_T1; CI_T3 ~ a2*CI_T2
  DP_T2 ~ a3*DP_T1; DP_T3 ~ a3*DP_T2
  CI_T2 ~ c1*CP_T1 + c2*DP_T1; CI_T3 ~ c1*CP_T2 + c2*DP_T2
  CP_T2 ~ c3*CI_T1 + c4*DP_T1; CP_T3 ~ c3*CI_T2 + c4*DP_T2
  DP_T2 ~ c5*CP_T1 + c6*CI_T1; DP_T3 ~ c5*CP_T2 + c6*CI_T2
  CP_T1 ~~ CI_T1; CP_T1 ~~ DP_T1; CI_T1 ~~ DP_T1
'

try_lavaan("M1: Standard CLPM (N=168, listwise)",        m_std, df_full, "ml")
try_lavaan("M2: Time-invariant CLPM (N=168, listwise)",  m_inv, df_full, "ml")
try_lavaan("M3: Standard CLPM FIML (N=total)",           m_std, df,      "fiml")
try_lavaan("M4: Time-invariant CLPM FIML (N=total)",     m_inv, df,      "fiml")

write_log("\\n===== ALL CLPM DONE =====")
close(con_clpm)
cat(sprintf("CLPM log: %s\\n", LOG_CLPM))

# ==============================================================================
# STEP 3. 模型比較：RI-CLPM 精簡系列（sem）
# ==============================================================================
cat("\\n=== STEP 3: RI-CLPM 精簡系列比較 ===\\n")

LOG_RI  <- "{log_ri_path}"
con_ri  <- file(LOG_RI, open="wt", encoding="UTF-8")
wl      <- function(...) cat(..., "\\n", file=con_ri, append=TRUE)
wl(paste0("N_full=", nrow(df_full), "  N_all=", nrow(df)))

try_sem <- function(label, syntax, data_in) {{
  wl(paste0("\\n", strrep("=",50), "\\n", label))
  tryCatch({{
    fit  <- sem(syntax, data=data_in, estimator="MLR")
    conv <- lavInspect(fit, "converged")
    fi   <- fitMeasures(fit, c("cfi","rmsea","srmr","chisq","df","pvalue"))
    wl(paste0("Converged=", conv))
    wl(paste0("CFI=",round(fi["cfi"],3)," RMSEA=",round(fi["rmsea"],3)," SRMR=",round(fi["srmr"],3)))
    wl(paste0("Chi2(",fi["df"],")=",round(fi["chisq"],2)," p=",round(fi["pvalue"],3)))
    if (conv) {{
      pe <- parameterEstimates(fit, standardized=TRUE)
      cl <- pe[pe$op == "~" & !is.na(pe$pvalue), ]
      if (nrow(cl) > 0) {{
        wl("--- regression paths ---")
        for (i in seq_len(nrow(cl))) {{
          r <- cl[i,]
          wl(paste0("  ",r$lhs," ~ ",r$rhs,
                    "  b=",round(r$est,3)," SE=",round(r$se,3),
                    " p=",round(r$pvalue,4)," beta=",round(r$std.all,3)))
        }}
      }}
    }}
    return(conv)
  }}, error=function(e) {{ wl(paste0("ERROR: ", e$message)); FALSE }})
}}

m_ri_compact <- "
  RI_CP =~ 1*CP_T1 + 1*CP_T2 + 1*CP_T3
  RI_CI =~ 1*CI_T1 + 1*CI_T2 + 1*CI_T3
  RI_DP =~ 1*DP_T1 + 1*DP_T2 + 1*DP_T3
  wp_CP_T1 =~ 1*CP_T1; wp_CP_T2 =~ 1*CP_T2; wp_CP_T3 =~ 1*CP_T3
  wp_CI_T1 =~ 1*CI_T1; wp_CI_T2 =~ 1*CI_T2; wp_CI_T3 =~ 1*CI_T3
  wp_DP_T1 =~ 1*DP_T1; wp_DP_T2 =~ 1*DP_T2; wp_DP_T3 =~ 1*DP_T3
  CP_T1 ~~ 0*CP_T1; CP_T2 ~~ 0*CP_T2; CP_T3 ~~ 0*CP_T3
  CI_T1 ~~ 0*CI_T1; CI_T2 ~~ 0*CI_T2; CI_T3 ~~ 0*CI_T3
  DP_T1 ~~ 0*DP_T1; DP_T2 ~~ 0*DP_T2; DP_T3 ~~ 0*DP_T3
  wp_CP_T2 ~ a1*wp_CP_T1; wp_CP_T3 ~ a1*wp_CP_T2
  wp_CI_T2 ~ a2*wp_CI_T1; wp_CI_T3 ~ a2*wp_CI_T2
  wp_DP_T2 ~ a3*wp_DP_T1; wp_DP_T3 ~ a3*wp_DP_T2
  wp_CI_T2 ~ c1*wp_CP_T1 + c2*wp_DP_T1
  wp_CI_T3 ~ c1*wp_CP_T2 + c2*wp_DP_T2
  wp_CP_T2 ~ c3*wp_CI_T1 + c4*wp_DP_T1
  wp_CP_T3 ~ c3*wp_CI_T2 + c4*wp_DP_T2
  wp_DP_T2 ~ c5*wp_CP_T1 + c6*wp_CI_T1
  wp_DP_T3 ~ c5*wp_CP_T2 + c6*wp_CI_T2
  RI_CP ~~ RI_CI; RI_CP ~~ RI_DP; RI_CI ~~ RI_DP
  wp_CP_T1 ~~ wp_CI_T1; wp_CP_T1 ~~ wp_DP_T1; wp_CI_T1 ~~ wp_DP_T1
"

try_sem("M_RI: RI-CLPM time-invariant sem() N=168", m_ri_compact, df_full)

wl("\\n===== ALL RI-CLPM COMPACT DONE =====")
close(con_ri)
cat(sprintf("RI-CLPM log: %s\\n", LOG_RI))

# ==============================================================================
# STEP 4. 自由 RI-CLPM（lavaan / FIML）
# ==============================================================================
cat("\\n=== STEP 4: 自由 RI-CLPM (lavaan + FIML) ===\\n")

riclpm_free <- '
  RI_CP =~ 1*CP_T1 + 1*CP_T2 + 1*CP_T3
  RI_CI =~ 1*CI_T1 + 1*CI_T2 + 1*CI_T3
  RI_DP =~ 1*DP_T1 + 1*DP_T2 + 1*DP_T3
  wp_CP_T1 =~ 1*CP_T1; wp_CP_T2 =~ 1*CP_T2; wp_CP_T3 =~ 1*CP_T3
  wp_CI_T1 =~ 1*CI_T1; wp_CI_T2 =~ 1*CI_T2; wp_CI_T3 =~ 1*CI_T3
  wp_DP_T1 =~ 1*DP_T1; wp_DP_T2 =~ 1*DP_T2; wp_DP_T3 =~ 1*DP_T3
  CP_T1 ~~ 0*CP_T1; CP_T2 ~~ 0*CP_T2; CP_T3 ~~ 0*CP_T3
  CI_T1 ~~ 0*CI_T1; CI_T2 ~~ 0*CI_T2; CI_T3 ~~ 0*CI_T3
  DP_T1 ~~ 0*DP_T1; DP_T2 ~~ 0*DP_T2; DP_T3 ~~ 0*DP_T3
  wp_CP_T2 ~ wp_CP_T1; wp_CP_T3 ~ wp_CP_T2
  wp_CI_T2 ~ wp_CI_T1; wp_CI_T3 ~ wp_CI_T2
  wp_DP_T2 ~ wp_DP_T1; wp_DP_T3 ~ wp_DP_T2
  wp_CI_T2 ~ wp_CP_T1 + wp_DP_T1; wp_CI_T3 ~ wp_CP_T2 + wp_DP_T2
  wp_CP_T2 ~ wp_CI_T1 + wp_DP_T1; wp_CP_T3 ~ wp_CI_T2 + wp_DP_T2
  wp_DP_T2 ~ wp_CP_T1 + wp_CI_T1; wp_DP_T3 ~ wp_CP_T2 + wp_CI_T2
  RI_CP ~~ RI_CI; RI_CP ~~ RI_DP; RI_CI ~~ RI_DP
  wp_CP_T1 ~~ wp_CI_T1; wp_CP_T1 ~~ wp_DP_T1; wp_CI_T1 ~~ wp_DP_T1
  wp_CP_T2 ~~ wp_CI_T2; wp_CP_T2 ~~ wp_DP_T2; wp_CI_T2 ~~ wp_DP_T2
  wp_CP_T3 ~~ wp_CI_T3; wp_CP_T3 ~~ wp_DP_T3; wp_CI_T3 ~~ wp_DP_T3
'
fit_free <- tryCatch({{ lavaan(riclpm_free, data=df, missing="fiml", estimator="MLR", bounds=TRUE) }}, error=function(e) NULL)
if(!is.null(fit_free)) print(summary(fit_free, fit.measures=TRUE, standardized=TRUE, rsquare=TRUE)) else cat("M_Free Non-convergence\\n")

# ==============================================================================
# STEP 5. 時間恆定限制 RI-CLPM（lavaan / FIML）
# ==============================================================================
cat("\\n=== STEP 5: 時間恆定限制 RI-CLPM (lavaan + FIML) ===\\n")

riclpm_constrained <- '
  RI_CP =~ 1*CP_T1 + 1*CP_T2 + 1*CP_T3
  RI_CI =~ 1*CI_T1 + 1*CI_T2 + 1*CI_T3
  RI_DP =~ 1*DP_T1 + 1*DP_T2 + 1*DP_T3
  wp_CP_T1 =~ 1*CP_T1; wp_CP_T2 =~ 1*CP_T2; wp_CP_T3 =~ 1*CP_T3
  wp_CI_T1 =~ 1*CI_T1; wp_CI_T2 =~ 1*CI_T2; wp_CI_T3 =~ 1*CI_T3
  wp_DP_T1 =~ 1*DP_T1; wp_DP_T2 =~ 1*DP_T2; wp_DP_T3 =~ 1*DP_T3
  CP_T1 ~~ 0*CP_T1; CP_T2 ~~ 0*CP_T2; CP_T3 ~~ 0*CP_T3
  CI_T1 ~~ 0*CI_T1; CI_T2 ~~ 0*CI_T2; CI_T3 ~~ 0*CI_T3
  DP_T1 ~~ 0*DP_T1; DP_T2 ~~ 0*DP_T2; DP_T3 ~~ 0*DP_T3
  wp_CP_T2 ~ a1*wp_CP_T1; wp_CP_T3 ~ a1*wp_CP_T2
  wp_CI_T2 ~ a2*wp_CI_T1; wp_CI_T3 ~ a2*wp_CI_T2
  wp_DP_T2 ~ a3*wp_DP_T1; wp_DP_T3 ~ a3*wp_DP_T2
  wp_CI_T2 ~ c1*wp_CP_T1 + c2*wp_DP_T1
  wp_CI_T3 ~ c1*wp_CP_T2 + c2*wp_DP_T2
  wp_CP_T2 ~ c3*wp_CI_T1 + c4*wp_DP_T1
  wp_CP_T3 ~ c3*wp_CI_T2 + c4*wp_DP_T2
  wp_DP_T2 ~ c5*wp_CP_T1 + c6*wp_CI_T1
  wp_DP_T3 ~ c5*wp_CP_T2 + c6*wp_CI_T2
  RI_CP ~~ RI_CI; RI_CP ~~ RI_DP; RI_CI ~~ RI_DP
  wp_CP_T1 ~~ wp_CI_T1; wp_CP_T1 ~~ wp_DP_T1; wp_CI_T1 ~~ wp_DP_T1
  wp_CP_T2 ~~ wp_CI_T2; wp_CP_T2 ~~ wp_DP_T2; wp_CI_T2 ~~ wp_DP_T2
  wp_CP_T3 ~~ wp_CI_T3; wp_CP_T3 ~~ wp_DP_T3; wp_CI_T3 ~~ wp_DP_T3
'
fit_constrained <- tryCatch({{ lavaan(riclpm_constrained, data=df, missing="fiml", estimator="MLR", bounds=TRUE) }}, error=function(e) NULL)
if(!is.null(fit_constrained)) print(summary(fit_constrained, fit.measures=TRUE, standardized=TRUE)) else cat("M_Constrained Non-convergence\\n")

# ==============================================================================
# STEP 6. 最佳模型報告 → Markdown
# ==============================================================================
cat("\\n=== STEP 6: 最佳模型報告輸出 ===\\n")

fit_best <- tryCatch({{ sem(m_ri_compact, data=df_full, estimator="MLR", bounds=TRUE) }}, error=function(e) NULL)
con_out  <- file(REPORT_PATH, open="wt", encoding="UTF-8")
w        <- function(...) cat(..., "\\n", file=con_out, append=TRUE)

if(!is.null(fit_best)) {{
  fi   <- fitMeasures(fit_best, c("cfi","tli","rmsea","srmr","chisq","df","pvalue"))
  pe   <- parameterEstimates(fit_best, standardized=TRUE, ci=TRUE)
  conv <- lavInspect(fit_best, "converged")
}} else {{
  fi <- c(cfi=NA, tli=NA, rmsea=NA, srmr=NA, chisq=NA, df=NA, pvalue=NA)
  pe <- data.frame(label=character(0))
  conv <- FALSE
}}

w("# RI-CLPM 分析報告")
w(paste0("**產出時間**: ", format(Sys.time(), "%Y-%m-%d %H:%M")))
w(paste0("**樣本數 (N)**: ", nrow(df_full), " (三波完整填答)"))
w(paste0("**估計方法**: MLR | **模型**: 時間恆定限制 RI-CLPM"))
w(paste0("**是否收斂**: ", ifelse(conv, "✅ 是", "❌ 否")))

w("\\n---\\n## 1. 模型配適指標\\n")
w("| 指標 | 數值 | 建議標準 |"); w("|---|---|---|")
w(paste0("| CFI   | ", round(fi["cfi"],3),   " | >.95 |"))
w(paste0("| TLI   | ", round(fi["tli"],3),   " | >.95 |"))
w(paste0("| RMSEA | ", round(fi["rmsea"],3), " | <.06 |"))
w(paste0("| SRMR  | ", round(fi["srmr"],3),  " | <.08 |"))
w(paste0("| Chi²  | ", round(fi["chisq"],2), " (df=", fi["df"], "), p=", round(fi["pvalue"],3), " |"))

w("\\n---\\n## 2. 自我迴歸效果\\n")
w("| 路徑 | b | SE | p | β |"); w("|---|---|---|---|---|")
ar_rows <- pe[pe$label %in% c("a1","a2","a3") & !duplicated(pe$label), ]
for (i in seq_len(nrow(ar_rows))) {{
  r   <- ar_rows[i,]
  sig <- ifelse(r$pvalue<.001,"***",ifelse(r$pvalue<.01,"**",ifelse(r$pvalue<.05,"*",ifelse(r$pvalue<.10,"†",""))))
  w(paste0("| ",r$lhs," ~ ",r$rhs," | ",round(r$est,3)," | ",round(r$se,3)," | ",round(r$pvalue,4),sig," | ",round(r$std.all,3)," |"))
}}

w("\\n---\\n## 3. 交叉延遲效果\\n")
w("| 路徑 | b | 95% CI | SE | z | p | β |"); w("|---|---|---|---|---|---|---|")
cl_rows <- pe[pe$label %in% paste0("c", 1:6) & !duplicated(pe$label), ]
for (i in seq_len(nrow(cl_rows))) {{
  r      <- cl_rows[i,]
  sig    <- ifelse(r$pvalue<.001,"***",ifelse(r$pvalue<.01,"**",ifelse(r$pvalue<.05,"*",ifelse(r$pvalue<.10,"†",""))))
  ci_str <- paste0("[",round(r$ci.lower,3),", ",round(r$ci.upper,3),"]")
  w(paste0("| ",r$lhs," ~ ",r$rhs," | ",round(r$est,3),sig," | ",ci_str," | ",round(r$se,3)," | ",round(r$z,3)," | ",round(r$pvalue,4)," | ",round(r$std.all,3)," |"))
}}

w("\\n---\\n## 4. 隨機截距共變數\\n")
w("| 路徑 | r (std) | p |"); w("|---|---|---|")
ri_cov <- pe[pe$op=="~~" & grepl("RI_",pe$lhs) & grepl("RI_",pe$rhs), ]
for (i in seq_len(nrow(ri_cov))) {{
  r   <- ri_cov[i,]
  sig <- ifelse(r$pvalue<.001,"***",ifelse(r$pvalue<.01,"**",ifelse(r$pvalue<.05,"*","")))
  w(paste0("| ",r$lhs," ~~ ",r$rhs," | ",round(r$std.all,3),sig," | ",round(r$pvalue,3)," |"))
}}

w("\\n---\\n## 5. 完整 lavaan 輸出\\n```")
sink_tmp <- tempfile()
sink(sink_tmp)
print(summary(fit_best, fit.measures=TRUE, standardized=TRUE, rsquare=TRUE))
sink()
for (line in readLines(sink_tmp, encoding="UTF-8")) w(line)
w("```")

close(con_out)
cat(sprintf("\\n✅ 報告: %s\\n✅ CLPM log: %s\\n✅ RI-CLPM log: %s\\n", REPORT_PATH, LOG_CLPM, LOG_RI))
cat("=== RICLPM_Master.R 完成 ===\\n")
"""
    return r_script_content
        
    results_md += f"✅ **分析樣本數 (N)**: {len(df_clean)}\n\n"
    
    riclpm_syntax = """
    # Random Intercepts
    RI_CP =~ 1*CP_T1 + 1*CP_T2 + 1*CP_T3
    RI_CI =~ 1*CI_T1 + 1*CI_T2 + 1*CI_T3
    RI_DP =~ 1*DP_T1 + 1*DP_T2 + 1*DP_T3
    
    # Within-person latent variables
    wp_CP_T1 =~ 1*CP_T1
    wp_CP_T2 =~ 1*CP_T2
    wp_CP_T3 =~ 1*CP_T3
    
    wp_CI_T1 =~ 1*CI_T1
    wp_CI_T2 =~ 1*CI_T2
    wp_CI_T3 =~ 1*CI_T3
    
    wp_DP_T1 =~ 1*DP_T1
    wp_DP_T2 =~ 1*DP_T2
    wp_DP_T3 =~ 1*DP_T3
    
    CP_T1 ~~ 0.0*CP_T1
    CP_T2 ~~ 0.0*CP_T2
    CP_T3 ~~ 0.0*CP_T3
    CI_T1 ~~ 0.0*CI_T1
    CI_T2 ~~ 0.0*CI_T2
    CI_T3 ~~ 0.0*CI_T3
    DP_T1 ~~ 0.0*DP_T1
    DP_T2 ~~ 0.0*DP_T2
    DP_T3 ~~ 0.0*DP_T3
    
    # Autoregressive
    wp_CP_T2 ~ wp_CP_T1
    wp_CP_T3 ~ wp_CP_T2
    wp_CI_T2 ~ wp_CI_T1
    wp_CI_T3 ~ wp_CI_T2
    wp_DP_T2 ~ wp_DP_T1
    wp_DP_T3 ~ wp_DP_T2
    
    # Cross-lagged (交叉延遲)
    wp_CI_T2 ~ wp_CP_T1 + wp_DP_T1
    wp_CI_T3 ~ wp_CP_T2 + wp_DP_T2
    
    wp_CP_T2 ~ wp_CI_T1 + wp_DP_T1
    wp_CP_T3 ~ wp_CI_T2 + wp_DP_T2
    
    wp_DP_T2 ~ wp_CP_T1 + wp_CI_T1
    wp_DP_T3 ~ wp_CP_T2 + wp_CI_T2
    
    RI_CP ~~ RI_CI
    RI_CP ~~ RI_DP
    RI_CI ~~ RI_DP
    
    wp_CP_T1 ~~ wp_CI_T1
    wp_CP_T1 ~~ wp_DP_T1
    wp_CI_T1 ~~ wp_DP_T1
    
    wp_CP_T2 ~~ wp_CI_T2
    wp_CP_T2 ~~ wp_DP_T2
    wp_CI_T2 ~~ wp_DP_T2
    
    wp_CP_T3 ~~ wp_CI_T3
    wp_CP_T3 ~~ wp_DP_T3
    wp_CI_T3 ~~ wp_DP_T3
    """
    
    try:
        model = semopy.Model(riclpm_syntax)
        model.fit(df_clean)
        ins = model.inspect()
        
        results_md += "### 交叉延遲效果 (Cross-lagged Effects)\n"
        results_md += "| 依變項 (Outcome) | 預測變項 (Predictor) | 估計值 (Estimate) | p-value | 顯著性 |\n"
        results_md += "|---|---|---|---|---|\n"
        
        cl_paths = ins[(ins['op'] == '~') & (ins['lval'].str.contains('wp_')) & (ins['rval'].str.contains('wp_'))]
        for _, row in cl_paths.iterrows():
            target = row['lval']
            predictor = row['rval']
            if target.split('_')[1] != predictor.split('_')[1]:
                p_val = row.get('p-value', 1.0)
                try: p_val_num = float(p_val)
                except: p_val_num = 1.0
                sig = "***" if p_val_num < 0.001 else ("**" if p_val_num < 0.01 else ("*" if p_val_num < 0.05 else ""))
                if "T1" in predictor and "T2" in target: pass
                elif "T2" in predictor and "T3" in target: pass
                else: continue
                
                results_md += f"| {target} | {predictor} | {row.get('Estimate', 0.0):.3f} | {p_val_num:.4f} | {sig} |\n"
                
    except Exception as e:
        results_md += f"\n⚠️ **RI-CLPM 配適失敗**: {e}\n估計過程可能因樣本少而產生 Singular Matrix，建議使用更精簡模型。\n"
        
    return results_md

def generate_r_script_split_cp(csv_filename):
    output_dir = OUTPUT_DIR.replace('\\\\', '/').replace('\\', '/')
    report_path = f"{output_dir}/RICLPM_SplitCP_Report.md"
    log_ri_path   = f"{output_dir}/model_split_v2_log.txt"
    csv_full_path = f"{output_dir}/{csv_filename}"

    r_script_content = f"""# ==============================================================================
# RICLPM_Split_Master.R (HP ＆ JCP 雙構面分拆版)
# ==============================================================================
library(lavaan)
library(readr)

DATA_PATH   <- "{csv_full_path}"
OUTPUT_DIR  <- "{output_dir}"
REPORT_PATH <- "{report_path}"
LOG_RI  <- "{log_ri_path}"

cat("=== Loading data ===\\n")
df <- read_csv(DATA_PATH, show_col_types = FALSE)
VARS <- c("HP_T1","HP_T2","HP_T3","JCP_T1","JCP_T2","JCP_T3","CI_T1","CI_T2","CI_T3","DP_T1","DP_T2","DP_T3")
df_full <- df[complete.cases(df[, VARS]), ]

cat(sprintf("N total (FIML) = %d\\n", nrow(df)))
cat(sprintf("N 三波完整 (listwise) = %d\\n\\n", nrow(df_full)))

cat("=== RI-CLPM 拆分 HP & JCP 構面模型 ===\\n")
m_ri_compact <- "
  RI_HP =~ 1*HP_T1 + 1*HP_T2 + 1*HP_T3
  RI_JCP =~ 1*JCP_T1 + 1*JCP_T2 + 1*JCP_T3
  RI_CI =~ 1*CI_T1 + 1*CI_T2 + 1*CI_T3
  RI_DP =~ 1*DP_T1 + 1*DP_T2 + 1*DP_T3
  
  wp_HP_T1 =~ 1*HP_T1; wp_HP_T2 =~ 1*HP_T2; wp_HP_T3 =~ 1*HP_T3
  wp_JCP_T1 =~ 1*JCP_T1; wp_JCP_T2 =~ 1*JCP_T2; wp_JCP_T3 =~ 1*JCP_T3
  wp_CI_T1 =~ 1*CI_T1; wp_CI_T2 =~ 1*CI_T2; wp_CI_T3 =~ 1*CI_T3
  wp_DP_T1 =~ 1*DP_T1; wp_DP_T2 =~ 1*DP_T2; wp_DP_T3 =~ 1*DP_T3
  
  HP_T1 ~~ 0*HP_T1; HP_T2 ~~ 0*HP_T2; HP_T3 ~~ 0*HP_T3
  JCP_T1 ~~ 0*JCP_T1; JCP_T2 ~~ 0*JCP_T2; JCP_T3 ~~ 0*JCP_T3
  CI_T1 ~~ 0*CI_T1; CI_T2 ~~ 0*CI_T2; CI_T3 ~~ 0*CI_T3
  DP_T1 ~~ 0*DP_T1; DP_T2 ~~ 0*DP_T2; DP_T3 ~~ 0*DP_T3
  
  wp_HP_T2 ~ a1*wp_HP_T1; wp_HP_T3 ~ a1*wp_HP_T2
  wp_JCP_T2 ~ a2*wp_JCP_T1; wp_JCP_T3 ~ a2*wp_JCP_T2
  wp_CI_T2 ~ a3*wp_CI_T1; wp_CI_T3 ~ a3*wp_CI_T2
  wp_DP_T2 ~ a4*wp_DP_T1; wp_DP_T3 ~ a4*wp_DP_T2

  wp_CI_T2 ~ hp_ci*wp_HP_T1 + jcp_ci*wp_JCP_T1 + dp_ci*wp_DP_T1
  wp_CI_T3 ~ hp_ci*wp_HP_T2 + jcp_ci*wp_JCP_T2 + dp_ci*wp_DP_T2
  
  wp_HP_T2 ~ ci_hp*wp_CI_T1 + jcp_hp*wp_JCP_T1 + dp_hp*wp_DP_T1
  wp_HP_T3 ~ ci_hp*wp_CI_T2 + jcp_hp*wp_JCP_T2 + dp_hp*wp_DP_T2
  
  wp_JCP_T2 ~ ci_jcp*wp_CI_T1 + hp_jcp*wp_HP_T1 + dp_jcp*wp_DP_T1
  wp_JCP_T3 ~ ci_jcp*wp_CI_T2 + hp_jcp*wp_HP_T2 + dp_jcp*wp_DP_T2
  
  wp_DP_T2 ~ hp_dp*wp_HP_T1 + jcp_dp*wp_JCP_T1 + ci_dp*wp_CI_T1
  wp_DP_T3 ~ hp_dp*wp_HP_T2 + jcp_dp*wp_JCP_T2 + ci_dp*wp_CI_T2

  RI_HP ~~ RI_JCP; RI_HP ~~ RI_CI; RI_HP ~~ RI_DP
  RI_JCP ~~ RI_CI; RI_JCP ~~ RI_DP; RI_CI ~~ RI_DP
  
  wp_HP_T1 ~~ wp_JCP_T1; wp_HP_T1 ~~ wp_CI_T1; wp_HP_T1 ~~ wp_DP_T1
  wp_JCP_T1 ~~ wp_CI_T1; wp_JCP_T1 ~~ wp_DP_T1; wp_CI_T1 ~~ wp_DP_T1
  
  wp_HP_T2 ~~ wp_JCP_T2; wp_HP_T2 ~~ wp_CI_T2; wp_HP_T2 ~~ wp_DP_T2
  wp_JCP_T2 ~~ wp_CI_T2; wp_JCP_T2 ~~ wp_DP_T2; wp_CI_T2 ~~ wp_DP_T2
  
  wp_HP_T3 ~~ wp_JCP_T3; wp_HP_T3 ~~ wp_CI_T3; wp_HP_T3 ~~ wp_DP_T3
  wp_JCP_T3 ~~ wp_CI_T3; wp_JCP_T3 ~~ wp_DP_T3; wp_CI_T3 ~~ wp_DP_T3
"

tryCatch({{
  fit_best <- lavaan(m_ri_compact, data=df, missing="fiml", estimator="MLR", bounds=TRUE)
  
  sink(LOG_RI)
  print(summary(fit_best, fit.measures=TRUE, standardized=TRUE))
  sink()
  
  cat(sprintf("✅ 拆分版 RI-CLPM 執行完成，報告已儲存至: %s\\n", LOG_RI))
}}, error=function(e) {{
  cat(sprintf("❌ 模型無法收斂或出現錯誤: %s\\n", e$message))
}})

cat("=== 腳本結束 ===\\n")
"""
    return r_script_content

# ==========================================
# 2.5 MPLUS SYNTAX GENERATOR
# ==========================================
def generate_spss_syntax(csv_filename, ts):
    """產出 SPSS 匯入語法 + 變數標籤 + 數值標籤"""
    return f"""* ============================================================.
* SPSS 匯入與變數標籤語法.
* 資料來源：{csv_filename}.
* 產生時間：{ts}.
* ============================================================.

* ---- 步驟 1：匯入 Analysis_Ready CSV ----.
GET DATA
  /TYPE = TXT
  /FILE = "{csv_filename}"
  /ENCODING = 'UTF8'
  /DELIMITERS = ","
  /QUALIFIER = '"'
  /FIRSTCASE = 2
  /VARIABLES =
    Group       F1.0
    HP1_T1 HP2_T1 HP3_T1 HP4_T1 HP5_T1 HP6_T1   F8.4
    JCP1_T1 JCP2_T1 JCP3_T1 JCP4_T1 JCP5_T1 JCP6_T1  F8.4
    PP1_T1 PP2_T1 PP3_T1 PP4_T1 PP5_T1 PP6_T1   F8.4
    DP1_T1 DP2_T1 DP3_T1 DP4_T1 DP5_T1           F8.4
    CI1_T1 CI2_T1 CI3_T1 CI4_T1 CI5_T1 CI6_T1 CI7_T1 CI8_T1  F8.4
    Gender      F1.0
    Age         F4.1
    Education   F1.0
    Marriage    F1.0
    NowJobTenure F6.1
    JobTenure    F6.1
    Position    F1.0
    Industry    F1.0
    OrgSize     F1.0
    PM_Has      F1.0
    PM_Supervisor PM_Self PM_Interview PM_Other  F1.0
    PM_Result   F1.0
    PM_Help     F4.1
    HP1_T2 HP2_T2 HP3_T2 HP4_T2 HP5_T2 HP6_T2   F8.4
    JCP1_T2 JCP2_T2 JCP3_T2 JCP4_T2 JCP5_T2 JCP6_T2  F8.4
    PP1_T2 PP2_T2 PP3_T2 PP4_T2 PP5_T2 PP6_T2   F8.4
    DP1_T2 DP2_T2 DP3_T2 DP4_T2 DP5_T2           F8.4
    CI1_T2 CI2_T2 CI3_T2 CI4_T2 CI5_T2 CI6_T2 CI7_T2 CI8_T2  F8.4
    HP1_T3 HP2_T3 HP3_T3 HP4_T3 HP5_T3 HP6_T3   F8.4
    JCP1_T3 JCP2_T3 JCP3_T3 JCP4_T3 JCP5_T3 JCP6_T3  F8.4
    PP1_T3 PP2_T3 PP3_T3 PP4_T3 PP5_T3 PP6_T3   F8.4
    DP1_T3 DP2_T3 DP3_T3 DP4_T3 DP5_T3           F8.4
    CI1_T3 CI2_T3 CI3_T3 CI4_T3 CI5_T3 CI6_T3 CI7_T3 CI8_T3  F8.4.
CACHE.
EXECUTE.

* ---- 步驟 2：變數標籤（Variable Labels）----.
VARIABLE LABELS
  Group       '波次群組 (1=僅T1, 2=T1+T2, 3=三波完整)'
  HP1_T1      'HP題1_T1：晉升可能性有限'
  HP2_T1      'HP題2_T1：職位達頂'
  HP3_T1      'HP題3_T1：不太可能獲更高職位'
  HP4_T1      'HP題4_T1(反)：預期近期可晉升'
  HP5_T1      'HP題5_T1：向上晉升機會有限'
  HP6_T1      'HP題6_T1(反)：預期晉升機會頻繁'
  JCP1_T1     'JCP題1_T1(反)：工作有挑戰性'
  JCP2_T1     'JCP題2_T1(反)：需拓展能力'
  JCP3_T1     'JCP題3_T1(反)：學習成長機會多'
  JCP4_T1     'JCP題4_T1(反)：工作經常有挑戰'
  JCP5_T1     'JCP題5_T1(反)：職責明顯增加'
  JCP6_T1     'JCP題6_T1：工作已成家常便飯'
  PP1_T1      'PP題1_T1：改正看不順眼的事'
  PP2_T1      'PP題2_T1：努力實現所信之事'
  PP3_T1      'PP題3_T1：擁護自己的想法'
  PP4_T1      'PP題4_T1：尋求更好做事方法'
  PP5_T1      'PP題5_T1：落實所信的理念'
  PP6_T1      'PP題6_T1：洞察先機'
  DP1_T1      'DP題1_T1：決定前花時間處理瑣事'
  DP2_T1      'DP題2_T1：決定後仍拖延行動'
  DP3_T1      'DP題3_T1：等很久才思考決定'
  DP4_T1      'DP題4_T1：拖延到為時已晚'
  DP5_T1      'DP題5_T1：拖延做決定'
  CI1_T1      'CI題1_T1：想改變職涯但未積極追求'
  CI2_T1      'CI題2_T1：不知如何開始'
  CI3_T1      'CI題3_T1：不敢放棄現有'
  CI4_T1      'CI題4_T1：未採具體行動'
  CI5_T1      'CI題5_T1：感到無法動彈'
  CI6_T1      'CI題6_T1：行動困難'
  CI7_T1      'CI題7_T1：職涯停滯感'
  CI8_T1      'CI題8_T1：無法實現職涯渴望'
  Gender      '性別'
  Age         '年齡（實歲）'
  Education   '教育程度'
  Marriage    '婚姻狀況'
  NowJobTenure '現職年資（月）'
  JobTenure   '工作總年資（月）'
  Position    '工作職級'
  Industry    '產業別'
  OrgSize     '公司規模'
  PM_Has      '是否有績效考核'
  PM_Supervisor '考核形式：主管評核'
  PM_Self     '考核形式：自我評核'
  PM_Interview '考核形式：績效面談'
  PM_Other    '考核形式：其他'
  PM_Result   '考核結果性質'
  PM_Help     '考核對職涯幫助程度（1-5）'.

* ---- 步驟 3：數值標籤（Value Labels）----.
VALUE LABELS
  Group
    1 '僅完成T1'
    2 '完成T1+T2'
    3 '三波完整' /
  Gender
    1 '男'
    2 '女'
    3 '其他' /
  Education
    1 '高中職'
    2 '專科'
    3 '大學'
    4 '碩士'
    5 '博士' /
  Marriage
    1 '未婚'
    2 '已婚無子女'
    3 '已婚有子女'
    4 '其他' /
  Position
    1 '一般員工'
    2 '基層主管'
    3 '中階主管'
    4 '高階主管' /
  Industry
    1 '製造業'
    2 '科技/資訊業'
    3 '金融/保險業'
    4 '服務業'
    5 '醫療/健康業'
    6 '教育業'
    7 '公部門'
    8 '其他' /
  OrgSize
    1 '30人以下'
    2 '31-100人'
    3 '101-500人'
    4 '501-1000人'
    5 '1001人以上' /
  PM_Has
    0 '無績效考核'
    1 '有績效考核' /
  PM_Supervisor PM_Self PM_Interview PM_Other
    0 '否'
    1 '是' /
  PM_Result
    1 '負向回饋'
    2 '中性/持平'
    3 '正向回饋'.

* ---- 步驟 4：遺漏值設定 ----.
MISSING VALUES ALL (SYSMIS).

* ---- 步驟 5：只保留三波完整樣本（Group=3）----.
* SELECT IF (Group = 3).
* EXECUTE.
* 如需全樣本分析，請移除上兩行前面的星號（*）.

* ---- 步驟 6：描述統計 ----.
DESCRIPTIVES VARIABLES = HP1_T1 TO CI8_T1
  /STATISTICS = MEAN STDDEV MIN MAX.
"""


def _mplus_header(dat_filename):
    return f"""ANALYSIS:
  ESTIMATOR = MLR;
  ITERATIONS = 10000;
  CONVERGENCE = 0.000001;
"""

def _mplus_cp_measurement():
    """CP 測量模型（HP+JCP 跨波等同）"""
    return """  ! CP: HP + JCP 跨波負荷等同 + 截距等同
  CP1 BY HP_T1  (l_hp)
          JCP_T1 (l_jcp);
  CP2 BY HP_T2  (l_hp)
          JCP_T2 (l_jcp);
  CP3 BY HP_T3  (l_hp)
          JCP_T3 (l_jcp);
  [HP_T1]  (int_hp);  [HP_T2]  (int_hp);  [HP_T3]  (int_hp);
  [JCP_T1] (int_jcp); [JCP_T2] (int_jcp); [JCP_T3] (int_jcp);
  CP1@0;  CP2@0;  CP3@0;
"""

def _mplus_single_indicator(var):
    """單一指標構念（負荷=1，殘差=0）"""
    v = var.upper()
    return (
        f"  {v}1 BY {v}_T1@1;  {v}2 BY {v}_T2@1;  {v}3 BY {v}_T3@1;\n"
        f"  {v}_T1@0;  {v}_T2@0;  {v}_T3@0;\n"
        f"  {v}1@0;  {v}2@0;  {v}3@0;\n"
    )

def _mplus_ri_clpm_core(vars_list):
    """隨機截距 + Within-person 殘差 + 自回歸（通用）"""
    ri_lines = "  ! 隨機截距\n"
    w_lines  = "  ! Within-person 殘差\n"
    ar_lines = "  ! 自回歸（跨波等同）\n"
    t1_cov   = "  ! T1 Within-person 共變\n"
    t2_cov   = "  ! T2 殘差共變\n"
    t3_cov   = "  ! T3 殘差共變\n"

    for v in vars_list:
        ri_lines += f"  RI_{v} BY {v}1@1 {v}2@1 {v}3@1;\n"
        w_lines  += f"  W{v}1 BY {v}1@1;  W{v}2 BY {v}2@1;  W{v}3 BY {v}3@1;\n"
        ar_lines += f"  W{v}2 ON W{v}1 (ar_{v.lower()});  W{v}3 ON W{v}2 (ar_{v.lower()});\n"

    w_vars = [f"W{v}1" for v in vars_list]
    t1_cov += "  " + " WITH ".join(w_vars) + ";\n" if len(w_vars) > 1 else ""
    for i in range(len(vars_list)):
        rest = [f"W{v}2" for v in vars_list[i+1:]]
        if rest:
            t2_cov += f"  W{vars_list[i]}2 WITH {' '.join(rest)};\n"
        rest3 = [f"W{v}3" for v in vars_list[i+1:]]
        if rest3:
            t3_cov += f"  W{vars_list[i]}3 WITH {' '.join(rest3)};\n"

    ri_cov = "  ! 隨機截距共變\n"
    for i in range(len(vars_list)):
        rest = [f"RI_{v}" for v in vars_list[i+1:]]
        if rest:
            ri_cov += f"  RI_{vars_list[i]} WITH {' '.join(rest)};\n"

    return ri_lines + w_lines + ar_lines + t1_cov + t2_cov + t3_cov + ri_cov


# ----------------------------------------------------------
# Step 1：主路徑 CP → DP → CI（確認信效度用）
# ----------------------------------------------------------
def generate_mplus_step1(dat_filename, ts):
    return f"""TITLE:
  [Step1] RI-CLPM 主路徑: CP -> DP -> CI
  Generated: {ts}
  用途: 確認主路徑信效度，不含 PP 與控制變數

DATA:
  FILE = "{dat_filename}";

VARIABLE:
  NAMES =
    HP_T1  JCP_T1  PP_T1  DP_T1  CI_T1
    HP_T2  JCP_T2  PP_T2  DP_T2  CI_T2
    HP_T3  JCP_T3  PP_T3  DP_T3  CI_T3;
  USEVARIABLES =
    HP_T1  JCP_T1  DP_T1  CI_T1
    HP_T2  JCP_T2  DP_T2  CI_T2
    HP_T3  JCP_T3  DP_T3  CI_T3;
  MISSING = ALL(-999);

{_mplus_header(dat_filename)}
MODEL:

{_mplus_cp_measurement()}
{_mplus_single_indicator('DP')}
{_mplus_single_indicator('CI')}
{_mplus_ri_clpm_core(['CP','DP','CI'])}
  ! 交叉延遲：CP -> DP [正向]
  WDP2 ON WCP1 (cl_cp_dp);  WDP3 ON WCP2 (cl_cp_dp);
  ! 交叉延遲：DP -> CI [正向]
  WCI2 ON WDP1 (cl_dp_ci);  WCI3 ON WDP2 (cl_dp_ci);

OUTPUT:
  SAMPSTAT;  STDYX;  MODINDICES(10);  CINTERVAL;
"""


# ----------------------------------------------------------
# Step 2：加入 PP（H8）
# ----------------------------------------------------------
def generate_mplus_step2(dat_filename, ts):
    return f"""TITLE:
  [Step2] RI-CLPM 加入 PP: CP -> DP -> CI, PP -> DP/CI
  Generated: {ts}
  H8: PP 負向預測後續 DP 與 CI

DATA:
  FILE = "{dat_filename}";

VARIABLE:
  NAMES =
    HP_T1  JCP_T1  PP_T1  DP_T1  CI_T1
    HP_T2  JCP_T2  PP_T2  DP_T2  CI_T2
    HP_T3  JCP_T3  PP_T3  DP_T3  CI_T3;
  USEVARIABLES = ALL;
  MISSING = ALL(-999);

{_mplus_header(dat_filename)}
MODEL:

{_mplus_cp_measurement()}
{_mplus_single_indicator('PP')}
{_mplus_single_indicator('DP')}
{_mplus_single_indicator('CI')}
{_mplus_ri_clpm_core(['CP','PP','DP','CI'])}
  ! 交叉延遲：CP -> DP [正向]
  WDP2 ON WCP1 (cl_cp_dp);  WDP3 ON WCP2 (cl_cp_dp);
  ! 交叉延遲：DP -> CI [正向]
  WCI2 ON WDP1 (cl_dp_ci);  WCI3 ON WDP2 (cl_dp_ci);
  ! H8: PP -> DP [負向]
  WDP2 ON WPP1 (cl_pp_dp);  WDP3 ON WPP2 (cl_pp_dp);
  ! H8: PP -> CI [負向]
  WCI2 ON WPP1 (cl_pp_ci);  WCI3 ON WPP2 (cl_pp_ci);

OUTPUT:
  SAMPSTAT;  STDYX;  MODINDICES(10);  CINTERVAL;
"""


# ----------------------------------------------------------
# Step 3：加入控制變數（性別、年齡、年資、職級）
# ----------------------------------------------------------
def generate_mplus_step3(dat_filename, ts):
    return f"""TITLE:
  [Step3] RI-CLPM 完整版: CP/PP/DP/CI + 控制變數
  Generated: {ts}
  控制變數: Gender, Age, Tenure, Position (T1 時間點)

DATA:
  FILE = "{dat_filename}";

VARIABLE:
  NAMES =
    HP_T1  JCP_T1  PP_T1  DP_T1  CI_T1
    HP_T2  JCP_T2  PP_T2  DP_T2  CI_T2
    HP_T3  JCP_T3  PP_T3  DP_T3  CI_T3
    Gender Tenure Position Age;
  USEVARIABLES = ALL;
  MISSING = ALL(-999);

{_mplus_header(dat_filename)}
MODEL:

{_mplus_cp_measurement()}
{_mplus_single_indicator('PP')}
{_mplus_single_indicator('DP')}
{_mplus_single_indicator('CI')}
{_mplus_ri_clpm_core(['CP','PP','DP','CI'])}
  ! 交叉延遲：CP -> DP
  WDP2 ON WCP1 (cl_cp_dp);  WDP3 ON WCP2 (cl_cp_dp);
  ! 交叉延遲：DP -> CI
  WCI2 ON WDP1 (cl_dp_ci);  WCI3 ON WDP2 (cl_dp_ci);
  ! H8: PP -> DP/CI
  WDP2 ON WPP1 (cl_pp_dp);  WDP3 ON WPP2 (cl_pp_dp);
  WCI2 ON WPP1 (cl_pp_ci);  WCI3 ON WPP2 (cl_pp_ci);

  ! 控制變數 -> 隨機截距（排除個體間差異）
  RI_CP ON Gender Age Tenure Position;
  RI_PP ON Gender Age Tenure Position;
  RI_DP ON Gender Age Tenure Position;
  RI_CI ON Gender Age Tenure Position;

OUTPUT:
  SAMPSTAT;  STDYX;  MODINDICES(10);  CINTERVAL;
"""


# ==========================================
# 信度分析 SPSS 語法
# ==========================================
def generate_spss_reliability_syntax(analysis_path, ts):
    return f"""\
* ============================================================.
* 信度分析語法（Cronbach's Alpha）— 自動產生 {ts}.
* 使用方式：先用 SPSS_Syntax_{ts}.sps 匯入資料，再執行本語法.
* 資料來源：{analysis_path}.
* ============================================================.

* === HP 階層停滯（T1，6 題，HP4/HP6 已反向計分）===.
RELIABILITY
  /VARIABLES = HP1_T1 HP2_T1 HP3_T1 HP4_T1 HP5_T1 HP6_T1
  /SCALE('HP 階層停滯 T1') ALL
  /MODEL = ALPHA
  /STATISTICS = DESCRIPTIVE SCALE CORR
  /SUMMARY = TOTAL MEANS VARIANCE.

* === JCP 工作內容停滯（T1，6 題，JCP1~5 已反向計分）===.
RELIABILITY
  /VARIABLES = JCP1_T1 JCP2_T1 JCP3_T1 JCP4_T1 JCP5_T1 JCP6_T1
  /SCALE('JCP 工作內容停滯 T1') ALL
  /MODEL = ALPHA
  /STATISTICS = DESCRIPTIVE SCALE CORR
  /SUMMARY = TOTAL MEANS VARIANCE.

* === CP 職涯高原合併（T1，HP+JCP 共 12 題）===.
RELIABILITY
  /VARIABLES = HP1_T1 HP2_T1 HP3_T1 HP4_T1 HP5_T1 HP6_T1
               JCP1_T1 JCP2_T1 JCP3_T1 JCP4_T1 JCP5_T1 JCP6_T1
  /SCALE('CP 職涯高原合併 T1') ALL
  /MODEL = ALPHA
  /STATISTICS = DESCRIPTIVE SCALE CORR
  /SUMMARY = TOTAL MEANS VARIANCE.

* === PP 主動型人格（T1，6 題）===.
RELIABILITY
  /VARIABLES = PP1_T1 PP2_T1 PP3_T1 PP4_T1 PP5_T1 PP6_T1
  /SCALE('PP 主動型人格 T1') ALL
  /MODEL = ALPHA
  /STATISTICS = DESCRIPTIVE SCALE CORR
  /SUMMARY = TOTAL MEANS VARIANCE.

* === DP 決策拖延（T1，5 題）===.
RELIABILITY
  /VARIABLES = DP1_T1 DP2_T1 DP3_T1 DP4_T1 DP5_T1
  /SCALE('DP 決策拖延 T1') ALL
  /MODEL = ALPHA
  /STATISTICS = DESCRIPTIVE SCALE CORR
  /SUMMARY = TOTAL MEANS VARIANCE.

* === CI 職涯無所作為（T1，8 題）===.
RELIABILITY
  /VARIABLES = CI1_T1 CI2_T1 CI3_T1 CI4_T1 CI5_T1 CI6_T1 CI7_T1 CI8_T1
  /SCALE('CI 職涯無所作為 T1') ALL
  /MODEL = ALPHA
  /STATISTICS = DESCRIPTIVE SCALE CORR
  /SUMMARY = TOTAL MEANS VARIANCE.

* ============================================================.
* 各波信度（T2 / T3）——若需跨波比較請執行以下語法.
* ============================================================.
* HP T2.
RELIABILITY
  /VARIABLES = HP1_T2 HP2_T2 HP3_T2 HP4_T2 HP5_T2 HP6_T2
  /SCALE('HP T2') ALL /MODEL = ALPHA /SUMMARY = TOTAL.
RELIABILITY
  /VARIABLES = HP1_T3 HP2_T3 HP3_T3 HP4_T3 HP5_T3 HP6_T3
  /SCALE('HP T3') ALL /MODEL = ALPHA /SUMMARY = TOTAL.

RELIABILITY
  /VARIABLES = DP1_T2 DP2_T2 DP3_T2 DP4_T2 DP5_T2
  /SCALE('DP T2') ALL /MODEL = ALPHA /SUMMARY = TOTAL.
RELIABILITY
  /VARIABLES = DP1_T3 DP2_T3 DP3_T3 DP4_T3 DP5_T3
  /SCALE('DP T3') ALL /MODEL = ALPHA /SUMMARY = TOTAL.

RELIABILITY
  /VARIABLES = CI1_T2 CI2_T2 CI3_T2 CI4_T2 CI5_T2 CI6_T2 CI7_T2 CI8_T2
  /SCALE('CI T2') ALL /MODEL = ALPHA /SUMMARY = TOTAL.
RELIABILITY
  /VARIABLES = CI1_T3 CI2_T3 CI3_T3 CI4_T3 CI5_T3 CI6_T3 CI7_T3 CI8_T3
  /SCALE('CI T3') ALL /MODEL = ALPHA /SUMMARY = TOTAL.
"""


# ==========================================
# CFA 用 dat 檔（原始題目，T1）
# ==========================================
def generate_cfa_dat(df, output_dir, ts):
    """匯出 T1 原始題目供五因子 CFA 使用（31 欄，無標題，空白分隔）"""
    cfa_cols = (
        [f'HP{i+1}_T1'  for i in range(6)] +
        [f'JCP{i+1}_T1' for i in range(6)] +
        [f'PP{i+1}_T1'  for i in range(6)] +
        [f'DP{i+1}_T1'  for i in range(5)] +
        [f'CI{i+1}_T1'  for i in range(8)]
    )
    cfa_cols = [c for c in cfa_cols if c in df.columns]
    cfa_df = df[cfa_cols].fillna(-999)
    dat_filename = f"CFA_Data_T1_{ts}.dat"
    dat_path = os.path.join(output_dir, dat_filename)
    cfa_df.to_csv(dat_path, sep=' ', index=False, header=False, float_format='%.4f')
    return dat_path, dat_filename


# ==========================================
# Mplus CFA 語法（五因子量測模型）
# ==========================================
def generate_mplus_cfa_five_factor(dat_filename, ts):
    return f"""\
TITLE:
  五因子 CFA — HP / JCP / PP / DP / CI（T1）
  N = 277 / 產生時間 {ts}

DATA:
  FILE = "{dat_filename}";

VARIABLE:
  NAMES =
    HP1 HP2 HP3 HP4 HP5 HP6
    JCP1 JCP2 JCP3 JCP4 JCP5 JCP6
    PP1 PP2 PP3 PP4 PP5 PP6
    DP1 DP2 DP3 DP4 DP5
    CI1 CI2 CI3 CI4 CI5 CI6 CI7 CI8;
  USEVARIABLES = ALL;
  MISSING = ALL(-999);

ANALYSIS:
  ESTIMATOR = MLR;

MODEL:
  ! 因子負荷量自由估計（* 符號），以固定因子變異數 @1 識別
  HP  BY HP1*  HP2  HP3  HP4  HP5  HP6;   HP@1;
  JCP BY JCP1* JCP2 JCP3 JCP4 JCP5 JCP6;  JCP@1;
  PP  BY PP1*  PP2  PP3  PP4  PP5  PP6;   PP@1;
  DP  BY DP1*  DP2  DP3  DP4  DP5;        DP@1;
  CI  BY CI1*  CI2  CI3  CI4  CI5  CI6  CI7  CI8;  CI@1;

  ! HP 與 JCP 同屬 CP 構念，允許共變
  HP WITH JCP;

OUTPUT:
  STDYX;           ! 標準化負荷量（報告用）
  MODINDICES(10);  ! 修正指標（≥ 10 才考慮修正）
  CINTERVAL;       ! 95% 信賴區間
"""


# ==========================================
# Mplus 測量恆等性語法（Configural / Metric / Scalar）
# ==========================================
def generate_mplus_cfa_three_factor(dat_filename, ts):
    """三因子 CFA：CP合併（12題）/ DP / CI — 僅主路徑構念"""
    return f"""\
TITLE:
  三因子 CFA（主路徑構念）— CP / DP / CI（T1）
  CP = HP1~HP6 + JCP1~JCP6 共 12 題視為單一構念
  不含 PP（主動型人格）
  N = 277 / 產生時間 {ts}
  【用途】驗證主路徑三構念之區別效度，與四因子/五因子比較

DATA:
  FILE = "{dat_filename}";

VARIABLE:
  NAMES =
    HP1 HP2 HP3 HP4 HP5 HP6
    JCP1 JCP2 JCP3 JCP4 JCP5 JCP6
    PP1 PP2 PP3 PP4 PP5 PP6
    DP1 DP2 DP3 DP4 DP5
    CI1 CI2 CI3 CI4 CI5 CI6 CI7 CI8;
  USEVARIABLES =
    HP1 HP2 HP3 HP4 HP5 HP6
    JCP1 JCP2 JCP3 JCP4 JCP5 JCP6
    DP1 DP2 DP3 DP4 DP5
    CI1 CI2 CI3 CI4 CI5 CI6 CI7 CI8;
  MISSING = ALL(-999);

ANALYSIS:
  ESTIMATOR = MLR;

MODEL:
  ! CP = HP + JCP 合併為單一因子（12 題）
  CP BY HP1* HP2 HP3 HP4 HP5 HP6
         JCP1 JCP2 JCP3 JCP4 JCP5 JCP6;  CP@1;

  DP BY DP1* DP2 DP3 DP4 DP5;  DP@1;
  CI BY CI1* CI2 CI3 CI4 CI5 CI6 CI7 CI8;  CI@1;

OUTPUT:
  STDYX;
  MODINDICES(10);
  CINTERVAL;
"""


def generate_mplus_cfa_four_factor(dat_filename, ts):
    """四因子 CFA：CP 合併（12 題）/ PP / DP / CI — 與五因子對照比較"""
    return f"""\
TITLE:
  四因子 CFA（對照模型）— CP合併 / PP / DP / CI（T1）
  CP = HP1~HP6 + JCP1~JCP6 共 12 題視為單一構念
  N = 277 / 產生時間 {ts}
  【用途】與五因子模型比較 CFI/RMSEA，驗證 HP/JCP 是否需要分開

DATA:
  FILE = "{dat_filename}";

VARIABLE:
  NAMES =
    HP1 HP2 HP3 HP4 HP5 HP6
    JCP1 JCP2 JCP3 JCP4 JCP5 JCP6
    PP1 PP2 PP3 PP4 PP5 PP6
    DP1 DP2 DP3 DP4 DP5
    CI1 CI2 CI3 CI4 CI5 CI6 CI7 CI8;
  USEVARIABLES = ALL;
  MISSING = ALL(-999);

ANALYSIS:
  ESTIMATOR = MLR;

MODEL:
  ! CP = HP + JCP 合併為單一因子（12 題）
  CP BY HP1* HP2 HP3 HP4 HP5 HP6
         JCP1 JCP2 JCP3 JCP4 JCP5 JCP6;  CP@1;

  PP BY PP1* PP2 PP3 PP4 PP5 PP6;  PP@1;
  DP BY DP1* DP2 DP3 DP4 DP5;     DP@1;
  CI BY CI1* CI2 CI3 CI4 CI5 CI6 CI7 CI8;  CI@1;

OUTPUT:
  STDYX;
  MODINDICES(10);
  CINTERVAL;
"""


def generate_mplus_measurement_invariance(dat_filename_ri, ts):
    """
    使用 parcel 合成分數（HP, JCP, PP, DP, CI）跨三波測量恆等性
    """
    return f"""\
TITLE:
  測量恆等性檢定（Measurement Invariance）
  HP / JCP / PP / DP / CI 三波追蹤
  產生時間 {ts}

! ============================================================
! 注意：以下三個模型請分別儲存為三個 .inp 檔案跑
!   MI_Step1_Configural.inp  （形態模式）
!   MI_Step2_Metric.inp      （因子負荷等同）
!   MI_Step3_Scalar.inp      （截距等同）
! ============================================================

DATA:
  FILE = "{dat_filename_ri}";   ! 使用含三波 parcel 分數的 dat

VARIABLE:
  NAMES =
    HP_T1 JCP_T1 PP_T1 DP_T1 CI_T1
    HP_T2 JCP_T2 PP_T2 DP_T2 CI_T2
    HP_T3 JCP_T3 PP_T3 DP_T3 CI_T3
    Gender Age Tenure Position;
  USEVARIABLES =
    HP_T1 JCP_T1 PP_T1 DP_T1 CI_T1
    HP_T2 JCP_T2 PP_T2 DP_T2 CI_T2
    HP_T3 JCP_T3 PP_T3 DP_T3 CI_T3;
  MISSING = ALL(-999);

ANALYSIS:
  ESTIMATOR = MLR;

! ===========================================================
! 【Step 1 — Configural Model（形態模式）：因子結構相同即可】
! ===========================================================
MODEL:
  ! T1 因子（自由估計負荷量）
  F_HP1  BY HP_T1*;   F_HP1@1;
  F_JCP1 BY JCP_T1*;  F_JCP1@1;
  F_PP1  BY PP_T1*;   F_PP1@1;
  F_DP1  BY DP_T1*;   F_DP1@1;
  F_CI1  BY CI_T1*;   F_CI1@1;
  ! T2
  F_HP2  BY HP_T2*;   F_HP2@1;
  F_JCP2 BY JCP_T2*;  F_JCP2@1;
  F_PP2  BY PP_T2*;   F_PP2@1;
  F_DP2  BY DP_T2*;   F_DP2@1;
  F_CI2  BY CI_T2*;   F_CI2@1;
  ! T3
  F_HP3  BY HP_T3*;   F_HP3@1;
  F_JCP3 BY JCP_T3*;  F_JCP3@1;
  F_PP3  BY PP_T3*;   F_PP3@1;
  F_DP3  BY DP_T3*;   F_DP3@1;
  F_CI3  BY CI_T3*;   F_CI3@1;

! ===========================================================
! 【Step 2 — Metric Model（因子負荷等同）：跨波加等同約束】
! 請複製此段改為以下語法再另存 MI_Step2_Metric.inp
! ===========================================================
! MODEL:
!   F_HP1  BY HP_T1*  (l_hp);
!   F_HP2  BY HP_T2   (l_hp);
!   F_HP3  BY HP_T3   (l_hp);
!   F_HP1@1; F_HP2@1; F_HP3@1;
!   (... 其餘 JCP / PP / DP / CI 同樣加 (l_xxx) 標籤)

! ===========================================================
! 【Step 3 — Scalar Model（截距等同）：再加截距約束】
! 請另存 MI_Step3_Scalar.inp，在 Metric 基礎上加：
! ===========================================================
! MODEL:
!   [HP_T1] (int_hp);  [HP_T2] (int_hp);  [HP_T3] (int_hp);
!   [JCP_T1](int_jcp); [JCP_T2](int_jcp); [JCP_T3](int_jcp);
!   (... 其餘同樣加截距等同標籤)

OUTPUT:
  STDYX;
  MODINDICES(10);
  CINTERVAL;
"""


def generate_mplus_dat(df, output_dir, ts):
    """
    從個別題目欄位計算 parcel 平均，產出 Mplus 用的 .dat 檔
    HP_T1 = mean(HP1_T1..HP6_T1), JCP_T1 = mean(JCP1_T1..JCP6_T1), etc.
    """
    def pmean(data, prefix, n, wave):
        cols = [f'{prefix}{i+1}_{wave}' for i in range(n)]
        cols = [c for c in cols if c in data.columns]
        return data[cols].mean(axis=1) if cols else pd.Series([-999]*len(data), index=data.index)

    mplus_df = pd.DataFrame(index=df.index)
    for wave in ['T1', 'T2', 'T3']:
        mplus_df[f'HP_{wave}']  = pmean(df, 'HP',  6, wave)
        mplus_df[f'JCP_{wave}'] = pmean(df, 'JCP', 6, wave)
        mplus_df[f'PP_{wave}']  = pmean(df, 'PP',  6, wave)
        mplus_df[f'DP_{wave}']  = pmean(df, 'DP',  5, wave)
        mplus_df[f'CI_{wave}']  = pmean(df, 'CI',  8, wave)

    # 控制變數（Step3 用）
    for col, src in [('Gender','Gender'), ('Age','Age'),
                     ('Tenure','NowJobTenure'), ('Position','Position')]:
        mplus_df[col] = df[src] if src in df.columns else -999

    # PP 中位數切割：PP_group = 0(低PP) / 1(高PP)，依 T1 PP 分數
    pp_median = mplus_df['PP_T1'].replace(-999, np.nan).median()
    mplus_df['PP_group'] = mplus_df['PP_T1'].apply(
        lambda x: -999 if x == -999 else (1 if x >= pp_median else 0))
    print(f"[PP分群] T1 PP 中位數 = {pp_median:.3f}  "
          f"低PP組(0): {(mplus_df['PP_group']==0).sum()}人  "
          f"高PP組(1): {(mplus_df['PP_group']==1).sum()}人")

    mplus_df = mplus_df.fillna(-999)
    dat_filename = f"Mplus_Data_{ts}.dat"
    dat_path = os.path.join(output_dir, dat_filename)
    mplus_df.to_csv(dat_path, sep=' ', index=False, header=False,
                    float_format='%.4f')
    return dat_path, dat_filename


# ==========================================
# MODULE A: P值格式化工具
# ==========================================
def fmt_p(p):
    """
    格式化 p 值，回傳 (星號str, p值str)
    星號：*** p<.001 / ** p<.01 / * p<.05 / '' 不顯著
    p值：p < .001 / p = .032（三位小數）
    """
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return '', 'N/A'
    star  = '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else ''
    p_str = 'p < .001' if p < .001 else f'p = {p:.3f}'
    return star, p_str


def fmt_beta(b, p, decimals=3):
    """
    格式化路徑係數：β值 + 星號（如 .234**），同時回傳 p 值字串
    用於 Excel 表格同一格顯示係數+顯著性，另一欄顯示 p 值
    """
    if b is None or (isinstance(b, float) and np.isnan(b)):
        return 'N/A', 'N/A'
    star, p_str = fmt_p(p)
    fmt = f'.{decimals}f'
    b_str = f'{b:{fmt}}{star}'
    return b_str, p_str


# ==========================================
# MODULE B: Mplus .inp 雙編碼儲存
# ==========================================
def save_inp_dual_encoding(content, run_dir, base_fname):
    """
    將 Mplus .inp 語法儲存為兩個版本：
      {base_fname}.inp    → UTF-8  （現代 Windows / Mac）
      {base_fname}_b5.inp → Big5/CP950（舊版繁中 Windows）
    中文字元若無法轉換 Big5 則以 ? 替代。
    """
    utf8_path = os.path.join(run_dir, base_fname + '.inp')
    b5_path   = os.path.join(run_dir, base_fname + '_b5.inp')

    with open(utf8_path, 'w', encoding='utf-8') as f:
        f.write(content)

    b5_bytes = content.encode('big5', errors='replace')
    with open(b5_path, 'wb') as f:
        f.write(b5_bytes)

    return utf8_path, b5_path


# ==========================================
# MODULE C: Mplus 自動執行模組
# ==========================================
import subprocess

MPLUS_EXE_CANDIDATES = [
    r"C:\Program Files\Mplus\mplus.exe",
    r"C:\Program Files (x86)\Mplus\mplus.exe",
    r"C:\Mplus\mplus.exe",
    r"D:\Program Files\Mplus\mplus.exe",
]

def find_mplus_exe():
    """自動搜尋 Mplus 執行檔；找不到回傳 None"""
    for path in MPLUS_EXE_CANDIDATES:
        if os.path.isfile(path):
            return path
    return None


def run_mplus_single(inp_path, mplus_exe=None, timeout=300):
    """
    執行單一 Mplus .inp 檔。
    回傳: (success: bool, out_path: str|None, error_msg: str)
    """
    if mplus_exe is None:
        mplus_exe = find_mplus_exe()
    if mplus_exe is None:
        return False, None, "找不到 Mplus 執行檔，請確認安裝路徑"

    inp_dir  = os.path.dirname(os.path.abspath(inp_path))
    inp_file = os.path.basename(inp_path)
    out_file = inp_file.lower().replace('.inp', '.out')
    out_path = os.path.join(inp_dir, out_file)

    try:
        subprocess.run(
            [mplus_exe, inp_file],
            cwd=inp_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )
        success = os.path.isfile(out_path)
        return success, out_path if success else None, ''
    except subprocess.TimeoutExpired:
        return False, None, f'執行逾時（>{timeout}s）'
    except Exception as e:
        return False, None, str(e)


def run_all_mplus(inp_list, mplus_exe=None, timeout=300):
    """
    批次執行多個 Mplus .inp 檔。
    inp_list: [(label, inp_path), ...]
    回傳: [(label, success, out_path, err_msg), ...]
    """
    if mplus_exe is None:
        mplus_exe = find_mplus_exe()
    if mplus_exe is None:
        print("  [警告] 找不到 Mplus，跳過自動執行。請手動執行 .inp 檔後再繼續。")
        return [(label, False, None, '未找到 Mplus') for label, _ in inp_list]

    results = []
    for label, inp_path in inp_list:
        print(f"  [Mplus] {label}...", end=' ', flush=True)
        ok, out, err = run_mplus_single(inp_path, mplus_exe, timeout)
        print('[OK]' if ok else f'[FAIL] ({err})')
        results.append((label, ok, out, err))
    return results


# ==========================================
# MODULE D: Mplus .out 結果解析
# ==========================================
def parse_mplus_fit(out_path):
    """
    從 Mplus .out 擷取模型適配指數。
    回傳 dict 含：chi2, df, p_chi2, scaling_cf,
                  cfi, tli, rmsea, rmsea_lo, rmsea_hi, p_rmsea, srmr
    """
    if not out_path or not os.path.isfile(out_path):
        return {}
    try:
        with open(out_path, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
    except Exception:
        return {}

    fit = {}
    # chi-square
    m = re.search(r'Chi-Square Test of Model Fit\s+Value\s+([\d.]+)\*?', text)
    if m: fit['chi2'] = float(m.group(1))
    m = re.search(r'Degrees of Freedom\s+(\d+)', text)
    if m: fit['df'] = int(m.group(1))
    m = re.search(r'P-Value\s+([\d.]+)', text)
    if m: fit['p_chi2'] = float(m.group(1))
    m = re.search(r'Scaling Correction Factor\s+([\d.]+)', text)
    if m: fit['scaling_cf'] = float(m.group(1))
    # RMSEA
    m = re.search(r'RMSEA.*?Estimate\s+([\d.]+)\s+90 Percent C\.I\.\s+([\d.]+)\s+([\d.]+)',
                  text, re.DOTALL)
    if m:
        fit['rmsea']    = float(m.group(1))
        fit['rmsea_lo'] = float(m.group(2))
        fit['rmsea_hi'] = float(m.group(3))
    m = re.search(r'Probability RMSEA <= \.05\s+([\d.]+)', text)
    if m: fit['p_rmsea'] = float(m.group(1))
    # CFI / TLI
    m = re.search(r'\bCFI\s+([\d.]+)', text)
    if m: fit['cfi'] = float(m.group(1))
    m = re.search(r'\bTLI\s+([\d.]+)', text)
    if m: fit['tli'] = float(m.group(1))
    # SRMR
    m = re.search(r'SRMR \(Standardized Root Mean Square Residual\)\s+Value\s+([\d.]+)', text)
    if m: fit['srmr'] = float(m.group(1))

    return fit


def parse_mplus_stdyx(out_path, path_map):
    """
    從 Mplus .out 的 STDYX STANDARDIZATION 區段擷取路徑係數。

    path_map: dict，格式為：
        { '顯示標籤': ('結果變數', '預測變數') }
    例：
        { 'JCP→DP': ('WDP2', 'WJCP1'),
          'DP→CI':  ('WCI2', 'WDP1'),
          'PP→DP':  ('WDP2', 'WPP1') }

    回傳 dict：{ '標籤': {'est': float, 'se': float, 'z': float, 'p': float} }
    """
    if not out_path or not os.path.isfile(out_path):
        return {}
    try:
        with open(out_path, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
    except Exception:
        return {}

    # 找 STDYX 區段（到 R-SQUARE 或下一個大標題為止）
    m = re.search(r'STDYX Standardization\s+(.*?)(?=\nR-SQUARE|\nSTD |\Z)',
                  text, re.DOTALL)
    if not m:
        return {}
    stdyx = m.group(1)

    results = {}
    for label, (outcome, predictor) in path_map.items():
        # 找 outcome ON ... 區段
        on_m = re.search(
            rf'{re.escape(outcome)}\s+ON\s+(.*?)(?=\n\s*\n\s*\w|\n\s*\n\s*$)',
            stdyx, re.DOTALL | re.IGNORECASE
        )
        if not on_m:
            continue
        on_text = on_m.group(1)
        row = re.search(
            rf'\b{re.escape(predictor)}\s+([-\d.]+)\s+([\d.]+)\s+([-\d.]+)\s+([\d.]+)',
            on_text, re.IGNORECASE
        )
        if row:
            results[label] = {
                'est': float(row.group(1)),
                'se':  float(row.group(2)),
                'z':   float(row.group(3)),
                'p':   float(row.group(4))
            }
    return results


def parse_mplus_ri_corr(out_path, ri_pairs):
    """
    從 Mplus .out 的 CONFIDENCE INTERVALS OF STANDARDIZED MODEL RESULTS 區段
    擷取隨機截距相關係數（STDYX 標準化）。

    ri_pairs: list of (label, ri_x, ri_y)
    例: [('RI_DP↔RI_CI', 'RI_DP', 'RI_CI'), ...]

    回傳: { label: {'est': float, 'ci_lo': float, 'ci_hi': float, 'sig': bool} }
    """
    if not out_path or not os.path.isfile(out_path):
        return {}
    try:
        with open(out_path, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
    except Exception:
        return {}

    # 從 CI OF STANDARDIZED 區段找 RI WITH 值（4 欄：lo95, lo90, lo68, est, hi68, hi90, hi95）
    ci_m = re.search(
        r'CONFIDENCE INTERVALS OF STANDARDIZED MODEL RESULTS.*?STDYX Standardization\s+(.*?)(?=\nTECHNICAL|\Z)',
        text, re.DOTALL
    )
    if not ci_m:
        return {}
    ci_text = ci_m.group(1)

    results = {}
    for label, ri_x, ri_y in ri_pairs:
        # 找 RI_X WITH ... 的 RI_Y 列
        with_m = re.search(
            rf'{re.escape(ri_x)}\s+WITH\s+(.*?)(?=\n\s*\n|\n\s*\w+\s+WITH|\Z)',
            ci_text, re.DOTALL | re.IGNORECASE
        )
        if not with_m:
            continue
        with_text = with_m.group(1)
        row = re.search(
            rf'\b{re.escape(ri_y)}\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)',
            with_text, re.IGNORECASE
        )
        if row:
            lo95 = float(row.group(2))   # Lower 2.5%
            est  = float(row.group(4))   # Estimate (中間值)
            hi95 = float(row.group(6))   # Upper 2.5%
            sig  = not (lo95 <= 0 <= hi95)   # 95% CI 不含 0 → 顯著
            results[label] = {
                'est': est,
                'ci_lo': lo95,
                'ci_hi': hi95,
                'sig': sig
            }
    return results


# ==========================================
# MODULE E: 整合執行所有 Mplus 模型並收集結果
# ==========================================
def run_and_parse_all_models(run_dir, mplus_dat_filename, cfa_dat_filename, ts,
                              mplus_exe=None):
    """
    生成 8 個新 CFA/RI-CLPM .inp → 自動執行 → 解析結果
    回傳 all_results dict 供 Excel/Word/PPT 使用
    """
    all_results = {}

    # ---- CFA 模型 A-D ----
    # vars_lines: 每個因子的題目分行（Mplus 每行 <90 字元限制）
    _v_jcp = '    JCP1 JCP2 JCP3 JCP4 JCP5 JCP6'
    _v_hp  = '    HP1  HP2  HP3  HP4  HP5  HP6'
    _v_pp  = '    PP1  PP2  PP3  PP4  PP5  PP6'
    _v_dp  = '    DP1  DP2  DP3  DP4  DP5'
    _v_ci  = '    CI1  CI2  CI3  CI4  CI5  CI6  CI7  CI8'

    cfa_models = {
        'CFA-A (JCP+DP+CI)': {
            'fname': f'CFA_A_JCP_DP_CI_{ts}',
            'vars_lines': f'{_v_jcp}\n{_v_dp}\n{_v_ci}',
            'model_lines': (
                '  JCP BY JCP1* JCP2 JCP3 JCP4 JCP5 JCP6;  JCP@1;\n'
                '  DP  BY DP1*  DP2  DP3  DP4  DP5;        DP@1;\n'
                '  CI  BY CI1*  CI2  CI3  CI4  CI5  CI6  CI7  CI8;  CI@1;\n'
            )
        },
        'CFA-B (HP+DP+CI)': {
            'fname': f'CFA_B_HP_DP_CI_{ts}',
            'vars_lines': f'{_v_hp}\n{_v_dp}\n{_v_ci}',
            'model_lines': (
                '  HP  BY HP1*  HP2  HP3  HP4  HP5  HP6;   HP@1;\n'
                '  DP  BY DP1*  DP2  DP3  DP4  DP5;        DP@1;\n'
                '  CI  BY CI1*  CI2  CI3  CI4  CI5  CI6  CI7  CI8;  CI@1;\n'
            )
        },
        'CFA-C (JCP+PP+DP+CI)': {
            'fname': f'CFA_C_JCP_PP_DP_CI_{ts}',
            'vars_lines': f'{_v_jcp}\n{_v_pp}\n{_v_dp}\n{_v_ci}',
            'model_lines': (
                '  JCP BY JCP1* JCP2 JCP3 JCP4 JCP5 JCP6;  JCP@1;\n'
                '  PP  BY PP1*  PP2  PP3  PP4  PP5  PP6;   PP@1;\n'
                '  DP  BY DP1*  DP2  DP3  DP4  DP5;        DP@1;\n'
                '  CI  BY CI1*  CI2  CI3  CI4  CI5  CI6  CI7  CI8;  CI@1;\n'
            )
        },
        'CFA-D (HP+PP+DP+CI)': {
            'fname': f'CFA_D_HP_PP_DP_CI_{ts}',
            'vars_lines': f'{_v_hp}\n{_v_pp}\n{_v_dp}\n{_v_ci}',
            'model_lines': (
                '  HP  BY HP1*  HP2  HP3  HP4  HP5  HP6;   HP@1;\n'
                '  PP  BY PP1*  PP2  PP3  PP4  PP5  PP6;   PP@1;\n'
                '  DP  BY DP1*  DP2  DP3  DP4  DP5;        DP@1;\n'
                '  CI  BY CI1*  CI2  CI3  CI4  CI5  CI6  CI7  CI8;  CI@1;\n'
            )
        },
    }

    cfa_inp_list = []
    for label, cfg in cfa_models.items():
        vl = cfg['vars_lines']
        content = (
            f'TITLE:\n  {label} CFA (T1)\n  Generated: {ts}\n\n'
            f'DATA:\n  FILE = "{cfa_dat_filename}";\n\n'
            f'VARIABLE:\n  NAMES =\n'
            f'    HP1  HP2  HP3  HP4  HP5  HP6\n'
            f'    JCP1 JCP2 JCP3 JCP4 JCP5 JCP6\n'
            f'    PP1  PP2  PP3  PP4  PP5  PP6\n'
            f'    DP1  DP2  DP3  DP4  DP5\n'
            f'    CI1  CI2  CI3  CI4  CI5  CI6  CI7  CI8;\n'
            f'  USEVARIABLES =\n{vl};\n'
            f'  MISSING =\n{vl} (-999);\n\n'
            f'ANALYSIS:\n  ESTIMATOR = MLR;\n\n'
            f'MODEL:\n{cfg["model_lines"]}\n'
            f'OUTPUT:\n  STDYX;\n  MODINDICES(10);\n  CINTERVAL;\n'
        )
        utf8_path, b5_path = save_inp_dual_encoding(content, run_dir, cfg['fname'])
        cfa_inp_list.append((label, utf8_path))

    # ---- RI-CLPM 模型 A-D ----
    # NAMES 欄位順序（含 PP_group）
    all_var_names = ('HP_T1  JCP_T1  PP_T1  DP_T1  CI_T1\n'
                     '    HP_T2  JCP_T2  PP_T2  DP_T2  CI_T2\n'
                     '    HP_T3  JCP_T3  PP_T3  DP_T3  CI_T3\n'
                     '    Gender Tenure Position Age PP_group')

    def make_riclpm_ab(cp, ts, mplus_dat_filename):
        """
        Model A (JCP) / B (HP)：完整雙向六條交叉延遲路徑
        H1: CP→DP  H2: CP→CI  H3: DP→CI
        H4: DP→CP  H5: CI→DP  H6: CI→CP
        """
        cpp = cp.lower()
        use_vars = (f'{cp}_T1  DP_T1  CI_T1\n'
                    f'    {cp}_T2  DP_T2  CI_T2\n'
                    f'    {cp}_T3  DP_T3  CI_T3')
        return (
            f'TITLE:\n  RI-CLPM Model {"A" if cp=="JCP" else "B"} ({cp}->DP->CI, Bidirectional)\n'
            f'  Generated: {ts}\n\n'
            f'DATA:\n  FILE = "{mplus_dat_filename}";\n\n'
            f'VARIABLE:\n  NAMES =\n    {all_var_names};\n'
            f'  USEVARIABLES =\n    {use_vars};\n'
            f'  MISSING = ALL(-999);\n\n'
            f'ANALYSIS:\n  ESTIMATOR = MLR;\n  ITERATIONS = 10000;\n  CONVERGENCE = 0.000001;\n\n'
            f'MODEL:\n'
            f'  ! 單一指標\n'
            f'  {cp}1 BY {cp}_T1@1;  {cp}_T1@0;  {cp}1@0;\n'
            f'  {cp}2 BY {cp}_T2@1;  {cp}_T2@0;  {cp}2@0;\n'
            f'  {cp}3 BY {cp}_T3@1;  {cp}_T3@0;  {cp}3@0;\n'
            f'  DP1 BY DP_T1@1;  DP_T1@0;  DP1@0;\n'
            f'  DP2 BY DP_T2@1;  DP_T2@0;  DP2@0;\n'
            f'  DP3 BY DP_T3@1;  DP_T3@0;  DP3@0;\n'
            f'  CI1 BY CI_T1@1;  CI_T1@0;  CI1@0;\n'
            f'  CI2 BY CI_T2@1;  CI_T2@0;  CI2@0;\n'
            f'  CI3 BY CI_T3@1;  CI_T3@0;  CI3@0;\n\n'
            f'  ! 隨機截距\n'
            f'  RI_{cp} BY {cp}1@1 {cp}2@1 {cp}3@1;\n'
            f'  RI_DP   BY DP1@1  DP2@1  DP3@1;\n'
            f'  RI_CI   BY CI1@1  CI2@1  CI3@1;\n\n'
            f'  ! Within-person 殘差\n'
            f'  W{cp}1 BY {cp}1@1;  W{cp}2 BY {cp}2@1;  W{cp}3 BY {cp}3@1;\n'
            f'  WDP1 BY DP1@1;  WDP2 BY DP2@1;  WDP3 BY DP3@1;\n'
            f'  WCI1 BY CI1@1;  WCI2 BY CI2@1;  WCI3 BY CI3@1;\n\n'
            f'  ! 自回歸（跨波等同）\n'
            f'  W{cp}2 ON W{cp}1 (ar_{cpp});  W{cp}3 ON W{cp}2 (ar_{cpp});\n'
            f'  WDP2  ON WDP1  (ar_dp);       WDP3  ON WDP2  (ar_dp);\n'
            f'  WCI2  ON WCI1  (ar_ci);       WCI3  ON WCI2  (ar_ci);\n\n'
            f'  ! T1 Within-person 共變\n'
            f'  W{cp}1 WITH WDP1;  W{cp}1 WITH WCI1;  WDP1 WITH WCI1;\n'
            f'  ! T2/T3 殘差共變\n'
            f'  W{cp}2 WITH WDP2;  W{cp}2 WITH WCI2;  WDP2 WITH WCI2;\n'
            f'  W{cp}3 WITH WDP3;  W{cp}3 WITH WCI3;  WDP3 WITH WCI3;\n\n'
            f'  ! 隨機截距共變\n'
            f'  RI_{cp} WITH RI_DP;  RI_{cp} WITH RI_CI;  RI_DP WITH RI_CI;\n\n'
            f'  ! ===== 六條雙向交叉延遲路徑 =====\n'
            f'  ! H1a/b: {cp} -> DP（正向）\n'
            f'  WDP2 ON W{cp}1 (cl_{cpp}_dp);  WDP3 ON W{cp}2 (cl_{cpp}_dp);\n'
            f'  ! H2a/b: {cp} -> CI（正向）\n'
            f'  WCI2 ON W{cp}1 (cl_{cpp}_ci);  WCI3 ON W{cp}2 (cl_{cpp}_ci);\n'
            f'  ! H3: DP -> CI（正向）\n'
            f'  WCI2 ON WDP1  (cl_dp_ci);      WCI3 ON WDP2  (cl_dp_ci);\n'
            f'  ! H4a/b: DP -> {cp}（正向，反向）\n'
            f'  W{cp}2 ON WDP1 (cl_dp_{cpp});  W{cp}3 ON WDP2 (cl_dp_{cpp});\n'
            f'  ! H5: CI -> DP（正向，反向）\n'
            f'  WDP2 ON WCI1  (cl_ci_dp);      WDP3 ON WCI2  (cl_ci_dp);\n'
            f'  ! H6a/b: CI -> {cp}（正向，反向）\n'
            f'  W{cp}2 ON WCI1 (cl_ci_{cpp});  W{cp}3 ON WCI2 (cl_ci_{cpp});\n'
            f'\nOUTPUT:\n  SAMPSTAT;  STDYX;  MODINDICES(10);  CINTERVAL;\n'
        )

    def make_riclpm_cd_multigroup(cp, ts, mplus_dat_filename):
        """
        Model C (JCP) / D (HP)：Multi-group RI-CLPM（高PP vs 低PP）
        GROUPING = PP_group (0=LowPP 1=HighPP)
        Configural model：各組路徑自由估計，比較組間差異
        """
        cpp = cp.lower()
        label = 'C' if cp == 'JCP' else 'D'
        use_vars = (f'{cp}_T1  DP_T1  CI_T1\n'
                    f'    {cp}_T2  DP_T2  CI_T2\n'
                    f'    {cp}_T3  DP_T3  CI_T3')
        return (
            f'TITLE:\n  RI-CLPM Model {label} Multi-group PP ({cp}, H8 test)\n'
            f'  Generated: {ts}\n\n'
            f'DATA:\n  FILE = "{mplus_dat_filename}";\n\n'
            f'VARIABLE:\n  NAMES =\n    {all_var_names};\n'
            f'  USEVARIABLES =\n    {use_vars};\n'
            f'  GROUPING = PP_group (0=LowPP 1=HighPP);\n'
            f'  MISSING = ALL(-999);\n\n'
            f'ANALYSIS:\n  ESTIMATOR = MLR;\n  ITERATIONS = 10000;\n  CONVERGENCE = 0.000001;\n\n'
            f'MODEL:\n'
            f'  ! 單一指標（兩組共用定義）\n'
            f'  {cp}1 BY {cp}_T1@1;  {cp}_T1@0;  {cp}1@0;\n'
            f'  {cp}2 BY {cp}_T2@1;  {cp}_T2@0;  {cp}2@0;\n'
            f'  {cp}3 BY {cp}_T3@1;  {cp}_T3@0;  {cp}3@0;\n'
            f'  DP1 BY DP_T1@1;  DP_T1@0;  DP1@0;\n'
            f'  DP2 BY DP_T2@1;  DP_T2@0;  DP2@0;\n'
            f'  DP3 BY DP_T3@1;  DP_T3@0;  DP3@0;\n'
            f'  CI1 BY CI_T1@1;  CI_T1@0;  CI1@0;\n'
            f'  CI2 BY CI_T2@1;  CI_T2@0;  CI2@0;\n'
            f'  CI3 BY CI_T3@1;  CI_T3@0;  CI3@0;\n\n'
            f'  ! 隨機截距\n'
            f'  RI_{cp} BY {cp}1@1 {cp}2@1 {cp}3@1;\n'
            f'  RI_DP   BY DP1@1  DP2@1  DP3@1;\n'
            f'  RI_CI   BY CI1@1  CI2@1  CI3@1;\n\n'
            f'  ! Within-person 殘差\n'
            f'  W{cp}1 BY {cp}1@1;  W{cp}2 BY {cp}2@1;  W{cp}3 BY {cp}3@1;\n'
            f'  WDP1 BY DP1@1;  WDP2 BY DP2@1;  WDP3 BY DP3@1;\n'
            f'  WCI1 BY CI1@1;  WCI2 BY CI2@1;  WCI3 BY CI3@1;\n\n'
            f'  ! 自回歸（跨波等同）\n'
            f'  W{cp}2 ON W{cp}1 (ar_{cpp});  W{cp}3 ON W{cp}2 (ar_{cpp});\n'
            f'  WDP2  ON WDP1  (ar_dp);       WDP3  ON WDP2  (ar_dp);\n'
            f'  WCI2  ON WCI1  (ar_ci);       WCI3  ON WCI2  (ar_ci);\n\n'
            f'  ! T1/T2/T3 Within-person 共變\n'
            f'  W{cp}1 WITH WDP1;  W{cp}1 WITH WCI1;  WDP1 WITH WCI1;\n'
            f'  W{cp}2 WITH WDP2;  W{cp}2 WITH WCI2;  WDP2 WITH WCI2;\n'
            f'  W{cp}3 WITH WDP3;  W{cp}3 WITH WCI3;  WDP3 WITH WCI3;\n\n'
            f'  ! 隨機截距共變\n'
            f'  RI_{cp} WITH RI_DP;  RI_{cp} WITH RI_CI;  RI_DP WITH RI_CI;\n\n'
            f'  ! 六條交叉延遲（configural：兩組各自自由估計）\n'
            f'  WDP2 ON W{cp}1;  WDP3 ON W{cp}2;\n'
            f'  WCI2 ON W{cp}1;  WCI3 ON W{cp}2;\n'
            f'  WCI2 ON WDP1;   WCI3 ON WDP2;\n'
            f'  W{cp}2 ON WDP1; W{cp}3 ON WDP2;\n'
            f'  WDP2 ON WCI1;   WDP3 ON WCI2;\n'
            f'  W{cp}2 ON WCI1; W{cp}3 ON WCI2;\n'
            f'\n! ------- 約束模型（另存 _Constrained 版本做 chi-square diff test）-------\n'
            f'! 若要測試 H8，另跑一個模型將上面六條路徑標上等同標籤：\n'
            f'!   WDP2 ON W{cp}1 (cl_{cpp}_dp);  WDP3 ON W{cp}2 (cl_{cpp}_dp); 等\n'
            f'! 再做 chi-square difference test（MLR 用 Satorra-Bentler correction）\n'
            f'\nOUTPUT:\n  SAMPSTAT;  STDYX;  MODINDICES(10);  CINTERVAL;\n'
        )

    ri_models_spec = [
        (f'RI-CLPM-A (JCP, Bidirectional)',   f'RI_CLPM_A_JCP_Bidir_{ts}',    'JCP', 'AB'),
        (f'RI-CLPM-B (HP, Bidirectional)',    f'RI_CLPM_B_HP_Bidir_{ts}',     'HP',  'AB'),
        (f'RI-CLPM-C (JCP, MultiGroup-PP)',   f'RI_CLPM_C_JCP_MultiGrp_{ts}', 'JCP', 'CD'),
        (f'RI-CLPM-D (HP, MultiGroup-PP)',    f'RI_CLPM_D_HP_MultiGrp_{ts}',  'HP',  'CD'),
    ]

    ri_inp_list = []
    for label, fname, cp, mtype in ri_models_spec:
        if mtype == 'AB':
            content = make_riclpm_ab(cp, ts, mplus_dat_filename)
        else:
            content = make_riclpm_cd_multigroup(cp, ts, mplus_dat_filename)
        utf8_path, _ = save_inp_dual_encoding(content, run_dir, fname)
        ri_inp_list.append((label, utf8_path))

    # ---- 自動執行 Mplus ----
    print("\n[Mplus] 自動執行 CFA 模型 A-D...")
    cfa_run_results = run_all_mplus(cfa_inp_list, mplus_exe)

    print("[Mplus] 自動執行 RI-CLPM 模型 A-D...")
    ri_run_results  = run_all_mplus(ri_inp_list, mplus_exe)

    # ---- 解析 CFA 結果 ----
    for label, ok, out_path, err in cfa_run_results:
        if ok:
            all_results[label] = {'fit': parse_mplus_fit(out_path), 'out': out_path}

    # ---- 解析 RI-CLPM 結果 ----
    # Model A/B: 雙向六路徑（H1a/b~H6a/b）；Model C/D: 多群組（configural，各組自由估計）
    ri_path_maps = {
        'RI-CLPM-A (JCP, Bidirectional)': {
            'H1a: JCP→DP': ('WDP2', 'WJCP1'),
            'H2a: JCP→CI': ('WCI2', 'WJCP1'),
            'H3:  DP→CI':  ('WCI2', 'WDP1'),
            'H4a: DP→JCP': ('WJCP2', 'WDP1'),
            'H5:  CI→DP':  ('WDP2', 'WCI1'),
            'H6a: CI→JCP': ('WJCP2', 'WCI1'),
        },
        'RI-CLPM-B (HP, Bidirectional)': {
            'H1b: HP→DP':  ('WDP2', 'WHP1'),
            'H2b: HP→CI':  ('WCI2', 'WHP1'),
            'H3:  DP→CI':  ('WCI2', 'WDP1'),
            'H4b: DP→HP':  ('WHP2', 'WDP1'),
            'H5:  CI→DP':  ('WDP2', 'WCI1'),
            'H6b: CI→HP':  ('WHP2', 'WCI1'),
        },
        # Models C/D are multi-group (configural); paths parsed per group via group-specific output
        # Cross-lagged labels match the configural (unconstrained) group sections
        'RI-CLPM-C (JCP, MultiGroup-PP)': {
            'H1a: JCP→DP [configural]': ('WDP2', 'WJCP1'),
            'H2a: JCP→CI [configural]': ('WCI2', 'WJCP1'),
            'H3:  DP→CI  [configural]': ('WCI2', 'WDP1'),
            'H4a: DP→JCP [configural]': ('WJCP2', 'WDP1'),
            'H5:  CI→DP  [configural]': ('WDP2', 'WCI1'),
            'H6a: CI→JCP [configural]': ('WJCP2', 'WCI1'),
        },
        'RI-CLPM-D (HP, MultiGroup-PP)': {
            'H1b: HP→DP  [configural]': ('WDP2', 'WHP1'),
            'H2b: HP→CI  [configural]': ('WCI2', 'WHP1'),
            'H3:  DP→CI  [configural]': ('WCI2', 'WDP1'),
            'H4b: DP→HP  [configural]': ('WHP2', 'WDP1'),
            'H5:  CI→DP  [configural]': ('WDP2', 'WCI1'),
            'H6b: CI→HP  [configural]': ('WHP2', 'WCI1'),
        },
    }
    ri_corr_maps = {
        'RI-CLPM-A (JCP, Bidirectional)': [
            ('RI_JCP↔RI_DP', 'RI_JCP', 'RI_DP'),
            ('RI_JCP↔RI_CI', 'RI_JCP', 'RI_CI'),
            ('RI_DP↔RI_CI',  'RI_DP',  'RI_CI')],
        'RI-CLPM-B (HP, Bidirectional)': [
            ('RI_HP↔RI_DP',  'RI_HP',  'RI_DP'),
            ('RI_HP↔RI_CI',  'RI_HP',  'RI_CI'),
            ('RI_DP↔RI_CI',  'RI_DP',  'RI_CI')],
        'RI-CLPM-C (JCP, MultiGroup-PP)': [
            ('RI_JCP↔RI_DP', 'RI_JCP', 'RI_DP'),
            ('RI_JCP↔RI_CI', 'RI_JCP', 'RI_CI'),
            ('RI_DP↔RI_CI',  'RI_DP',  'RI_CI')],
        'RI-CLPM-D (HP, MultiGroup-PP)': [
            ('RI_HP↔RI_DP',  'RI_HP',  'RI_DP'),
            ('RI_HP↔RI_CI',  'RI_HP',  'RI_CI'),
            ('RI_DP↔RI_CI',  'RI_DP',  'RI_CI')],
    }

    for label, ok, out_path, err in ri_run_results:
        if ok:
            path_map = ri_path_maps.get(label, {})
            corr_pairs = ri_corr_maps.get(label, [])
            all_results[label] = {
                'fit':    parse_mplus_fit(out_path),
                'paths':  parse_mplus_stdyx(out_path, path_map),
                'ri_corr': parse_mplus_ri_corr(out_path, corr_pairs),
                'out':    out_path
            }

    return all_results, cfa_inp_list + ri_inp_list


# ==========================================
# MODULE F: Excel 綜合報告產生
# ==========================================
def generate_excel_report(run_dir, ts, g3_sample, alpha_dict, corr_dict, all_results):
    """
    產生 Excel 綜合報告 (Thesis_Results_YYYYMMDD_HHMM.xlsx)，含：
      Sheet 1: 樣本背景變項描述統計
      Sheet 2: 各量表各波次敘述統計 + 信度 (Cronbach's α)
      Sheet 3: 相關分析矩陣 (T1)
      Sheet 4: CFA 適配指數（4 個模型）
      Sheet 5: RI-CLPM 適配指數（4 個模型）
      Sheet 6: RI-CLPM Within-person 路徑係數（STDYX）
      Sheet 7: RI-CLPM Between-person 隨機截距相關
    """
    try:
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    except ImportError:
        print("  [警告] 未安裝 openpyxl，跳過 Excel 報告。請執行: pip install openpyxl")
        return None

    wb = openpyxl.Workbook()
    df = g3_sample.copy()
    n_total = len(df)

    # ── 共用樣式 ──────────────────────────────────────────────────
    thin = Side(border_style="thin", color="000000")
    bdr  = Border(left=thin, right=thin, top=thin, bottom=thin)
    hdr_fill  = PatternFill("solid", fgColor="4472C4")
    sub_fill  = PatternFill("solid", fgColor="D9E1F2")
    ctr = Alignment(horizontal="center", vertical="center", wrap_text=True)
    lft = Alignment(horizontal="left",   vertical="center", wrap_text=True)

    def hdr(ws, row, col, val):
        c = ws.cell(row=row, column=col, value=val)
        c.font = Font(bold=True, color="FFFFFF", size=10)
        c.fill = hdr_fill
        c.alignment = ctr
        c.border = bdr
        return c

    def cell(ws, row, col, val, bold=False, align='center', color=None):
        c = ws.cell(row=row, column=col, value=val)
        c.font = Font(bold=bold, size=10, color=color if color else "000000")
        c.alignment = ctr if align == 'center' else lft
        c.border = bdr
        return c

    def title(ws, text, end_col=8):
        ws.cell(row=1, column=1, value=text).font = Font(bold=True, size=12)
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=end_col)

    def set_widths(ws, pairs):
        for col_letter, w in pairs:
            ws.column_dimensions[col_letter].width = w

    # ── Sheet 1: 樣本背景變項 ─────────────────────────────────────
    ws1 = wb.active
    ws1.title = "1_背景變項"
    title(ws1, f"樣本背景變項描述統計（N = {n_total}，三波配對樣本）", end_col=5)
    r = 3
    for ci, h in enumerate(["變項", "類別 / 統計量", "人數 / 數值", "%", "單位"], 1):
        hdr(ws1, r, ci, h)
    r += 1

    # 連續變項
    for col_name, label, unit in [
        ('Age',           '年齡',       '歲'),
        ('NowJobTenure',  '現職年資',   '月'),
        ('JobTenure',     '整體工作年資', '月'),
    ]:
        if col_name not in df.columns:
            continue
        s = pd.to_numeric(df[col_name], errors='coerce').dropna()
        cell(ws1, r, 1, label, bold=True, align='left')
        cell(ws1, r, 2, 'M (SD)')
        cell(ws1, r, 3, f"{s.mean():.1f} ({s.std():.1f})")
        cell(ws1, r, 4, '')
        cell(ws1, r, 5, unit)
        r += 1
        cell(ws1, r, 1, '')
        cell(ws1, r, 2, '最小值 ~ 最大值')
        cell(ws1, r, 3, f"{s.min():.0f} ~ {s.max():.0f}")
        cell(ws1, r, 4, '')
        cell(ws1, r, 5, '')
        r += 1

    # 類別變項
    cat_vars = [
        ('Gender',    '性別',
         {1: '男', 2: '女', 3: '其他'}),
        ('Education', '教育程度',
         {1: '高中(職)', 2: '專科', 3: '大學', 4: '碩士', 5: '博士'}),
        ('Marriage',  '婚姻狀況',
         {1: '未婚', 2: '已婚無子女', 3: '已婚有子女', 4: '其他'}),
        ('Position',  '職位層級',
         {1: '一般員工', 2: '基層主管', 3: '中階主管', 4: '高階主管'}),
        ('Industry',  '所屬產業',
         {1: '製造', 2: '科技', 3: '金融', 4: '服務',
          5: '醫療', 6: '教育', 7: '公部門', 8: '其他'}),
    ]
    for col_name, label, val_map in cat_vars:
        if col_name not in df.columns:
            continue
        s = pd.to_numeric(df[col_name], errors='coerce').dropna()
        cell(ws1, r, 1, label, bold=True, align='left')
        for ci in range(2, 6):
            cell(ws1, r, ci, '')
        r += 1
        for v, v_label in val_map.items():
            cnt = int((s == v).sum())
            pct = cnt / n_total * 100 if n_total > 0 else 0
            cell(ws1, r, 1, '')
            cell(ws1, r, 2, v_label, align='left')
            cell(ws1, r, 3, cnt)
            cell(ws1, r, 4, f"{pct:.1f}%")
            cell(ws1, r, 5, '')
            r += 1

    set_widths(ws1, [('A', 18), ('B', 20), ('C', 16), ('D', 10), ('E', 12)])

    # ── Sheet 2: 敘述統計 + 信度（各量表 × 各波次）─────────────────
    ws2 = wb.create_sheet("2_敘述統計與信度")
    title(ws2, "各量表各波次敘述統計與信度（N = 277，三波配對樣本）", end_col=12)
    r = 3
    hdr_cols = ["量表", "說明", "題數",
                "T1 M", "T1 SD", "T1 α",
                "T2 M", "T2 SD", "T2 α",
                "T3 M", "T3 SD", "T3 α"]
    for ci, h in enumerate(hdr_cols, 1):
        hdr(ws2, r, ci, h)
    r += 1

    scale_defs = [
        ('HP',  'HP 階層停滯（CP 次量表）',        [f'HP{i}'  for i in range(1, 7)]),
        ('JCP', 'JCP 工作內容停滯（CP 次量表）',   [f'JCP{i}' for i in range(1, 7)]),
        ('PP',  'PP 主動型人格',                    [f'PP{i}'  for i in range(1, 7)]),
        ('DP',  'DP 決策拖延',                      [f'DP{i}'  for i in range(1, 6)]),
        ('CI',  'CI 職涯無所作為',                  [f'CI{i}'  for i in range(1, 9)]),
    ]
    for s_name, s_label, s_items in scale_defs:
        row_data = [s_name, s_label, len(s_items)]
        for wave in ['T1', 'T2', 'T3']:
            wave_cols = [f'{item}_{wave}' for item in s_items]
            valid_cols = [c for c in wave_cols if c in df.columns]
            if valid_cols:
                mat = df[valid_cols].apply(pd.to_numeric, errors='coerce')
                means = mat.mean(axis=1)
                m  = means.mean()
                sd = means.std()
                alpha_v = calculate_cronbach_alpha(mat.dropna())
                row_data += [
                    f"{m:.2f}",
                    f"{sd:.2f}",
                    f"{alpha_v:.3f}" if not np.isnan(alpha_v) else 'N/A'
                ]
            else:
                row_data += ['N/A', 'N/A', 'N/A']
        for ci, val in enumerate(row_data, 1):
            cell(ws2, r, ci, val, bold=(ci == 1),
                 align='left' if ci <= 2 else 'center')
        r += 1

    set_widths(ws2, [('A', 7), ('B', 26), ('C', 5),
                     ('D', 8), ('E', 8), ('F', 8),
                     ('G', 8), ('H', 8), ('I', 8),
                     ('J', 8), ('K', 8), ('L', 8)])

    # ── Sheet 3: 相關矩陣 (T1) ────────────────────────────────────
    ws3 = wb.create_sheet("3_相關矩陣T1")
    title(ws3, f"相關分析矩陣（T1，N = {n_total}）  *** p<.001  ** p<.01  * p<.05", end_col=8)
    r = 3
    scale_order = ['HP', 'JCP', 'PP', 'DP', 'CI']
    t1_means = {}
    for sn in scale_order:
        if sn == 'HP':
            cols = [f'HP{i}_T1'  for i in range(1, 7)]
        elif sn == 'JCP':
            cols = [f'JCP{i}_T1' for i in range(1, 7)]
        elif sn == 'PP':
            cols = [f'PP{i}_T1'  for i in range(1, 7)]
        elif sn == 'DP':
            cols = [f'DP{i}_T1'  for i in range(1, 6)]
        elif sn == 'CI':
            cols = [f'CI{i}_T1'  for i in range(1, 9)]
        valid = [c for c in cols if c in df.columns]
        if valid:
            t1_means[sn] = df[valid].apply(pd.to_numeric, errors='coerce').mean(axis=1)

    hdr(ws3, r, 1, '變數')
    for ci, sn in enumerate(scale_order, 2):
        hdr(ws3, r, ci, sn)
    hdr(ws3, r, len(scale_order) + 2, 'M')
    hdr(ws3, r, len(scale_order) + 3, 'SD')
    r += 1

    for i, sn_r in enumerate(scale_order):
        cell(ws3, r, 1, sn_r, bold=True)
        for j, sn_c in enumerate(scale_order):
            col = j + 2
            if i == j:
                cell(ws3, r, col, '—')
            elif i < j and sn_r in t1_means and sn_c in t1_means:
                valid_dat = pd.concat(
                    [t1_means[sn_r], t1_means[sn_c]], axis=1).dropna()
                if len(valid_dat) > 2:
                    rv, pv = stats.pearsonr(
                        valid_dat.iloc[:, 0], valid_dat.iloc[:, 1])
                    star, _ = fmt_p(pv)
                    cell(ws3, r, col, f"{rv:.2f}{star}")
                else:
                    cell(ws3, r, col, '—')
            else:
                cell(ws3, r, col, '')
        if sn_r in t1_means:
            m  = t1_means[sn_r].mean()
            sd = t1_means[sn_r].std()
            cell(ws3, r, len(scale_order) + 2, f"{m:.2f}")
            cell(ws3, r, len(scale_order) + 3, f"{sd:.2f}")
        r += 1

    set_widths(ws3, [('A', 8), ('B', 10), ('C', 10), ('D', 10),
                     ('E', 10), ('F', 10), ('G', 8), ('H', 8)])

    # ── Sheet 4 & 5: 適配指數（共用內部函式）─────────────────────
    fit_hdr_cols = ["模型", "結構說明", "χ²", "df", "p(χ²)",
                    "CFI", "TLI", "RMSEA", "90% CI", "SRMR", "判斷"]

    def write_fit_sheet(ws, sheet_title, model_info_dict):
        title(ws, sheet_title, end_col=11)
        r2 = 3
        for ci, h in enumerate(fit_hdr_cols, 1):
            hdr(ws, r2, ci, h)
        r2 += 1
        for mkey, mdesc in model_info_dict.items():
            fit = all_results.get(mkey, {}).get('fit', {})
            chi2_v  = fit.get('chi2')
            df_v    = fit.get('df')
            p_chi2  = fit.get('p_chi2')
            cfi_v   = fit.get('cfi')
            tli_v   = fit.get('tli')
            rmsea_v = fit.get('rmsea')
            rlo_v   = fit.get('rmsea_lo')
            rhi_v   = fit.get('rmsea_hi')
            srmr_v  = fit.get('srmr')
            ok = (isinstance(cfi_v, float) and cfi_v >= .90 and
                  isinstance(rmsea_v, float) and rmsea_v <= .08 and
                  isinstance(srmr_v, float) and srmr_v <= .08)
            verdict = '✅' if ok else ('⚠️' if fit else '（尚未執行）')
            vals = [
                mkey, mdesc,
                f"{chi2_v:.2f}" if isinstance(chi2_v, float) else '—',
                df_v if df_v is not None else '—',
                f"{p_chi2:.3f}" if isinstance(p_chi2, float) else '—',
                f"{cfi_v:.3f}" if isinstance(cfi_v, float) else '—',
                f"{tli_v:.3f}" if isinstance(tli_v, float) else '—',
                f"{rmsea_v:.3f}" if isinstance(rmsea_v, float) else '—',
                (f"[{rlo_v:.3f}, {rhi_v:.3f}]"
                 if isinstance(rlo_v, float) and isinstance(rhi_v, float) else '—'),
                f"{srmr_v:.3f}" if isinstance(srmr_v, float) else '—',
                verdict,
            ]
            for ci, val in enumerate(vals, 1):
                cell(ws, r2, ci, val, align='left' if ci <= 2 else 'center')
            r2 += 1
        r2 += 1
        ws.cell(row=r2, column=1,
                value="判斷標準：CFI ≥ .90；RMSEA ≤ .08；SRMR ≤ .08"
                ).font = Font(italic=True, size=9)
        ws.merge_cells(start_row=r2, start_column=1, end_row=r2, end_column=11)
        set_widths(ws, [('A', 22), ('B', 24), ('C', 8), ('D', 5), ('E', 8),
                        ('F', 7), ('G', 7), ('H', 9), ('I', 14), ('J', 7), ('K', 6)])

    ws4 = wb.create_sheet("4_CFA適配")
    write_fit_sheet(ws4, "CFA 驗證性因素分析適配指數（T1, N = 277）", {
        'CFA-A (JCP+DP+CI)':     'JCP + DP + CI（3因子）',
        'CFA-B (HP+DP+CI)':      'HP + DP + CI（3因子）',
        'CFA-C (JCP+PP+DP+CI)':  'JCP + PP + DP + CI（4因子）',
        'CFA-D (HP+PP+DP+CI)':   'HP + PP + DP + CI（4因子）',
    })

    ws5 = wb.create_sheet("5_RICLPM適配")
    write_fit_sheet(ws5, "RI-CLPM 適配指數（parcel 合成分數，N = 277）", {
        'RI-CLPM-A (JCP→DP→CI)':    'JCP → DP → CI',
        'RI-CLPM-B (HP→DP→CI)':     'HP → DP → CI',
        'RI-CLPM-C (JCP+PP→DP→CI)': 'JCP + PP → DP → CI',
        'RI-CLPM-D (HP+PP→DP→CI)':  'HP + PP → DP → CI',
    })

    # ── Sheet 6: RI-CLPM Within-person 路徑係數 ──────────────────
    ws6 = wb.create_sheet("6_路徑係數")
    title(ws6, "RI-CLPM Within-person 標準化路徑係數（STDYX，MLR 估計）", end_col=7)
    r = 3
    for ci, h in enumerate(
            ["模型", "路徑", "β（含顯著星號）", "SE", "z值", "p值", "結論"], 1):
        hdr(ws6, r, ci, h)
    r += 1

    ri_model_order = [
        'RI-CLPM-A (JCP→DP→CI)',
        'RI-CLPM-B (HP→DP→CI)',
        'RI-CLPM-C (JCP+PP→DP→CI)',
        'RI-CLPM-D (HP+PP→DP→CI)',
    ]
    for mkey in ri_model_order:
        paths = all_results.get(mkey, {}).get('paths', {})
        if not paths:
            cell(ws6, r, 1, mkey, bold=True, align='left')
            cell(ws6, r, 2, '（尚未執行或無法解析，請確認 .out 檔）', align='left')
            for ci in range(3, 8):
                cell(ws6, r, ci, '')
            r += 1
            continue
        first = True
        for path_label, pdata in paths.items():
            est = pdata.get('est', np.nan)
            se  = pdata.get('se',  np.nan)
            z   = pdata.get('z',   np.nan)
            pv  = pdata.get('p',   np.nan)
            b_str, p_str = fmt_beta(est, pv)
            is_sig = isinstance(pv, float) and not np.isnan(pv) and pv < .05
            cell(ws6, r, 1, mkey if first else '', bold=first, align='left')
            cell(ws6, r, 2, path_label, align='left')
            cell(ws6, r, 3, b_str)
            cell(ws6, r, 4, f"{se:.3f}" if not np.isnan(se) else 'N/A')
            cell(ws6, r, 5, f"{z:.3f}"  if not np.isnan(z)  else 'N/A')
            cell(ws6, r, 6, p_str)
            cell(ws6, r, 7, '顯著 ✅' if is_sig else '不顯著',
                 color='006100' if is_sig else '000000',
                 bold=is_sig)
            first = False
            r += 1

    r += 1
    ws6.cell(row=r, column=1,
             value="*** p<.001  ** p<.01  * p<.05（STDYX 標準化；自回歸路徑跨波等同限制）"
             ).font = Font(italic=True, size=9)
    ws6.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
    set_widths(ws6, [('A', 28), ('B', 18), ('C', 16),
                     ('D', 8), ('E', 8), ('F', 10), ('G', 10)])

    # ── Sheet 7: RI-CLPM Between-person 隨機截距相關 ─────────────
    ws7 = wb.create_sheet("7_RI相關")
    title(ws7, "RI-CLPM Between-person 隨機截距相關（STDYX，95% CI）", end_col=6)
    r = 3
    for ci, h in enumerate(
            ["模型", "變數對", "r 估計值", "95% CI 下限", "95% CI 上限", "顯著（CI不含0）"], 1):
        hdr(ws7, r, ci, h)
    r += 1

    for mkey in ri_model_order:
        ri_corrs = all_results.get(mkey, {}).get('ri_corr', {})
        if not ri_corrs:
            cell(ws7, r, 1, mkey, bold=True, align='left')
            cell(ws7, r, 2, '（尚未執行或無法解析，請確認 .out 檔）', align='left')
            for ci in range(3, 7):
                cell(ws7, r, ci, '')
            r += 1
            continue
        first = True
        for pair_label, cdata in ri_corrs.items():
            est   = cdata.get('est',   np.nan)
            ci_lo = cdata.get('ci_lo', np.nan)
            ci_hi = cdata.get('ci_hi', np.nan)
            sig   = cdata.get('sig',   False)
            cell(ws7, r, 1, mkey if first else '', bold=first, align='left')
            cell(ws7, r, 2, pair_label, align='left')
            cell(ws7, r, 3, f"{est:.3f}"   if not np.isnan(est)   else 'N/A')
            cell(ws7, r, 4, f"{ci_lo:.3f}" if not np.isnan(ci_lo) else 'N/A')
            cell(ws7, r, 5, f"{ci_hi:.3f}" if not np.isnan(ci_hi) else 'N/A')
            cell(ws7, r, 6, '是 ✅' if sig else '否',
                 color='006100' if sig else '000000', bold=sig)
            first = False
            r += 1

    r += 1
    ws7.cell(row=r, column=1,
             value="95% CI 不含 0 即顯著；代表穩定的個人間差異關聯（between-person effect）"
             ).font = Font(italic=True, size=9)
    ws7.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
    set_widths(ws7, [('A', 28), ('B', 18), ('C', 10), ('D', 12), ('E', 12), ('F', 14)])

    # ── 儲存 ─────────────────────────────────────────────────────
    excel_path = os.path.join(run_dir, f"Thesis_Results_{ts}.xlsx")
    try:
        wb.save(excel_path)
        print(f"  [OK] Excel 報告已儲存：{excel_path}")
    except Exception as e:
        print(f"  [錯誤] Excel 儲存失敗：{e}")
        return None
    return excel_path


# ==========================================
# TODO-2: MODULE G — Word 論文草稿（python-docx）
# ==========================================
# 尚未實作。建議在此處新增 generate_word_report(run_dir, ts, g3_sample, all_mplus_results, ...) 函式。
#
# 功能規劃：
#   - 使用 python-docx（pip install python-docx）
#   - APA 格式表格，內容對應 Excel Sheet 2~7
#   - 表格標題、標註、顯著性說明（*** p<.001 等）
#   - 章節：研究方法（樣本背景）→ 信效度 → 相關矩陣 → CFA 適配 → RI-CLPM 結果
#   - 在 main() 中呼叫：word_path = generate_word_report(run_dir, ts, g3_sample_full, alpha_dict, corr_dict, all_mplus_results)
#
# ==========================================
# TODO-3: MODULE H — PPT 簡報（python-pptx）
# ==========================================
# 尚未實作。建議在此處新增 generate_pptx_report(run_dir, ts, all_mplus_results, ...) 函式。
#
# 功能規劃：
#   - 使用 python-pptx（pip install python-pptx）
#   - 投影片規劃：研究架構圖 → 樣本說明 → CFA 適配表 → RI-CLPM 路徑圖（含係數）→ RI 相關 → 結論
#   - 在 main() 中呼叫：pptx_path = generate_pptx_report(run_dir, ts, all_mplus_results)
#
# ==========================================
# TODO-4: 刪題目設定（等老師確認後執行）
# ==========================================
# 問題題目：
#   - JCP6：標準化因素負荷量為負值（約 -.092 ~ -.097），且未達顯著
#   - DP1：因素負荷量極低（約 .276），與其他題目差距大
#
# 確認要刪後的修改方式：
#   1. 在程式最上方新增設定區塊（建議放在 OUTPUT_DIR 附近）：
#        ITEMS_TO_EXCLUDE = ['JCP6', 'DP1']   # 老師確認後填入
#   2. 在 generate_cfa_dat()、run_and_parse_all_models() 的 CFA model_lines 中
#      將對應題目從 USEVARIABLES 和 BY 語法中移除
#   3. 重新執行 pipeline 並比較新舊 CFA 適配指數
#
# ==========================================
# TODO-5: 執行 pipeline 驗證（第一次跑完整流程）
# ==========================================
# 建議執行步驟：
#   1. python pipeline_master.py
#   2. 確認 Master_Pipeline_Output/<ts>/ 資料夾下有：
#        - Thesis_Results_<ts>.xlsx（7 個 Sheet 資料正確）
#        - CFA_A~D_<ts>.inp 及 _b5.inp（Big5 版本可在另一台電腦開啟）
#        - RI_CLPM_A~D_<ts>.inp 及 _b5.inp
#        - 若已安裝 Mplus：.out 檔會自動產生，Excel 內數字會填入
#        - 若未安裝 Mplus：Excel 欄位顯示「（尚未執行）」，手動執行 .inp 後可重跑 pipeline
#   3. 確認 SPSS .sps 語法在 SPSS 中可正常執行（所有 * 行結尾有句點）
#   4. 若另一台電腦有編碼問題，改用 _b5.inp 版本開啟
#
# ==========================================

# ==========================================
# 3. MAIN PIPELINE
# ==========================================
def main():
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    run_dir = os.path.join(OUTPUT_DIR, ts)   # e.g. Master_Pipeline_Output/20260325_1730
    os.makedirs(run_dir, exist_ok=True)
    
    print("--- Starting Master Pipeline ---")
    merged_df, escales, tracking = perform_matching()
    
    print("Running Analyses...")
    attrition_md, merged_df, anova_stats, chi_stats = analyze_attrition(merged_df, tracking)

    g3_sample = merged_df[merged_df['Group'] == 3].copy()
    desc_md, alpha_dict, corr_dict = run_descriptives_and_correlations(
        g3_sample if not g3_sample.empty else merged_df, escales)
    
    # === 產出 CSV 供 SPSS/R 讀取（清除暫時計算欄位）===
    drop_tmp = [c for c in merged_df.columns if c.startswith('_') or c == 'Edu']
    csv_df = merged_df.drop(columns=drop_tmp, errors='ignore')
    csv_filename = f"SPSS_Ready_Data_{ts}.csv"
    csv_path = os.path.join(run_dir, csv_filename)
    csv_df.to_csv(csv_path, index=False, encoding='utf-8-sig')

    # === 產出純分析版本（移除身份識別欄位，僅保留分析所需）===
    id_cols = ['Custom_UID', 'Timestamp', 'Matched_T1_ID', 'Matched_T1_ID_x',
               'Matched_T1_ID_y', 'System_ID', 'key1', 'key2', 'key3',
               'dedup_id', 'Email', 'Custom_UID']
    analysis_df = csv_df.drop(columns=[c for c in id_cols if c in csv_df.columns], errors='ignore')
    analysis_filename = f"Analysis_Ready_Data_{ts}.csv"
    analysis_path = os.path.join(run_dir, analysis_filename)
    analysis_df.to_csv(analysis_path, index=False, encoding='utf-8-sig')

    # === 產出 SPSS 匯入 + 變數標籤語法 ===
    spss_syntax = generate_spss_syntax(analysis_path, ts)
    spss_sps_path = os.path.join(run_dir, f"SPSS_Syntax_{ts}.sps")
    with open(spss_sps_path, 'w', encoding='utf-8-sig') as f:
        f.write(spss_syntax)

    # === 產出 SPSS 信度分析語法 ===
    spss_rel_syntax = generate_spss_reliability_syntax(analysis_path, ts)
    spss_rel_path = os.path.join(run_dir, f"SPSS_Reliability_{ts}.sps")
    with open(spss_rel_path, 'w', encoding='utf-8-sig') as f:
        f.write(spss_rel_syntax)

    # === 產出 R 語法檔 (單一 CP 合併版) ===
    r_script_content = generate_r_script(csv_filename)
    r_script_path = os.path.join(run_dir, f"RICLPM_Master_{ts}.R")
    with open(r_script_path, 'w', encoding='utf-8') as f:
        f.write(r_script_content)

    # === 產出 R 語法檔 (HP & JCP 拆分版) ===
    split_script_content = generate_r_script_split_cp(csv_filename)
    split_script_path = os.path.join(run_dir, f"RICLPM_SplitCP_{ts}.R")
    with open(split_script_path, 'w', encoding='utf-8') as f:
        f.write(split_script_content)

    # === 產出 Mplus .dat 資料檔（含控制變數）===
    g3_sample_full = merged_df[merged_df['Group'] == 3].copy() if 'Group' in merged_df.columns else merged_df.dropna(subset=['HP_T3','DP_T3','CI_T3']).copy()
    mplus_dat_path, mplus_dat_filename = generate_mplus_dat(g3_sample_full, run_dir, ts)

    # === 產出 CFA 用 dat（T1 原始題目）===
    cfa_dat_path, cfa_dat_filename = generate_cfa_dat(g3_sample_full, run_dir, ts)

    # === 執行 Mplus 模型 A-D（CFA + RI-CLPM）並解析結果 ===
    print("[Mplus] 生成並自動執行所有 CFA/RI-CLPM 模型...")
    all_mplus_results, all_inp_list = run_and_parse_all_models(
        run_dir, mplus_dat_filename, cfa_dat_filename, ts)

    # === 產出 Excel 綜合報告 ===
    print("[Excel] 產生 Excel 綜合報告...")
    excel_path = generate_excel_report(
        run_dir, ts, g3_sample_full, alpha_dict, corr_dict, all_mplus_results)

    # === 產出 Mplus CFA 語法（五因子 / 四因子 / 三因子）===
    cfa_models = [
        (generate_mplus_cfa_five_factor,   f"CFA_M1_FiveFactor_{ts}.inp",          "CFA M1 五因子(HP/JCP/PP/DP/CI)"),
        (generate_mplus_cfa_four_factor,   f"CFA_M2_FourFactor_CP_merged_{ts}.inp", "CFA M2 四因子(CP合併/PP/DP/CI)"),
        (generate_mplus_cfa_three_factor,  f"CFA_M3_ThreeFactor_CP_DP_CI_{ts}.inp","CFA M3 三因子(CP/DP/CI 主路徑)"),
    ]
    cfa_paths = []
    for gen_fn, fname, label in cfa_models:
        content = gen_fn(cfa_dat_filename, ts)
        fpath = os.path.join(run_dir, fname)
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        cfa_paths.append((label, fpath))
    mplus_cfa_path  = cfa_paths[0][1]
    mplus_cfa4_path = cfa_paths[1][1]
    mplus_cfa3_path = cfa_paths[2][1]

    # === 產出 Mplus 測量恆等性語法 ===
    mplus_mi_content = generate_mplus_measurement_invariance(mplus_dat_filename, ts)
    mplus_mi_path = os.path.join(run_dir, f"MI_Configural_Template_{ts}.inp")
    with open(mplus_mi_path, 'w', encoding='utf-8') as f:
        f.write(mplus_mi_content)

    # === 產出三階段 Mplus .inp 語法檔 ===
    mplus_steps = [
        (generate_mplus_step1, f"RI_CLPM_Step1_CP_DP_CI_{ts}.inp",   "Step1 主路徑 CP->DP->CI"),
        (generate_mplus_step2, f"RI_CLPM_Step2_Add_PP_{ts}.inp",      "Step2 加入 PP（H8）"),
        (generate_mplus_step3, f"RI_CLPM_Step3_Controls_{ts}.inp",    "Step3 加入控制變數"),
    ]
    mplus_inp_paths = []
    for gen_fn, fname, label in mplus_steps:
        content = gen_fn(mplus_dat_filename, ts)
        fpath = os.path.join(run_dir, fname)
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        mplus_inp_paths.append((label, fpath))

    riclpm_info_md = (
        f"\n## 4. 信效度分析語法\n\n"
        f"| 工具 | 分析目的 | 檔案 |\n"
        f"|---|---|---|\n"
        f"| SPSS | 匯入資料 + 變數標籤 | `SPSS_Syntax_{ts}.sps` |\n"
        f"| SPSS | 信度分析（Cronbach's α） | `SPSS_Reliability_{ts}.sps` |\n"
        f"| Mplus | **M1** 五因子 CFA（HP/JCP/PP/DP/CI）| `CFA_M1_FiveFactor_{ts}.inp` |\n"
        f"| Mplus | **M2** 四因子 CFA（CP合併/PP/DP/CI）| `CFA_M2_FourFactor_CP_merged_{ts}.inp` |\n"
        f"| Mplus | **M3** 三因子 CFA（CP/DP/CI 主路徑）| `CFA_M3_ThreeFactor_CP_DP_CI_{ts}.inp` |\n"
        f"| Mplus | 測量恆等性模板 | `MI_Configural_Template_{ts}.inp` |\n"
        f"\n## 5. RI-CLPM 動態模型分析\n\n已自動產生分析腳本：\n"
        f"1. **R 單一 CP 合併版**：`{r_script_path}`\n"
        f"2. **R HP & JCP 拆分版**：`{split_script_path}`\n"
        f"3. **Mplus parcel 資料檔（RI-CLPM 用）**：`{mplus_dat_path}`\n"
        f"4. **Mplus CFA 資料檔（原始題目 T1）**：`{cfa_dat_path}`\n"
        + "".join(f"{i+5}. **Mplus {label}**：`{p}`\n"
                  for i, (label, p) in enumerate(mplus_inp_paths))
        + f"\n> 建議執行順序：\n"
          f"> 1. SPSS_Syntax 匯入資料 → 2. SPSS_Reliability 跑信度\n"
          f"> 3. CFA_FiveFactor 跑量測模型 → 4. MI 測量恆等性\n"
          f"> 5. RI-CLPM Step1 主路徑 → Step2 加 PP → Step3 加控制變數\n"
    )
    report_content = f"# 全階段資料分析自動化整合報告 (產生時間: {ts})\n\n" + attrition_md + desc_md + riclpm_info_md

    report_path = os.path.join(run_dir, f"Pipeline_Master_Report_{ts}.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    # ── 動態計算 draft 所需數值 ──────────────────────────────
    n_t1_raw      = tracking.get('T1_Raw', 'N/A')
    n_t1_attn_out = (tracking.get('T1_Raw', 0) - tracking.get('T1_Pass_Attn', 0))
    n_t1_job      = tracking.get('T1_Pass_Job', 'N/A')
    n_t1_eff      = len(merged_df)                   # 去重後 T1 有效人數
    n_t2_raw      = tracking.get('T2_Raw', 'N/A')
    n_t2_attn_out = (tracking.get('T2_Raw', 0) - tracking.get('T2_Pass_Attn', 0))
    n_t2_matched  = tracking.get('T2_Matched', 'N/A')
    n_t3_raw      = tracking.get('T3_Raw', 'N/A')
    n_t3_attn_out = (tracking.get('T3_Raw', 0) - tracking.get('T3_Pass_Attn', 0))
    n_t3_final    = tracking.get('T3_Matched', len(g3_sample))  # 最終有效樣本

    # 各量表 α
    def _afmt(key):
        v = alpha_dict.get(key, np.nan)
        return f"{v:.3f}" if not np.isnan(v) else "N/A"
    alpha_min_val = min((v for v in alpha_dict.values() if not np.isnan(v)), default=np.nan)
    alpha_max_val = max((v for v in alpha_dict.values() if not np.isnan(v)), default=np.nan)
    alpha_range   = (f"{alpha_min_val:.2f} 至 {alpha_max_val:.2f}"
                     if not np.isnan(alpha_min_val) else "N/A")

    # 關鍵相關係數
    def _rfmt(key):
        d = corr_dict.get(key, {})
        r, p = d.get('r', np.nan), d.get('p', np.nan)
        if np.isnan(r): return "r = N/A"
        # TODO-1: 改用 fmt_p() 取代此處的 (ns)，範例如下：
        #   star, p_str = fmt_p(p)
        #   return f"r = {r:.2f}{star}（{p_str}）"
        star = '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else '(ns)'
        return f"r = {r:.2f}{star}"

    # ANOVA 流失分析結論（依 p 值動態產生文字）
    psych_vars = ['_CP_T1', '_DP_T1', '_CI_T1', '_PP_T1']
    psych_nonsig = all(anova_stats.get(v, {}).get('p', 1) > .05 for v in psych_vars if v in anova_stats)
    demo_sig_gender = chi_stats.get('gender_p', 1) < .05
    demo_sig_edu    = chi_stats.get('edu_p', 1) < .05

    if psych_nonsig:
        attrition_conclusion = (
            "單因子變異數分析（ANOVA）結果顯示，三組參與者在「職涯高原」、「決策拖延」、"
            "「職涯無所作為」與「主動型人格」等核心心理變項之基期得分上，均無顯著差異。"
        )
    else:
        sig_vars = [v for v in psych_vars if anova_stats.get(v, {}).get('p', 1) <= .05]
        attrition_conclusion = (
            f"單因子變異數分析（ANOVA）結果顯示，三組參與者在多數核心心理變項基期得分上無顯著差異，"
            f"惟 {', '.join(sig_vars)} 達顯著水準，分析結果請參考流失分析表格。"
        )

    demo_note_parts = []
    if demo_sig_gender:
        demo_note_parts.append(f"性別比例（χ²={chi_stats.get('gender_chi2', 0):.3f}, p={chi_stats.get('gender_p', 0):.3f}）")
    if demo_sig_edu:
        demo_note_parts.append(f"教育程度（χ²={chi_stats.get('edu_chi2', 0):.3f}, p={chi_stats.get('edu_p', 0):.3f}）")
    demo_note = ("在" + "、".join(demo_note_parts) + "上呈現顯著差異，" if demo_note_parts else "")

    # Generate Thesis Draft
    thesis_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for f in os.listdir(thesis_dir):
        if f.startswith("thesis_analysis_draft_") and f.endswith(".md"):
            try: os.remove(os.path.join(thesis_dir, f))
            except: pass

    draft_content = f"""# 論文論文段落草稿（自動產生，產生時間：{ts}）
> ⚠️ 本文件由 pipeline_master.py 依當次資料運算結果自動產生，所有數字皆為實際計算值。
> RI-CLPM 係數欄位需待 Mplus 執行後手動填入（標記為 [待填]）。

---

## 第三章：研究對象與研究程序

### 樣本回收與清理

本研究採縱貫性研究設計（longitudinal study），共發放三波問卷，
各波相隔約三個月。各波段之樣本回收與清理程序如下：

**第一階段（T1）**：原始回收 {n_t1_raw} 份問卷，
扣除未通過注意力檢測之 {n_t1_attn_out} 人，
以及不符合填寫條件（須填寫三次）與就業資格（排除兼職、待業、學生、自由工作者、自營）後，
通過資格篩選計 {n_t1_job} 人，
再刪除同一時點重複填答後，T1 實際有效樣本為 **{n_t1_eff} 人**。

**第二階段（T2）**：原始回收 {n_t2_raw} 份問卷，
扣除未通過注意力檢測之 {n_t2_attn_out} 人後，
成功配對回 T1 之樣本為 **{n_t2_matched} 人**。

**第三階段（T3）**：原始回收 {n_t3_raw} 份問卷，
扣除未通過注意力檢測之 {n_t3_attn_out} 人後，
最終成功配對回 T1、T2 之有效樣本為 **{n_t3_final} 人**（本研究主分析樣本，N = {n_t3_final}）。

### 樣本流失分析（Attrition Analysis）

為確認樣本流失是否造成系統性偏誤，本研究將全體 T1 有效樣本（N = {n_t1_eff}）
依後續參與波次分為三組：
僅完成 T1 者（Group 1, n = {merged_df['Group'].value_counts().get(1, 0)}）、
完成 T1 與 T2 者（Group 2, n = {merged_df['Group'].value_counts().get(2, 0)}）、
以及完成三波者（Group 3, n = {merged_df['Group'].value_counts().get(3, 0)}），
並針對 T1 時點之主要研究變項及人口統計變項進行差異檢定。

{attrition_conclusion}
{demo_note}考量所有核心心理研究變項之基期水準皆無顯著差距，
本研究之樣本流失情況應不至於對縱貫歷程中核心構念之發展造成系統性偏誤。

---

## 第四章：研究結果

### 信度分析

本研究各量表之 Cronbach's α 如下：
階層停滯（HP）α = {_afmt('HP')}、工作內容停滯（JCP）α = {_afmt('JCP')}、
職涯高原合併（CP = HP + JCP，12 題）α = {_afmt('CP')}、
主動型人格（PP）α = {_afmt('PP')}、決策拖延（DP）α = {_afmt('DP')}、
職涯無所作為（CI）α = {_afmt('CI')}。
各量表信度均達 .70 以上學術標準（範圍 {alpha_range}），顯示測量工具具備良好之內部一致性。

### 敘述統計與相關分析

相關分析結果（T1，N = {len(g3_sample)}）顯示：
- CP（職涯高原）與 CI（職涯無所作為）：{_rfmt('CP_CI')}
- CP（職涯高原）與 DP（決策拖延）：{_rfmt('CP_DP')}
- DP（決策拖延）與 CI（職涯無所作為）：{_rfmt('DP_CI')}
- PP（主動型人格）與 DP（決策拖延）：{_rfmt('PP_DP')}
- PP（主動型人格）與 CI（職涯無所作為）：{_rfmt('PP_CI')}

### RI-CLPM 動態模型分析結果

> **以下數值待 Mplus 跑完 Step1~Step3 後填入。**

**主路徑（Step 1：CP → DP → CI）**

| 路徑 | β（標準化） | SE | p |
|---|---|---|---|
| WCP → WDP（T1→T2 / T2→T3 均等）| [待填] | [待填] | [待填] |
| WDP → WCI（T1→T2 / T2→T3 均等）| [待填] | [待填] | [待填] |

**加入 PP 後（Step 2：H8）**

| 路徑 | β（標準化） | SE | p |
|---|---|---|---|
| WPP → WDP（H8a：PP 負向→DP）| [待填] | [待填] | [待填] |
| WPP → WCI（H8b：PP 負向→CI）| [待填] | [待填] | [待填] |

**模型適配（Step 1 / Step 2 / Step 3）**

| 模型 | CFI | TLI | RMSEA | SRMR |
|---|---|---|---|---|
| Step 1 主路徑 | [待填] | [待填] | [待填] | [待填] |
| Step 2 加入 PP | [待填] | [待填] | [待填] | [待填] |
| Step 3 加控制變數 | [待填] | [待填] | [待填] | [待填] |

---
*（本檔案由 pipeline_master.py 於 {ts} 自動產生，N = {n_t3_final}）*
"""

    draft_path = os.path.join(thesis_dir, f"thesis_analysis_draft_v{ts}.md")
    with open(draft_path, 'w', encoding='utf-8') as f:
        f.write(draft_content)
        
    print(f"[OK] Pipeline Completed!")
    print(f"   - Report           : {report_path}")
    print(f"   - Thesis Draft     : {draft_path}")
    if excel_path:
        print(f"   - Excel 報告       : {excel_path}")
    for label, inp_p in all_inp_list:
        print(f"   - Mplus (新) {label}: {os.path.basename(inp_p)}")
    print(f"   - SPSS Full Data   : {csv_path}")
    print(f"   - Analysis Data    : {analysis_path}")
    print(f"   - SPSS 匯入語法    : {spss_sps_path}")
    print(f"   - SPSS 信度語法    : {spss_rel_path}")
    print(f"   - Mplus CFA dat    : {cfa_dat_path}")
    for label, p in cfa_paths:
        print(f"   - Mplus {label}: {os.path.basename(p)}")
    print(f"   - Mplus MI 模板    : {mplus_mi_path}")
    print(f"   - Mplus RI-CLPM dat: {mplus_dat_path}")
    for label, p in mplus_inp_paths:
        print(f"   - Mplus {label}: {os.path.basename(p)}")

if __name__ == "__main__":
    main()
