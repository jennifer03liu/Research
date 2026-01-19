import pandas as pd
import os

file_path = r"d:\HTML\Research\職涯發展與工作狀況調查問卷 (T1) (回覆).xlsx"

try:
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
    else:
        # Read only the header
        df = pd.read_excel(file_path, nrows=1)
        
        found = False
        for col in df.columns:
            if "家常便飯" in str(col):
                print(f"FOUND JCP6: {col}")
                found = True
        
        if not found:
            print("Not found '家常便飯' in columns. Printing all columns containing '工作':")
            for col in df.columns:
                if "工作" in str(col):
                    print(col)

except Exception as e:
    print(f"Error: {e}")
