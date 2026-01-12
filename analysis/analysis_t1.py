import pandas as pd
import semopy
import numpy as np
import os
import glob
from scipy.stats import pearsonr
from datetime import datetime

# ==========================================
# 0. Helper Functions
# ==========================================

def calculate_cronbach_alpha(df):
    """
    Calculates Cronbach's Alpha for a given DataFrame of items.
    """
    df_corr = df.corr()
    N = df.shape[1]
    
    rs = np.array([])
    for i, col1 in enumerate(df_corr.columns):
        for j, col2 in enumerate(df_corr.columns):
            if i > j:
                rs = np.append(rs, df_corr.iloc[i, j])
    
    mean_r = np.mean(rs)
    alpha = (N * mean_r) / (1 + (N - 1) * mean_r)
    return alpha

def get_significance_stars(p_value):
    if p_value < 0.001: return '***'
    elif p_value < 0.01: return '**'
    elif p_value < 0.05: return '*'
    else: return ''

def calculate_ave_cr(loadings):
    """
    Calculates AVE and CR from factor loadings.
    Prioritizes 'Est. Std' (Standardized Estimates) if available.
    """
    results = []
    if loadings.empty: return pd.DataFrame()

    # Determine which column to use for loadings
    col_name = 'Est. Std' if 'Est. Std' in loadings.columns else 'Estimate'
    
    factors = loadings['lval'].unique()
    
    for factor in factors:
        # Filter for the specific factor
        factor_loadings = loadings[loadings['lval'] == factor][col_name]
        
        # Ensure we are working with floats
        factor_loadings = pd.to_numeric(factor_loadings, errors='coerce')
        
        lam_sq = factor_loadings ** 2
        sum_lam_sq = lam_sq.sum()
        sum_lam = factor_loadings.sum()
        
        # Error Variance (Standardized assumption: 1 - lam^2)
        # Clip loadings to 0.99 to avoid negative error variance if model is crazy
        clamped_loadings = factor_loadings.clip(upper=0.99)
        error_var = 1 - (clamped_loadings ** 2)
        sum_error = error_var.sum()
        
        ave = sum_lam_sq / (sum_lam_sq + sum_error)
        cr = (sum_lam ** 2) / ((sum_lam ** 2) + sum_error)
        
        results.append({
            "Variable": factor,
            "AVE": round(ave, 3),
            "CR": round(cr, 3),
            "Status": "Good" if ave > 0.5 and cr > 0.7 else "Check"
        })
        
    return pd.DataFrame(results)

def save_to_markdown(stats_df, corr_df, cfa_loadings, cfa_fit, ave_cr_df, error_msg=None, filename="Research_Result.md"):
    print(f"\nGenerating Markdown Report: {filename}...")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# Research Analysis Report\n\n")
        
        f.write("## Table 1. Descriptive Statistics and Reliability\n")
        f.write(stats_df.to_markdown(index=False))
        f.write("\n\n")
        
        f.write("## Table 2. Correlation Matrix\n")
        f.write(corr_df.to_markdown(index=False))
        f.write("\n\n")
        
        if error_msg:
            f.write("## ⚠️ Analysis Error\n")
            f.write(f"**The CFA Model failed to run:** {error_msg}\n")
            f.write("Tables 3, 4, and 5 are empty because the model could not be estimated.\n")
            f.write("Possible reasons: Missing data (NaN), Singular matrix, or variable name mismatch.\n\n")
        
        f.write("## Table 3. Model Fit Indices\n")
        if not cfa_fit.empty:
            # Write all columns to avoid missing data due to name mismatches
            f.write(cfa_fit.to_markdown(index=False))
        else:
            f.write("(No Data)\n")
        f.write("\n\n")
        
        f.write("## Table 4. Factor Loadings (Standardized)\n")
        if not cfa_loadings.empty:
            loadings = cfa_loadings[cfa_loadings['op'] == '=~'].copy()
            
            # Select appropriate columns for display
            display_cols = ['lval', 'rval', 'Estimate', 'p-value', 'Std. Err']
            if 'Est. Std' in loadings.columns:
                display_cols = ['lval', 'rval', 'Est. Std', 'p-value', 'Std. Err']
            
            # Filter existing columns only
            display_cols = [c for c in display_cols if c in loadings.columns]
            
            loadings = loadings[display_cols]
            
            # Round numeric columns
            for col in ['Estimate', 'Est. Std', 'p-value', 'Std. Err']:
                if col in loadings.columns:
                     loadings[col] = pd.to_numeric(loadings[col], errors='coerce').apply(lambda x: round(x, 3) if pd.notnull(x) else "")

            f.write(loadings.to_markdown(index=False))
        else:
            f.write("(No Data)\n")
        f.write("\n\n")

        f.write("## Table 5. Convergent Validity (CR & AVE)\n")
        if not ave_cr_df.empty:
            f.write(ave_cr_df.to_markdown(index=False))
        else:
            f.write("(No Data)\n")
        f.write("\n\n")

        
    print(f"Report saved to {filename}")

