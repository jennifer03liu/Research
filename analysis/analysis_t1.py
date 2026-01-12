import pandas as pd
import semopy
import numpy as np
import os

# ==========================================
# 1. Load Data
# ==========================================
# Please export your Google Sheet "T1_..._SPSS" to CSV and name it 'data_t1.csv'
FILENAME = 'T1_0105_377_SPSS.csv'

if os.path.exists(FILENAME):
    print(f"Loading data from {FILENAME}...")
    data = pd.read_csv(FILENAME)
else:
    print(f"Warning: {FILENAME} not found. Generating MOCK data for demonstration...")
    # Generate synthetic data
    np.random.seed(42)
    N = 377
    data = pd.DataFrame()
    
    # helper to generate correlated items
    def gen_factor(name, n_items, mean=3.5, std=1.0):
        # latent factor
        f = np.random.normal(0, 1, N)
        for i in range(1, n_items + 1):
            # item = loading*f + error
            item_val = 0.7 * f + np.random.normal(0, 0.5, N)
            # scale to likely range
            item_val = (item_val * std) + mean
            item_val = np.clip(item_val, 1, 6) # 1-6 scale
            col_name = f"{name}{i}"
            # Simulate _R suffix if needed by your schema, keeping simple here for demo
            if name == "HCP" and i in [4, 6]: col_name += "_R"
            if name == "JCP" and i <= 5: col_name += "_R"
            data[col_name] = item_val

    # Generate based on your structure
    gen_factor("HCP", 6)
    gen_factor("JCP", 6)
    gen_factor("PP", 6)
    gen_factor("DP", 5) # 1-5 scale presumably?
    gen_factor("CI", 8)

    # Print columns to verify
    print("Generated Mock Columns:", data.columns.tolist())

# ==========================================
# 2. Define Model (CFA)
# ==========================================
# Syntax similar to lavaan/Mplus
# LatentVariable =~ item1 + item2 ...

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

# ==========================================
# 3. Run Analysis
# ==========================================
print("\nRunning CFA Model...")
try:
    model = semopy.Model(model_desc)
    # Validate dataframe has all columns
    missing_cols = []
    # Extract variable names from description is tricky in pure python string parsing, 
    # but semopy assumes columns exist. 
    # Let's just run fit.
    
    model.fit(data)
    
    # ==========================================
    # 4. Reporting
    # ==========================================
    inspect = model.inspect()
    stats = semopy.calc_stats(model)
    
    print("\n--- Model Fit Indices ---")
    print(stats.T) # Transpose for readability
    
    print("\n--- Factor Loadings (Standardized estimate recommended manually) ---")
    print(inspect[inspect['op'] == '=~'])
    
    print("\n--- Factor Correlations (Covariances) ---")
    print(inspect[inspect['op'] == '~~'])

    # Save results
    inspect.to_csv("cfa_results_loadings.csv")
    stats.to_csv("cfa_results_fit.csv")
    print("\nResults saved to 'cfa_results_loadings.csv' and 'cfa_results_fit.csv'")

except Exception as e:
    print(f"\nError running model: {e}")
    print("Please check if column names in CSV match the model description exactly.")
