import pandas as pd
import semopy
import numpy as np
import os
import glob
from scipy import stats # For t-tests and ANOVA
from datetime import datetime, timedelta

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

def analyze_performance_impact(data, scale_scores_df):
    output_md = ""
    # Merge scores with raw data for grouping
    analysis_df = pd.concat([data, scale_scores_df], axis=1)
    scales = list(scale_scores_df.columns)
    
    output_md += "## 📈 績效考核對職涯停滯之影響分析 (Performance Appraisal Impact)\n\n"
    
    # 1. Utility (Helpfulness)
    t1 = run_ttest(analysis_df, "PM_Help", [4, 5], [1, 2, 3], scales, "High Help", "Low Help")
    if not t1.empty:
        output_md += "### 1. 績效考核幫助程度 (Utility)\n"
        output_md += "- **高幫助組 (High)**: 填答 4 (有幫助), 5 (非常有幫助)\n"
        output_md += "- **低幫助組 (Low)**: 填答 1 (完全沒幫助) ~ 3 (普通)\n\n"
        output_md += t1.to_markdown(index=False) + "\n\n"
        output_md += "> **解讀**：若 Diff 為負且顯著(*)，代表「覺得有幫助的人」該變項分數顯著較低 (例如停滯感較低)。\n\n"

    # 2. Existence (Has PM)
    if 'PM_Has' in analysis_df.columns:
        t2 = run_ttest(analysis_df, "PM_Has", [1], [0], scales, "Yes", "No")
        if not t2.empty:
            output_md += "### 2. 是否有績效考核 (Existence)\n"
            output_md += "- **有 (Yes)**: PM_Has = 1\n"
            output_md += "- **無 (No)**: PM_Has = 0\n\n"
            output_md += t2.to_markdown(index=False) + "\n\n"

    # 3. Result Nature
    if 'PM_Result' in analysis_df.columns:
        anova = analyze_anova(analysis_df, "PM_Result", scales)
        if not anova.empty:
            output_md += "### 3. 績效考核結果性質 (Result Nature)\n"
            output_md += "比較不同考核結果 (例如: 1=負面/普通, 2=正面... 需確認問卷定義) 之差異。\n\n"
            output_md += anova.to_markdown(index=False) + "\n\n"

    # 4. Appraisal Forms
    form_cols = [c for c in analysis_df.columns if c.startswith('PM_Form_')]
    if form_cols:
        output_md += "### 4. 績效考核形式 (Appraisal Forms)\n"
        output_md += "比較「有採用某種形式(1)」 vs 「沒採用(0)」的差異。\n\n"
        for form in form_cols:
            form_name = form.replace('PM_Form_', '')
            t_form = run_ttest(analysis_df, form, [1], [0], scales, f"With {form_name}", f"No {form_name}")
            if not t_form.empty:
                output_md += f"#### 形式: {form_name}\n"
                output_md += t_form.to_markdown(index=False) + "\n\n"

    return output_md

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