def generate_syntax_files(scale_items, timestamp):
    print("\nGenerating Syntax Files...")
    
    # 1. SPSS Syntax (.sps)
    with open(f"Syntax_SPSS_{timestamp}.sps", "w", encoding='utf-8') as f:
        f.write("* SPSS Syntax generated by Analysis Script.\n\n")
        
        for scale, items in scale_items.items():
            item_str = " ".join(items)
            f.write(f"* Reliability for {scale}.\n")
            f.write(f"RELIABILITY\n  /VARIABLES={item_str}\n  /SCALE('ALL VARIABLES') ALL\n  /MODEL=ALPHA.\n\n")
        
        scales = list(scale_items.keys())
        scale_str = " ".join(scales)
        f.write("* Correlation Analysis.\n")
        f.write("* Note: You must calculate scale means first in SPSS.\n")
        f.write(f"CORRELATIONS\n  /VARIABLES={scale_str}\n  /PRINT=TWOTAIL NOSIG\n  /MISSING=PAIRWISE.\n")
        
    print("Saved Syntax_SPSS.sps")

    # 2. Mplus Syntax (.inp)
    with open(f"Syntax_Mplus_{timestamp}.inp", "w", encoding='utf-8') as f:
        f.write("TITLE: CFA Analysis T1;\n")
        f.write("DATA: FILE IS data.dat;\n")
        f.write("VARIABLE:\n")
        
        all_items = []
        for items in scale_items.values():
            all_items.extend(items)
        
        names_str = "  NAMES ARE\n" 
        chunk = ""
        for item in all_items:
            if len(chunk) > 60:
                names_str += "    " + chunk + "\n"
                chunk = ""
            chunk += item + " "
        names_str += "    " + chunk + ";\n"
        
        f.write(names_str)
        f.write("  USEVARIABLES ARE ALL;\n\n")
        
        f.write("MODEL:\n")
        for scale, items in scale_items.items():
            item_str = " ".join(items)
            f.write(f"  {scale} BY {item_str};\n")
            
        f.write("\nOUTPUT: SAMPSTAT STANDARDIZED MODINDICES;\n")
        
    print("Saved Syntax_Mplus.inp")

    # 3. R Syntax (lavaan)
    with open(f"Syntax_R_{timestamp}.R", "w", encoding='utf-8') as f:
        f.write("# R Syntax using lavaan package\n")
        f.write("library(lavaan)\n\n")
        f.write("# 1. Load Data\n")
        f.write("data <- read.csv('T1_data.csv')\n\n")
        
        f.write("# 2. Define Model\n")
        f.write("model <- '\n")
        for scale, items in scale_items.items():
            item_str = " + ".join(items)
            f.write(f"  {scale} =~ {item_str}\n")
        f.write("'\n\n")
        
        f.write("# 3. Fit Model\n")
        f.write("fit <- cfa(model, data=data)\n\n")
        f.write("# 4. Summary & Fit Indices\n")
        f.write("summary(fit, fit.measures=TRUE, standardized=TRUE)\n")
        f.write("fitMeasures(fit, c('cfi', 'tli', 'rmsea', 'srmr'))\n")
        
    print("Saved Syntax_R.R")


# ==========================================
# 1. Load Data
# ==========================================
# Generate Timestamp for this run
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
print(f"Run Timestamp: {timestamp}")

# Define Scale Items
scale_items = {
    "HP": ["HP1", "HP2", "HP3", "HP4_R", "HP5", "HP6_R"],
    "JCP": ["JCP1_R", "JCP2_R", "JCP3_R", "JCP4_R", "JCP5_R", "JCP6"],
    "PP":  ["PP1", "PP2", "PP3", "PP4", "PP5", "PP6"],
    "DP":  ["DP1", "DP2", "DP3", "DP4", "DP5"],
    "CI":  ["CI1", "CI2", "CI3", "CI4", "CI5", "CI6", "CI7", "CI8"]
}

# Find latest CSV file matching pattern
search_pattern = 'T1_*_SPSS.csv'
list_of_files = glob.glob(search_pattern)

if list_of_files:
    latest_file = max(list_of_files, key=os.path.getmtime)
    print(f"Found {len(list_of_files)} data files. Using the latest: {latest_file}")
    data = pd.read_csv(latest_file)
else:
    print(f"Warning: No files matching '{search_pattern}' found. Generating MOCK data...")
    np.random.seed(42)
    N = 377
    data = pd.DataFrame()
    for scale, items in scale_items.items():
        pass # Generating in loop below...
        f = np.random.normal(0, 1, N)
        for i, col_name in enumerate(items):
            item_val = 0.7 * f + np.random.normal(0, 0.5, N)
            item_val = (item_val * 1.0) + 3.5
            item_val = np.clip(item_val, 1, 6)
            data[col_name] = item_val

# ==========================================
# 2. Reliability & Descriptive Statistics
# ==========================================
print("\n--- Reliability & Descriptive Statistics ---")
stats_list = []
scale_scores = pd.DataFrame()

cols_flat = [item for sublist in scale_items.values() for item in sublist]

