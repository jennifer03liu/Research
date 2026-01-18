import pandas as pd
import semopy
import numpy as np
import os
import glob
import sys

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

def run_all_models(data, scale_items):
    # Define Models
    models_config = {
        "M1": {
            "desc": "Original 5 Factors",
            "syntax": f"""
                HP =~ {get_items_str(scale_items, 'HP')}
                JCP =~ {get_items_str(scale_items, 'JCP')}
                PP =~ {get_items_str(scale_items, 'PP')}
                DP =~ {get_items_str(scale_items, 'DP')}
                CI =~ {get_items_str(scale_items, 'CI')}
            """
        },
        "M2": {
            "desc": "4 Factors: CP(HP+JCP)",
            "syntax": f"""
                CP =~ {get_items_str(scale_items, 'HP')} + {get_items_str(scale_items, 'JCP')}
                PP =~ {get_items_str(scale_items, 'PP')}
                DP =~ {get_items_str(scale_items, 'DP')}
                CI =~ {get_items_str(scale_items, 'CI')}
            """
        },
        "M3": {
            "desc": "4 Factors: No PP",
            "syntax": f"""
                HP =~ {get_items_str(scale_items, 'HP')}
                JCP =~ {get_items_str(scale_items, 'JCP')}
                DP =~ {get_items_str(scale_items, 'DP')}
                CI =~ {get_items_str(scale_items, 'CI')}
            """
        },
        "M4": {
            "desc": "3 Factors: CP, No PP",
            "syntax": f"""
                CP =~ {get_items_str(scale_items, 'HP')} + {get_items_str(scale_items, 'JCP')}
                DP =~ {get_items_str(scale_items, 'DP')}
                CI =~ {get_items_str(scale_items, 'CI')}
            """
        },
        "M5": {
            "desc": "4 Factors: No DP",
            "syntax": f"""
                HP =~ {get_items_str(scale_items, 'HP')}
                JCP =~ {get_items_str(scale_items, 'JCP')}
                PP =~ {get_items_str(scale_items, 'PP')}
                CI =~ {get_items_str(scale_items, 'CI')}
            """
        },
        "M6": {
            "desc": "3 Factors: CP, No DP",
            "syntax": f"""
                CP =~ {get_items_str(scale_items, 'HP')} + {get_items_str(scale_items, 'JCP')}
                PP =~ {get_items_str(scale_items, 'PP')}
                CI =~ {get_items_str(scale_items, 'CI')}
            """
        }
    }

    results = []
    
    # Prepare Data
    cols = [item for sublist in scale_items.values() for item in sublist]
    available_cols = [c for c in cols if c in data.columns]
    cfa_data = data[available_cols].dropna()
    
    best_loadings = None
    best_loadings_col = None

    print(f"\n{BLUE}Comparing all 6 models with current items...{RESET}")
    print(f"{'Model':<6} {'CFI':<10} {'RMSEA':<10} {'AIC':<10} {'Description'}")
    print("-" * 60)

    for m_name, config in models_config.items():
        try:
            model = semopy.Model(config['syntax'])
            model.fit(cfa_data)
            stats = semopy.calc_stats(model)
            
            cfi = stats.iloc[0]['CFI']
            rmsea = stats.iloc[0]['RMSEA']
            aic = stats.iloc[0]['AIC']
            
            # Color code good fit
            cfi_str = f"{CFI_COLOR(cfi)}{cfi:.3f}{RESET}"
            rmsea_str = f"{RMSEA_COLOR(rmsea)}{rmsea:.3f}{RESET}"
            
            print(f"{m_name:<6} {cfi_str:<20} {rmsea_str:<20} {aic:.1f}      {config['desc']}")
            
            # Store loadings for Model 1 (Base) to help optimization
            if m_name == "M1":
                loadings = model.inspect(std_est=True)
                loadings = loadings[loadings['op'] == '~'].copy()
                col_name = 'Est. Std' if 'Est. Std' in loadings.columns else 'Estimate'
                loadings[col_name] = pd.to_numeric(loadings[col_name], errors='coerce')
                best_loadings = loadings
                best_loadings_col = col_name
                
        except Exception as e:
            print(f"{m_name:<6} {RED}Failed{RESET}                               {config['desc']}")

    return best_loadings, best_loadings_col

