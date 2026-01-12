import pandas as pd
import semopy
import numpy as np
import os
from scipy.stats import pearsonr

# ==========================================
# 0. Helper Functions
# ==========================================

def calculate_cronbach_alpha(df):
    """
    Calculates Cronbach's Alpha for a given DataFrame of items.
    """
    df_corr = df.corr()
    N = df.shape[1]
    
    # Calculate the mean of the correlations
    # We sum the lower triangle (or upper) and divide by n*(n-1)/2
    rs = np.array([])
    for i, col1 in enumerate(df_corr.columns):
        for j, col2 in enumerate(df_corr.columns):
            if i > j:
                rs = np.append(rs, df_corr.iloc[i, j])
    
    mean_r = np.mean(rs)
    
    # Standardized Cronbach's Alpha formula
    alpha = (N * mean_r) / (1 + (N - 1) * mean_r)
    return alpha

def get_significance_stars(p_value):
    if p_value < 0.001:
        return '***'
    elif p_value < 0.01:
        return '**'
    elif p_value < 0.05:
        return '*'
    else:
        return ''

# ==========================================
# 1. Load Data
# ==========================================
# Please export your Google Sheet "T1_..._SPSS" to CSV and name it 'data_t1.csv'
FILENAME = 'T1_0105_377_SPSS.csv'

# Define Scale Items (Based on your DataCleaning.js structure)
scale_items = {
    "HCP": ["HCP1", "HCP2", "HCP3", "HCP4_R", "HCP5", "HCP6_R"],
    "JCP": ["JCP1_R", "JCP2_R", "JCP3_R", "JCP4_R", "JCP5_R", "JCP6"],
    "PP":  ["PP1", "PP2", "PP3", "PP4", "PP5", "PP6"],
    "DP":  ["DP1", "DP2", "DP3", "DP4", "DP5"],
    "CI":  ["CI1", "CI2", "CI3", "CI4", "CI5", "CI6", "CI7", "CI8"]
}

if os.path.exists(FILENAME):
    print(f"Loading data from {FILENAME}...")
    data = pd.read_csv(FILENAME)
else:
    print(f"Warning: {FILENAME} not found. Generating MOCK data for demonstration...")
    # Generate synthetic data
    np.random.seed(42)
    N = 377
    data = pd.DataFrame()
    
    def gen_factor(name, items_list, mean=3.5, std=1.0):
        f = np.random.normal(0, 1, N)
        for i, col_name in enumerate(items_list):
            # item = loading*f + error
            item_val = 0.7 * f + np.random.normal(0, 0.5, N)
            
            # reverse logic simulation for demo (if filename implies reversed)
            # In real data, DataCleaning.js already reversed them, so they correlate positively with construct.
            
            item_val = (item_val * std) + mean
            item_val = np.clip(item_val, 1, 6) # 1-6 scale
            data[col_name] = item_val

    for scale, items in scale_items.items():
        gen_factor(scale, items)

    # Print columns to verify
    print("Generated Mock Columns:", data.columns.tolist())

# ==========================================
# 2. Reliability & Descriptive Statistics
# ==========================================
print("\n--- Reliability & Descriptive Statistics ---")
stats_list = []
scale_scores = pd.DataFrame()

for scale, items in scale_items.items():
    # Subset data
    missing_cols = [c for c in items if c not in data.columns]
    if missing_cols:
        print(f"Skipping {scale}: Missing columns {missing_cols}")
        continue
        
    df_subset = data[items]
    
    # Reliability
    alpha = calculate_cronbach_alpha(df_subset)
    
    # Mean & SD
    # Assuming items are already recoded in DataCleaning.js so high score = high trait
    scale_score = df_subset.mean(axis=1)
    scale_scores[scale] = scale_score
    
    mean = scale_score.mean()
    sd = scale_score.std()
    
    stats_list.append({
        "Variable": scale,
        "Items": len(items),
        "Mean": round(mean, 2),
        "SD": round(sd, 2),
        "Alpha": round(alpha, 2)
    })

stats_df = pd.DataFrame(stats_list)
print(stats_df)
stats_df.to_csv("descriptive_reliability.csv", index=False)
print("Saved to 'descriptive_reliability.csv'")

# ==========================================
# 3. Correlation Matrix with Stars
# ==========================================
print("\n--- Correlation Matrix ---")

# Calculate Pearson correlations and p-values
cols = stats_df['Variable'].tolist()
corr_data = []

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
print(corr_df)
corr_df.to_csv("correlation_matrix.csv", index=False)
print("Saved to 'correlation_matrix.csv'")


# ==========================================
# 4. Run Analysis (CFA)
# ==========================================
model_desc = """
    # 1. Hierarchical Career Plateau
    HCP =~ HCP1 + HCP2 + HCP3 + HCP4_R + HCP5 + HCP6_R

    # 2. Job Content Plateau
    JCP =~ JCP1_R + JCP2_R + JCP3_R + JCP4_R + JCP5_R

    # 3. Proactive Personality
    PP =~ PP1 + PP2 + PP3 + PP4 + PP5 + PP6

    # 4. Decisional Procrastination
    DP =~ DP1 + DP2 + DP3 + DP4 + DP5

    # 5. Career Inaction
    CI =~ CI1 + CI2 + CI3 + CI4 + CI5 + CI6 + CI7 + CI8
"""

print("\nRunning CFA Model...")
try:
    model = semopy.Model(model_desc)
    model.fit(data)
    
    # Reporting
    inspect = model.inspect()
    stats = semopy.calc_stats(model)
    
    print("\n--- Model Fit Indices ---")
    print(stats.T) 
    
    # Save results
    inspect.to_csv("cfa_results_loadings.csv")
    stats.to_csv("cfa_results_fit.csv")
    print("\nResults saved to 'cfa_results_loadings.csv' and 'cfa_results_fit.csv'")

except Exception as e:
    print(f"\nError running model: {e}")