# Pre-filter columns that might be missing
available_cols_flat = [c for c in cols_flat if c in data.columns]
if len(available_cols_flat) < len(cols_flat):
    missing = set(cols_flat) - set(available_cols_flat)
    print(f"Warning: Missing columns in CSV: {missing}")

for scale, items in scale_items.items():
    missing_cols = [c for c in items if c not in data.columns]
    if missing_cols: continue
        
    df_subset = data[items]
    alpha = calculate_cronbach_alpha(df_subset)
    scale_score = df_subset.mean(axis=1)
    scale_scores[scale] = scale_score
    
    stats_list.append({
        "Variable": scale,
        "Items": len(items),
        "Mean": round(scale_score.mean(), 2),
        "SD": round(scale_score.std(), 2),
        "Alpha": round(alpha, 2)
    })

stats_df = pd.DataFrame(stats_list)
stats_df.to_csv(f"descriptive_reliability_{timestamp}.csv", index=False)

# ==========================================
# 3. Correlation Matrix
# ==========================================
print("\n--- Correlation Matrix ---")
cols = stats_df['Variable'].tolist()
corr_data = []

if not stats_df.empty:
    for r in cols:
        row_data = {'Variable': r}
        for c in cols:
            if r == c:
                row_data[c] = '1.00'
            else:
                r_val, p_val = pearsonr(scale_scores[r], scale_scores[c])
                star = get_significance_stars(p_val)
                row_data[c] = f"{r_val:.2f}{star}"
        corr_data.append(row_data)

corr_df = pd.DataFrame(corr_data)
corr_df.to_csv(f"correlation_matrix_{timestamp}.csv", index=False)

# ==========================================
# 4. CFA & Validity
# ==========================================
model_desc = """
    HP =~ HP1 + HP2 + HP3 + HP4_R + HP5 + HP6_R
    JCP =~ JCP1_R + JCP2_R + JCP3_R + JCP4_R + JCP5_R
    PP =~ PP1 + PP2 + PP3 + PP4 + PP5 + PP6
    DP =~ DP1 + DP2 + DP3 + DP4 + DP5
    CI =~ CI1 + CI2 + CI3 + CI4 + CI5 + CI6 + CI7 + CI8
"""

print("\nRunning CFA Model...")
cfa_loadings = pd.DataFrame()
cfa_fit = pd.DataFrame()
ave_cr_df = pd.DataFrame()
error_msg = None

try:
    # 1. Prepare Data for CFA (Drop Missing)
    cfa_data = data[available_cols_flat].dropna()
    print(f"Observations for CFA: {len(cfa_data)} (Original: {len(data)})")
    
    if len(cfa_data) < 10:
        raise ValueError("Too few observations after dropping missing values.")

    # 2. Fit Model
    model = semopy.Model(model_desc)
    model.fit(cfa_data)
    
    try:
        cfa_loadings = model.inspect(std_est=True)
    except:
        cfa_loadings = model.inspect()

    cfa_fit = semopy.calc_stats(model).T
    
    print("\n--- Model Fit Indices ---")
    print(cfa_fit) 
    
    measurement_loadings = cfa_loadings[cfa_loadings['op'] == '=~']
    ave_cr_df = calculate_ave_cr(measurement_loadings)
    print("\n--- Convergent Validity ---")
    print(ave_cr_df)



except Exception as e:
    error_msg = str(e)
    print(f"\nError running model: {e}")

# ==========================================
# 5. Export Reports & Syntax
# ==========================================

# --- Variable Translation ---
variable_mapping = {
    "HP": "階層停滯 (HP)",
    "JCP": "工作內容停滯 (JCP)",
    "CI": "職涯無所作為 (CI)",
    "PP": "主動型人格 (PP)",
    "DP": "決策拖延 (DP)"
}

print("\nTranslating variables to Chinese...")

# 1. Descriptive Stats
stats_df['Variable'] = stats_df['Variable'].replace(variable_mapping)

# 2. Correlation Matrix
corr_df['Variable'] = corr_df['Variable'].replace(variable_mapping)
corr_df.rename(columns=variable_mapping, inplace=True)

# 3. CFA Loadings (Latent Factors only)
if not cfa_loadings.empty:
    cfa_loadings['lval'] = cfa_loadings['lval'].replace(variable_mapping)
    # Note: We don't translate 'rval' (items) to keep them clean (e.g. HP1)

# 4. AVE/CR
if not ave_cr_df.empty:
    ave_cr_df['Variable'] = ave_cr_df['Variable'].replace(variable_mapping)

# Export CSVs (even if empty)
cfa_loadings.to_csv(f"cfa_results_loadings_{timestamp}.csv")
cfa_fit.to_csv(f"cfa_results_fit_{timestamp}.csv")
ave_cr_df.to_csv(f"cfa_results_validity_{timestamp}.csv", index=False)

save_to_markdown(stats_df, corr_df, cfa_loadings, cfa_fit, ave_cr_df, error_msg, filename=f"Research_Result_{timestamp}.md")
generate_syntax_files(scale_items, timestamp)
