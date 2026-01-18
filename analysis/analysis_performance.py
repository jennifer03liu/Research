import pandas as pd
import numpy as np
import os
import glob
from scipy import stats

# Configuration
OUTPUT_FILE = "Performance_Analysis_Impact.md"

def get_latest_data():
    search_pattern = 'T1_*_SPSS.csv'
    list_of_files = glob.glob(search_pattern)
    if list_of_files:
        latest_file = max(list_of_files, key=os.path.getmtime)
        return pd.read_csv(latest_file)
    return None

def calculate_scale_scores(df):
    # Reuse item definitions (excluding JCP6 as per optimization)
    scale_items = {
        "HP": ["HP1", "HP2", "HP3", "HP4_R", "HP5", "HP6_R"],
        "JCP": ["JCP1_R", "JCP2_R", "JCP3_R", "JCP4_R", "JCP5_R"], # No JCP6
        "PP":  ["PP1", "PP2", "PP3", "PP4", "PP5", "PP6"],
        "DP":  ["DP1", "DP2", "DP3", "DP4", "DP5"],
        "CI":  ["CI1", "CI2", "CI3", "CI4", "CI5", "CI6", "CI7", "CI8"]
    }
    
    scores = pd.DataFrame()
    for scale, items in scale_items.items():
        valid_items = [i for i in items if i in df.columns]
        if valid_items:
            scores[scale] = df[valid_items].mean(axis=1)
            
    return scores

def run_ttest(df, group_col, group1_val, group2_val, scales, label1, label2):
    results = []
    
    g1 = df[df[group_col].isin(group1_val)]
    g2 = df[df[group_col].isin(group2_val)]
    
    for scale in scales:
        if scale not in df.columns: continue
        
        m1 = g1[scale].mean()
        m2 = g2[scale].mean()
        t_stat, p_val = stats.ttest_ind(g1[scale].dropna(), g2[scale].dropna(), equal_var=False)
        
        star = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
        
        results.append({
            "Variable": scale,
            f"{label1} (N={len(g1)})": round(m1, 2),
            f"{label2} (N={len(g2)})": round(m2, 2),
            "Diff": round(m1 - m2, 2),
            "p-value": f"{p_val:.3f} {star}"
        })
        
    return pd.DataFrame(results)

def analyze_anova(df, group_col, scales):
    results = []
    groups = df[group_col].dropna().unique()
    groups.sort()
    
    for scale in scales:
        if scale not in df.columns: continue
        
        group_data = [df[df[group_col] == g][scale].dropna() for g in groups]
        if len(group_data) < 2: continue
        
        f_stat, p_val = stats.f_oneway(*group_data)
        star = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
        
        row = {"Variable": scale, "F-value": round(f_stat, 2), "p-value": f"{p_val:.3f} {star}"}
        
        # Add means for each group
        for i, g in enumerate(groups):
            row[f"Group {int(g)} Mean"] = round(group_data[i].mean(), 2)
            
        results.append(row)
        
    return pd.DataFrame(results)

def main():
    print("Loading data...")
    raw_df = get_latest_data()
    if raw_df is None:
        print("No data found.")
        return

    # Calculate Scale Scores (HP, JCP, CI...)
    scores = calculate_scale_scores(raw_df)
    analysis_df = pd.concat([raw_df, scores], axis=1)
    
    scales = ["HP", "JCP", "PP", "DP", "CI"]
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# 績效考核對職涯停滯之影響分析 (Performance Appraisal Impact)\n\n")
        
        # Analysis 1: PM_Help (Utility)
        # High (4,5) vs Low (1,2,3)
        f.write("## 1. 績效考核幫助程度 (Utility)\n")
        f.write("- **高幫助組 (High)**: 填答 4 (有幫助), 5 (非常有幫助)\n")
        f.write("- **低幫助組 (Low)**: 填答 1 (完全沒幫助) ~ 3 (普通)\n\n")
        
        t1 = run_ttest(analysis_df, "PM_Help", [4, 5], [1, 2, 3], scales, "High Help", "Low Help")
        f.write(t1.to_markdown(index=False))
        f.write("\n\n> **解讀**：若 Diff 為負且顯著(*)，代表「覺得有幫助的人」該變項分數顯著較低 (例如停滯感較低)。\n\n")
        
        # Analysis 2: PM_Has (Existence)
        # Yes (1) vs No (0)
        if 'PM_Has' in analysis_df.columns:
            f.write("## 2. 是否有績效考核 (Existence)\n")
            f.write("- **有 (Yes)**: PM_Has = 1\n")
            f.write("- **無 (No)**: PM_Has = 0\n\n")
            
            t2 = run_ttest(analysis_df, "PM_Has", [1], [0], scales, "Yes", "No")
            f.write(t2.to_markdown(index=False))
            f.write("\n\n")
            
        # Analysis 3: PM_Result (Outcome Nature)
        # ANOVA for groups 1, 2, 3
        if 'PM_Result' in analysis_df.columns:
            f.write("## 3. 績效考核結果性質 (Result Nature)\n")
            f.write("比較不同考核結果 (例如: 1=負面/普通, 2=正面... 需確認問卷定義) 之差異。\n\n")
            
            anova = analyze_anova(analysis_df, "PM_Result", scales)
            f.write(anova.to_markdown(index=False))
            f.write("\n\n")

        # Analysis 4: PM_Form Types
        # Compare "Used" (1) vs "Not Used" (0) for each form
        form_cols = [c for c in analysis_df.columns if c.startswith('PM_Form_')]
        if form_cols:
            f.write("## 4. 績效考核形式 (Appraisal Forms)\n")
            f.write("比較「有採用某種形式(1)」 vs 「沒採用(0)」的差異。\n\n")
            
            for form in form_cols:
                form_name = form.replace('PM_Form_', '')
                t_form = run_ttest(analysis_df, form, [1], [0], scales, f"With {form_name}", f"No {form_name}")
                if not t_form.empty:
                    f.write(f"### 形式: {form_name}\n")
                    f.write(t_form.to_markdown(index=False))
                    f.write("\n\n")

    print(f"Analysis complete. Report saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
