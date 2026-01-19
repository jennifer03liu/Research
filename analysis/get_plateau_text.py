import pandas as pd
import os
import glob

# Search in the analysis directory
search_path = os.path.join(r"d:\HTML\Research\analysis", "*.xlsx")
files = glob.glob(search_path)

if not files:
    print("No Excel files found.")
else:
    file_path = files[0] 
    for f in files:
        if "職涯" in f:
            file_path = f
            break
            
    print(f"Reading file: {file_path}")

    try:
        # Read only the header
        df = pd.read_excel(file_path, nrows=1)
        
        print("\n--- HP Items (likely Hierarchical Plateau) ---")
        hp_cols = [c for c in df.columns if "HP" in c or "階層" in c]
        for col in hp_cols:
            print(col)

        print("\n--- JCP Items (likely Method says 'Job Content Plateau') ---")
        jcp_cols = [c for c in df.columns if "JCP" in c or "工作內容" in c]
        for col in jcp_cols:
            print(col)

    except Exception as e:
        print(f"Error: {e}")