def main():
    print(f"{CYAN}=== Interactive Model Optimization Tool (Multi-Model) ==={RESET}")
    print("This tool removes items from ALL models simultaneously.")
    print("Watch how CFI changes for M1-M6 as you remove bad items.")
    
    # 1. Load Data
    data = get_latest_data()
    if data is None: return

    # 2. Initial Scale Items
    scale_items = {
        "HP": ["HP1", "HP2", "HP3", "HP4_R", "HP5", "HP6_R"],
        "JCP": ["JCP1_R", "JCP2_R", "JCP3_R", "JCP4_R", "JCP5_R", "JCP6"],
        "PP":  ["PP1", "PP2", "PP3", "PP4", "PP5", "PP6"],
        "DP":  ["DP1", "DP2", "DP3", "DP4", "DP5"],
        "CI":  ["CI1", "CI2", "CI3", "CI4", "CI5", "CI6", "CI7", "CI8"]
    }
    
    removed_items = []
    
    while True:
        loadings1, col1 = run_all_models(data, scale_items)
        
        # Show Low Loadings (from Model 1 as reference)
        if loadings1 is not None:
            print(f"\n{YELLOW}>>> Low Loadings (Reference: Model 1) <<<{RESET}")
            print("(Removing an item removes it from ALL models)")
            low_loadings = loadings1[loadings1[col1] < 0.60].sort_values(by=col1)
            
            if not low_loadings.empty:
                print(f"{'Item':<10} {'Factor':<10} {'Loading':<10}")
                print("-" * 30)
                for _, row in low_loadings.iterrows():
                    val = row[col1]
                    color = RED if val < 0.4 else (YELLOW if val < 0.55 else RESET)
                    print(f"{color}{row['lval']:<10} {row['rval']:<10} {val:.3f}{RESET}")
            else:
                print(f"{GREEN}No items with loading < 0.60 in Model 1.{RESET}")
                
        # Prompt for Action
        print(f"\n{CYAN}Options:{RESET}")
        print("  - Enter item names to REMOVE (e.g., 'HP3, JCP6')")
        print("  - Enter 'done' to finish")
        print("  - Enter 'reset' to restart")
        
        user_input = input(f"\n{YELLOW}Selection >> {RESET}").strip()
        
        if user_input.lower() == 'done':
            break
        elif user_input.lower() == 'reset':
            print("Resetting is not fully implemented in loop, please restart script.")
            return
        elif user_input:
            items_to_remove = [x.strip() for x in user_input.replace(',', ' ').split() if x.strip()]
            
            for item in items_to_remove:
                found = False
                for scale in scale_items:
                    if item in scale_items[scale]:
                        scale_items[scale].remove(item)
                        removed_items.append(item)
                        print(f"Removed {RED}{item}{RESET} from {scale}")
                        found = True
                        break
                if not found:
                    print(f"Item '{item}' not found (already removed?).")
        
    # Final Output
    print(f"\n{GREEN}=== Optimization Finished ==={RESET}")
    print("Final Items Configuration:")
    print("scale_items = {")
    for scale, items in scale_items.items():
        items_str = ', '.join([f'"{i}"' for i in items])
        print(f'    "{scale}": [{items_str}],')
    print("}")

def CFI_COLOR(val):
    return GREEN if val > 0.9 else (YELLOW if val > 0.85 else RED)

def RMSEA_COLOR(val):
    return GREEN if val < 0.08 else (YELLOW if val < 0.1 else RED)

if __name__ == "__main__":
    try:
        pd.set_option('display.max_columns', None)
    except: pass
    main()
