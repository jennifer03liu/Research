import pandas as pd
import os
import glob

# Search in the analysis directory
search_path = os.path.join(r"d:\HTML\Research\analysis", "*.xlsx")
files = glob.glob(search_path)

if not files:
    print("No Excel files found.")
else:
    file_path = files[0] # Use first match
    for f in files:
        if "職涯" in f:
            file_path = f
            break
            
    print(f"Reading file: {file_path}")

    try:
        # Read only the header
        df = pd.read_excel(file_path, nrows=1)
        
        print("\n--- CI (Career Inaction) Items ---")
        ci_cols = [c for c in df.columns if "職涯" in c or "CI" in c or "Inaction" in c]
        
        # If no explicit "CI" in header, look for the text
        if not ci_cols:
            print("No CI columns found by name. Printing all columns to spot check:")
            # Print columns 50-70 where CI usually resides (guessing)
            print(df.columns.tolist())
        else:
            for col in ci_cols:
                print(col)

    except Exception as e:
        print(f"Error: {e}")
