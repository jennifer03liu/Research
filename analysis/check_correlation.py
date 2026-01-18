import pandas as pd
import glob
import os
import scipy.stats as stats

def get_latest_data():
    search_pattern = 'T1_*_SPSS.csv'
    list_of_files = glob.glob(search_pattern)
    if list_of_files:
        latest_file = max(list_of_files, key=os.path.getmtime)
        return pd.read_csv(latest_file)
    return None

def main():
    df = get_latest_data()
    if df is None:
        print("No data found.")
        return

    # Calculate scales
    scale_cols = {
        "HP": ["HP1", "HP2", "HP3", "HP4_R", "HP5", "HP6_R"],
        "JCP": ["JCP1_R", "JCP2_R", "JCP3_R", "JCP4_R", "JCP5_R"] # Optimized: No JCP6
    }
    
    # Simple mean calculation (no fancy alpha check here)
    for name, items in scale_cols.items():
        # Ensure numeric
        cols = [c for c in items if c in df.columns]
        df[name] = df[cols].apply(pd.to_numeric, errors='coerce').mean(axis=1)

    # Check PM_Help correlation
    # Usually PM_Help is 1-5. 
    if 'PM_Help' in df.columns:
        print("\nCorrelation Analysis (Pearson):")
        for target in ['HP', 'JCP']:
            corr, p = stats.pearsonr(df['PM_Help'].dropna(), df[target].dropna())
            print(f"PM_Help (1-5) vs {target}: r = {corr:.3f}, p = {p:.3e}")
            
        # Check ANOVA for each level 1-5
        print("\nANOVA across PM_Help levels (1-5):")
        for target in ['HP', 'JCP']:
            groups = [df[df['PM_Help'] == i][target].dropna() for i in range(1, 6)]
            # Filter empty groups
            groups = [g for g in groups if len(g) > 0]
            if len(groups) > 1:
                f, p = stats.f_oneway(*groups)
                print(f"{target} by PM_Help levels: F = {f:.3f}, p = {p:.3e}")
            else:
                print(f"{target}: Not enough groups")
    else:
        print("PM_Help column not found.")

if __name__ == "__main__":
    main()