def save_to_markdown(stats_df, corr_df, cfa_loadings, cfa_fit, ave_cr_df, comparison_df=None, error_msg=None, filename="Research_Result.md", suggestions_df=None, performance_md=""):
    print(f"\nGenerating Markdown Report: {filename}...")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# 研究分析結果報告 (Research Analysis Report)\n\n")
        
        f.write("## 表 1. 敘述性統計與信度分析 (Descriptive Statistics & Reliability)\n")
        f.write(stats_df.to_markdown(index=False))
        f.write("\n\n")
        
        f.write("## 表 2. 相關係數矩陣 (Correlation Matrix)\n")
        f.write(corr_df.to_markdown(index=False))
        f.write("\n\n")
        
        if error_msg:
            f.write("## ⚠️ 分析錯誤 (Analysis Error)\n")
            f.write(f"**CFA 模型無法執行:** {error_msg}\n")
            f.write("後續表格 (表3, 4, 5) 空白，因為模型無法估計。\n")
            f.write("可能原因: 數據缺失 (NaN)、奇異矩陣 (Singular matrix) 或變數名稱不匹配。\n\n")
        
        f.write("## 表 3. 模型適配度指標 (Model Fit Indices)\n")
        if not cfa_fit.empty:
            # Write all columns to avoid missing data due to name mismatches
            f.write(cfa_fit.to_markdown(index=False))
        else:
            f.write("(無資料 No Data)\n")
        f.write("\n\n")
        
        f.write("## 表 4. 因素負荷量 (Factor Loadings - Standardized)\n")
        if not cfa_loadings.empty:
            # FIX: semopy output uses '~' for loadings (Item ~ Factor)
            loadings = cfa_loadings[cfa_loadings['op'] == '~'].copy()
            
            # Select appropriate columns for display
            display_cols = ['lval', 'rval', 'Estimate', 'p-value', 'Std. Err', 'Model']
            if 'Est. Std' in loadings.columns:
                display_cols = ['lval', 'rval', 'Est. Std', 'p-value', 'Std. Err', 'Model']
            
            # Filter existing columns only
            display_cols = [c for c in display_cols if c in loadings.columns]
            
            loadings = loadings[display_cols]
            
            # Round numeric columns
            for col in ['Estimate', 'Est. Std', 'p-value', 'Std. Err']:
                if col in loadings.columns:
                     loadings[col] = pd.to_numeric(loadings[col], errors='coerce').apply(lambda x: round(x, 3) if pd.notnull(x) else "")

            f.write(loadings.to_markdown(index=False))
        else:
            f.write("(無資料 No Data)\n")
        f.write("\n\n")

        f.write("## 表 5. 收斂效度 (Convergent Validity - CR & AVE)\n")
        if not ave_cr_df.empty:
            f.write(ave_cr_df.to_markdown(index=False))
        else:
            f.write("(無資料 No Data)\n")
        f.write("\n\n")

        if comparison_df is not None and not comparison_df.empty:
            f.write("## 表 6. 多模型比較摘要 (Model Comparison Summary)\n")
            f.write("比較不同假設模型的適配度指標。\n")
            f.write(comparison_df.to_markdown(index=False))
            f.write("\n\n")
            
            f.write(suggestions_df.to_markdown(index=False))
            f.write("\n\n")

        if performance_md:
            f.write(performance_md)
            f.write("\n\n")

        
    print(f"Report saved to {filename}")

def suggest_optimizations(loadings_df, timestamp, output_dir):
    print("\nAnalyzing for Model Optimization...")
    if loadings_df.empty: return pd.DataFrame()

    # Filter for Factor Loadings (op='~')
    col_name = 'Est. Std' if 'Est. Std' in loadings_df.columns else 'Estimate'
    
    # Filter Loadings
    subset = loadings_df[loadings_df['op'] == '~'].copy()
    subset[col_name] = pd.to_numeric(subset[col_name], errors='coerce')
    
    # Identify Low Loadings (< 0.6)
    low_loadings = subset[subset[col_name] < 0.6].copy()
    
    if not low_loadings.empty:
        print(f"  Found {len(low_loadings)} items with low loadings (< 0.6).")
        
        # Select relevant columns
        cols = ['Model', 'lval', 'rval', col_name, 'p-value']
        cols = [c for c in cols if c in low_loadings.columns]
        
        suggestions = low_loadings[cols].sort_values(by=[col_name])
        
        # Save to CSV
        csv_path = os.path.join(output_dir, f"optimization_suggestions_{timestamp}.csv")
        suggestions.to_csv(csv_path, index=False)
        print(f"  Suggestions saved to {csv_path}")
        
        return suggestions
    else:
        print("  No items with loadings < 0.6 found.")
        return pd.DataFrame()

def generate_syntax_files(scale_items, timestamp, output_dir):
    print("\nGenerating Syntax Files...")
    
    # 1. SPSS Syntax (.sps)
    spss_file = os.path.join(output_dir, f"Syntax_SPSS_{timestamp}.sps")
    with open(spss_file, "w", encoding='utf-8') as f:
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
    mplus_file = os.path.join(output_dir, f"Syntax_Mplus_{timestamp}.inp")
    with open(mplus_file, "w", encoding='utf-8') as f:
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
    r_file = os.path.join(output_dir, f"Syntax_R_{timestamp}.R")
    with open(r_file, "w", encoding='utf-8') as f:
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

