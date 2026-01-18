import pandas as pd
import semopy
import os
import glob
import sys
from analysis_t1 import run_full_analysis

# Color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
CYAN = '\033[96m'
BLUE = '\033[94m'

def get_latest_data():
    search_pattern = 'T1_*_SPSS.csv'
    list_of_files = glob.glob(search_pattern)
    if list_of_files:
        latest_file = max(list_of_files, key=os.path.getmtime)
        print(f"Using data file: {GREEN}{latest_file}{RESET}")
        return pd.read_csv(latest_file)
    else:
        print(f"{RED}Error: No data file found matching '{search_pattern}'{RESET}")
        return None

def get_items_str(scale_items, key):
    return " + ".join(scale_items[key])

def run_quick_cfa(data, scale_items):
    """
    Runs a quick M1 CFA to get fit indices for optimization loop.
    Returns: CFI, RMSEA, AIC, Loadings DataFrame
    """
    model_syntax = f"""
        HP =~ {get_items_str(scale_items, 'HP')}
        JCP =~ {get_items_str(scale_items, 'JCP')}
        PP =~ {get_items_str(scale_items, 'PP')}
        DP =~ {get_items_str(scale_items, 'DP')}
        CI =~ {get_items_str(scale_items, 'CI')}
    """
    
    cols = [item for sublist in scale_items.values() for item in sublist]
    cfa_data = data[cols].dropna()
    
    try:
        model = semopy.Model(model_syntax)
        model.fit(cfa_data)
        stats = semopy.calc_stats(model)
        
        loadings = model.inspect(std_est=True)
        loadings = loadings[loadings['op'] == '~'].copy()
        col_name = 'Est. Std' if 'Est. Std' in loadings.columns else 'Estimate'
        loadings[col_name] = pd.to_numeric(loadings[col_name], errors='coerce')
        
        return stats.iloc[0], loadings, col_name
        
    except Exception as e:
        print(f"{RED}CFA Failed: {e}{RESET}")
        return None, None, None

def print_fit(stage_name, stats):
    if stats is None: return
    cfi = stats['CFI']
    rmsea = stats['RMSEA']
    aic = stats['AIC']
    
    cfi_str = f"{GREEN if cfi > 0.9 else YELLOW if cfi > 0.85 else RED}{cfi:.3f}{RESET}"
    rmsea_str = f"{GREEN if rmsea < 0.08 else YELLOW if rmsea < 0.1 else RED}{rmsea:.3f}{RESET}"
    
    print(f"\n{BLUE}--- {stage_name} Fit ---{RESET}")
    print(f"CFI   : {cfi_str}")
    print(f"RMSEA : {rmsea_str}")
    print(f"AIC   : {aic:.1f}")

def main():
    print(f"{CYAN}======================================================={RESET}")
    print(f"{CYAN}   Interactive Research Analysis Master (Optimization) {RESET}")
    print(f"{CYAN}======================================================={RESET}")
    
    # 1. Load Data
    data = get_latest_data()
    if data is None: return

    # 2. Initial Configuration
    scale_items = {
        "HP": ["HP1", "HP2", "HP3", "HP4_R", "HP5", "HP6_R"],
        "JCP": ["JCP1_R", "JCP2_R", "JCP3_R", "JCP4_R", "JCP5_R", "JCP6"],
        "PP":  ["PP1", "PP2", "PP3", "PP4", "PP5", "PP6"],
        "DP":  ["DP1", "DP2", "DP3", "DP4", "DP5"],
        "CI":  ["CI1", "CI2", "CI3", "CI4", "CI5", "CI6", "CI7", "CI8"]
    }
    
    original_stats = None
    optimized_stats = None
    removed_history = []

    # 3. Stage 1: Initial Check
    print(f"\n{YELLOW}Step 1: Running Initial Model (M1)...{RESET}")
    stats, loadings, load_col = run_quick_cfa(data, scale_items)
    original_stats = stats
    print_fit("Original M1", stats)
    
    if loadings is not None:
        print(f"\n{YELLOW}>>> Low Loadings (< 0.60) <<<{RESET}")
        low = loadings[loadings[load_col] < 0.60].sort_values(by=load_col)
        if not low.empty:
            for _, row in low.iterrows():
                val = row[load_col]
                color = RED if val < 0.4 else YELLOW
                print(f"{color}{row['lval']:<5} - {row['rval']:<10} : {val:.3f}{RESET}")
        else:
            print(f"{GREEN}No low loadings found!{RESET}")

    # 4. Optimization Loop
    while True:
        print(f"\n{CYAN}Action Required:{RESET}")
        print(" [Item Name] : Remove item (e.g. 'JCP6' or 'HP3, JCP6')")
        print(" [done]      : Finish optimization and generate FULL report")
        print(" [reset]     : Reset to original items")
        
        user_input = input(f"\n{YELLOW}>> {RESET}").strip()
        
        if user_input.lower() == 'done':
            break
        elif user_input.lower() == 'reset':
            # Reset logic would go here, simpler to just restart script for now
            print("Please restart script to reset completely.")
            continue
        elif user_input:
            items_to_remove = [x.strip() for x in user_input.replace(',', ' ').split() if x.strip()]
            valid_removal = False
            
            for item in items_to_remove:
                found = False
                for scale in scale_items:
                    if item in scale_items[scale]:
                        scale_items[scale].remove(item)
                        removed_history.append(item)
                        print(f"Removed {RED}{item}{RESET} from {scale}")
                        found = True
                        valid_removal = True
                        break
                if not found:
                    print(f"Item '{item}' not found.")
            
            if valid_removal:
                # Re-run quick check
                stats, loadings, load_col = run_quick_cfa(data, scale_items)
                print_fit("Current M1", stats)
                optimized_stats = stats

    # 5. Final Report Generation
    print(f"\n{GREEN}Step 2: Generating Final Report...{RESET}")
    
    suffix = "Optimized"
    if removed_history:
        suffix = "No_" + "_".join(removed_history)
        print(f"Analysis will be saved to folder suffix: {suffix}")
    
    # Run the full pipeline from analysis_t1.py
    run_full_analysis(data, scale_items, output_folder_suffix=suffix)
    
    print(f"\n{GREEN}All Done!{RESET}")
    if original_stats is not None and optimized_stats is not None:
        print(f"\n{BLUE}--- Optimization Summary ---{RESET}")
        print(f"Original CFI : {original_stats['CFI']:.3f}")
        print(f"Final CFI    : {optimized_stats['CFI']:.3f}")
        print(f"Improvement  : {optimized_stats['CFI'] - original_stats['CFI']:.3f}")

if __name__ == "__main__":
    main()
