import pandas as pd
import os
import glob

# Search in the analysis directory
search_path = os.path.join(r"d:\HTML\Research\analysis", "*.xlsx")
files = glob.glob(search_path)

if not files:
    print("No Excel files found in analysis directory.")
else:
    # Use the first match (likely the one we want)
    file_path = files[0] # Improve logic if multiple exist, but likely this is the one
    for f in files:
        if "職涯" in f:
            file_path = f
            break
            
    print(f"Reading file: {file_path}")

    try:
        # Read only the header
        df = pd.read_excel(file_path, nrows=1)
        
        found = False
        print("Columns found:")
        for col in df.columns:
            if "家常便飯" in str(col):
                print(f"\n>> FOUND JCP6: {col}\n")
                found = True
        
        if not found:
            print("Not found '家常便飯'. Printing first 10 columns to check structure:")
            print(df.columns[:10].tolist())

    except Exception as e:
        print(f"Error: {e}")