def run_full_analysis(data, scale_items, output_folder_suffix=None):
    # ==========================================
    # 1. Setup & Timestamp
    # ==========================================
    # Use UTC+8 for Taiwan time
    timestamp = (datetime.utcnow() + timedelta(hours=8)).strftime("%y%m%d%H%M")
    
    if output_folder_suffix:
        output_dir = f"{timestamp}_Results_{output_folder_suffix}"
    else:
        output_dir = f"{timestamp}_Results"
        
    os.makedirs(output_dir, exist_ok=True)
    print(f"Run Timestamp: {timestamp}")
    print(f"Output Directory: {output_dir}")
    
    # Check observations
    cols_flat = [item for sublist in scale_items.values() for item in sublist]
    available_cols_flat = [c for c in cols_flat if c in data.columns]
    if len(available_cols_flat) < len(cols_flat):
        missing = set(cols_flat) - set(available_cols_flat)
        print(f"Warning: Missing columns in CSV: {missing}")

    # ==========================================
    # 2. Reliability & Descriptive Statistics
    # ==========================================
    print("\n--- Reliability & Descriptive Statistics ---")
    stats_list = []
    scale_scores = pd.DataFrame()
    
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
    stats_file = os.path.join(output_dir, f"descriptive_reliability_{timestamp}.csv")
    stats_df.to_csv(stats_file, index=False)
    
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
                    r_val, p_val = stats.pearsonr(scale_scores[r], scale_scores[c])
                    star = get_significance_stars(p_val)
                    row_data[c] = f"{r_val:.2f}{star}"
            corr_data.append(row_data)

    corr_df = pd.DataFrame(corr_data)
    corr_file = os.path.join(output_dir, f"correlation_matrix_{timestamp}.csv")
    corr_df.to_csv(corr_file, index=False)
    
    # ==========================================
    # 4. CFA & Validity (Multi-Model Comparison)
    # ==========================================
    print("\n--- Running Multi-Model CFA Comparison ---")

    # Define Item Groups helper
    def get_items_str(key):
        return " + ".join(scale_items[key])

    # 1. Define Models (Dynamic based on passed scale_items)
    models_config = {
        "Model_1_5Factors": {
            "desc": "原始五因子模型 (HP, JCP, PP, DP, CI)",
            "syntax": f"""
                HP =~ {get_items_str('HP')}
                JCP =~ {get_items_str('JCP')}
                PP =~ {get_items_str('PP')}
                DP =~ {get_items_str('DP')}
                CI =~ {get_items_str('CI')}
            """
        },
        "Model_2_4Factors_CP": {
            "desc": "四因子: 合併階層與工作內容停滯 (CP=HP+JCP)",
            "syntax": f"""
                CP =~ {get_items_str('HP')} + {get_items_str('JCP')}
                PP =~ {get_items_str('PP')}
                DP =~ {get_items_str('DP')}
                CI =~ {get_items_str('CI')}
            """
        },
        "Model_3_4Factors_NoPP": {
            "desc": "四因子: 排除主動型人格 (No PP)",
            "syntax": f"""
                HP =~ {get_items_str('HP')}
                JCP =~ {get_items_str('JCP')}
                DP =~ {get_items_str('DP')}
                CI =~ {get_items_str('CI')}
            """
        },
        "Model_4_3Factors_CP_NoPP": {
            "desc": "三因子: 合併CP且排除PP (CP, DP, CI)",
            "syntax": f"""
                CP =~ {get_items_str('HP')} + {get_items_str('JCP')}
                DP =~ {get_items_str('DP')}
                CI =~ {get_items_str('CI')}
            """
        },
        "Model_5_4Factors_NoDP": {
            "desc": "四因子: 排除決策拖延 (No DP)",
            "syntax": f"""
                HP =~ {get_items_str('HP')}
                JCP =~ {get_items_str('JCP')}
                PP =~ {get_items_str('PP')}
                CI =~ {get_items_str('CI')}
            """
        },
        "Model_6_3Factors_CP_NoDP": {
            "desc": "三因子: 合併CP且排除DP (CP, PP, CI)",
            "syntax": f"""
                CP =~ {get_items_str('HP')} + {get_items_str('JCP')}
                PP =~ {get_items_str('PP')}
                CI =~ {get_items_str('CI')}
            """
        }
    }

    model_fit_results = []
    # all_loadings = {} # Not used, removed
    cfa_loadings = pd.DataFrame()
    ave_cr_df = pd.DataFrame()
    cfa_fit = pd.DataFrame()
    comparison_df = pd.DataFrame()
    error_msg = None

    try:
        # Prepare Data
        cfa_data = data[available_cols_flat].dropna()
        print(f"Observations for CFA: {len(cfa_data)}")
        
        if len(cfa_data) < 10:
            raise ValueError("Too few observations.")

        for m_name, config in models_config.items():
            print(f"Running {m_name}...")
            try:
                model = semopy.Model(config['syntax'])
                model.fit(cfa_data)
                
                # Get Fit Indices
                fit_stats = semopy.calc_stats(model)
                fit_stats['Model'] = m_name
                fit_stats['Description'] = config['desc']
                model_fit_results.append(fit_stats)
                
                # Store Loadings
                try:
                    loadings = model.inspect(std_est=True)
                except:
                    loadings = model.inspect()
                
                loadings['Model'] = m_name
                # all_loadings[m_name] = loadings # Not used, removed
                
                cfa_loadings = pd.concat([cfa_loadings, loadings], ignore_index=True)
                    
            except Exception as e:
                print(f"  Failed {m_name}: {e}")
                model_fit_results.append(pd.DataFrame({'Model': [m_name], 'Description': [config['desc']], 'Error': [str(e)]}))

    # Compile Comparison Table
        if model_fit_results:
            comparison_df = pd.concat(model_fit_results, ignore_index=True)
            # Use the FULL comparison dataframe as cfa_fit (for Table 3 - Full Stats)
            cfa_fit = comparison_df.copy()
            
            cols_order = ['Model', 'Description', 'Chi2', 'DoF', 'p-value', 'CFI', 'TLI', 'RMSEA', 'AIC', 'BIC', 'Error']
            # Filter cols that exist
            cols_order = [c for c in cols_order if c in comparison_df.columns]
            comparison_df = comparison_df[cols_order]
            
            print("\n--- Model Comparison Summary ---")
            print(comparison_df.to_markdown(index=False))
            
            # Calculate validity for the MAIN model (Model 1)
            if not cfa_loadings.empty:
                # FIX: semopy uses '~' for factor loadings
                measurement_loadings = cfa_loadings[cfa_loadings['op'] == '~']
                ave_cr_df = calculate_ave_cr(measurement_loadings)

    except Exception as e:
        error_msg = str(e)
        print(f"\nCritical Error in CFA loop: {e}")

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
    cfa_loadings.to_csv(os.path.join(output_dir, f"cfa_results_loadings_{timestamp}.csv"))
    cfa_fit.to_csv(os.path.join(output_dir, f"cfa_results_fit_{timestamp}.csv"))
    ave_cr_df.to_csv(os.path.join(output_dir, f"cfa_results_validity_{timestamp}.csv"), index=False)

    # Run Optimization Analysis
    suggestions_df = suggest_optimizations(cfa_loadings, timestamp, output_dir)

    # Run Performance Impact Analysis
    performance_md = analyze_performance_impact(data, scale_scores)

    md_file = os.path.join(output_dir, f"Research_Result_{timestamp}.md")
    save_to_markdown(stats_df, corr_df, cfa_loadings, cfa_fit, ave_cr_df, comparison_df, error_msg, filename=md_file, suggestions_df=suggestions_df, performance_md=performance_md)
    comparison_df.to_csv(os.path.join(output_dir, f"model_comparison_{timestamp}.csv"), index=False)
    generate_syntax_files(scale_items, timestamp, output_dir)
    
    return comparison_df, suggestions_df

if __name__ == "__main__":
    # ==========================================
    # 1. Load Data (Default Behavior)
    # ==========================================
    search_pattern = 'T1_*_SPSS.csv'
    list_of_files = glob.glob(search_pattern)
    
    if list_of_files:
        latest_file = max(list_of_files, key=os.path.getmtime)
        print(f"Using default data: {latest_file}")
        data = pd.read_csv(latest_file)
        
        # Default Scale Items
        scale_items = {
            "HP": ["HP1", "HP2", "HP3", "HP4_R", "HP5", "HP6_R"],
            "JCP": ["JCP1_R", "JCP2_R", "JCP3_R", "JCP4_R", "JCP5_R"], # JCP6 default removed? Or keep? Let's keep JCP6 removed as per latest state
            "PP":  ["PP1", "PP2", "PP3", "PP4", "PP5", "PP6"],
            "DP":  ["DP1", "DP2", "DP3", "DP4", "DP5"],
            "CI":  ["CI1", "CI2", "CI3", "CI4", "CI5", "CI6", "CI7", "CI8"]
        }
        
        run_full_analysis(data, scale_items)
    else:
        print("No data found.")
