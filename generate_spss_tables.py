import pandas as pd
import os
import openpyxl
from openpyxl.styles import Border, Side, Alignment, Font, PatternFill

OUTPUT_DIR = r"g:\其他電腦\我的 PC\NSYSU_HRM\Thesis_LM\05_會議報告與關聯圖\報告簡報"
excel_path = os.path.join(OUTPUT_DIR, "Canva_Tables_SPSS_Style_v2.xlsx")

# Table 1: Attrition
df_attrition = pd.DataFrame([
    ["整體職涯停滯 (CP)", "p = .355", "無顯著差異"],
    ["階層停滯 (HP)", "p = .215", "無顯著差異"],
    ["工作停滯 (JCP)", "p = .491", "無顯著差異"],
    ["決策拖延 (DP)", "p = .117", "無顯著差異"],
    ["職涯無所作為 (CI)", "p = .630", "無顯著差異"],
    ["主動型人格 (PP)", "p = .571", "無顯著差異"]
], columns=["研究變數", "Levene / t 檢定 (p value)", "檢驗結果判斷"])

# Table 2: Correlation Matrix
df_corr = pd.DataFrame([
    ["1. 整體停滯 (CP)", "(.80)", "", "", "", "", "", ""],
    ["2. 階層停滯 (HP)", ".84***", "(.86)", "", "", "", "", ""],
    ["3. 工作停滯 (JCP)", ".69***", ".18*", "(.77)", "", "", "", ""],
    ["4. 決策拖延", ".15*", ".16*", ".07", "(.81)", "", "", ""],
    ["5. 無所作為", ".32***", ".34***", ".13", ".44***", "(.89)", "", ""],
    ["6. 主動型 PP", "-.16*", "-.17*", "-.07", "-.10", "-.21**", "(.77)", ""]
], columns=["變數名稱", "1. 整體CP", "2. 階層HP", "3. 工作JCP", "4. 決策拖延", "5. 無所作為", "6. 主動性PP", " "])

# Table 3: PP Analysis
df_pp = pd.DataFrame([
    ["A. 靜態前測 (傳統干擾)", "把 PP 抽出來當作 T1 特質來做預測或調節 (K=3)。\n優：簡單保險，一定跑得出結果。\n缺：無法觀察 PP 動態消長。", "約 42 個", "🟢 絕對安全\n(N:q 比約 4.83)"],
    ["B. 第四個平行變數 (動態軌跡)", "讓 PP 同流合汙成為第 4 個節點 (K=4)。\n優：能證明動態消磨，屬 SSCI 期刊水準。⭐強烈建議\n缺：需謹慎約束不必要路徑。", "約 68 個", "🟡 稍微緊繃\n(N:q 比約 2.98)"],
    ["C. 動態交互 (Interaction)", "在潛在變數層次把 WP_PP 與 WP_CP 的殘差直接相乘。\n缺：太過複雜，要求樣本數極度龐大。", "破百 (外加非線性估計)", "🔴 保證不收斂\n(博士班量級)"]
], columns=["方法流派", "作法描述與優缺點", "預估參數負擔", "樣本生存機率評估"])

# Create Excel writer using openpyxl
with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    df_attrition.to_excel(writer, sheet_name='樣本流失檢定', index=False)
    df_corr.to_excel(writer, sheet_name='相關矩陣與信度', index=False)
    df_pp.to_excel(writer, sheet_name='PP分析防禦表', index=False)

# Apply SPSS styling
wb = openpyxl.load_workbook(excel_path)

# SPSS Border Rules: Thick top and bottom for header, Thin bottom for header, Thick bottom for last row, NO vertical borders.
thick_border = Side(border_style="thick", color="000000")
thin_border = Side(border_style="thin", color="000000")
no_border = Side(border_style=None)

for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    max_row = ws.max_row
    max_col = ws.max_column
    
    # Auto-adjust column widths
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                lines = str(cell.value).split('\n')
                for line in lines:
                    # heuristic: asian characters are wider
                    length = sum(2 if ord(c) > 127 else 1 for c in line)
                    if length > max_length:
                        max_length = length
            except:
                pass
        adjusted_width = (max_length + 4)
        ws.column_dimensions[column].width = min(adjusted_width, 60) # cap at 60

    for row_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=max_row, min_col=1, max_col=max_col), 1):
        for cell in row:
            # Set font (Times New Roman for English/Numbers, but keeps system default for Chinese usually)
            cell.font = Font(name='Times New Roman', size=12, bold=(row_idx == 1))
            
            # Set alignment (SPSS usually centers data, except for text-heavy columns)
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            
            if sheet_name == '相關矩陣與信度' and cell.column == 1:
                cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
                
            if sheet_name == 'PP分析防禦表' and cell.column == 2 and row_idx > 1:
                cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
            elif sheet_name == 'PP分析防禦表' and cell.column == 4 and row_idx > 1:
                cell.alignment = Alignment(horizontal='center', vertical='top', wrap_text=True)
            
            # Borders
            top = no_border
            bottom = no_border
            
            if row_idx == 1:
                top = thick_border
                bottom = thin_border
            elif row_idx == max_row:
                bottom = thick_border
            
            cell.border = Border(top=top, bottom=bottom, left=no_border, right=no_border)

wb.save(excel_path)
print(f"Excel file created at: {excel_path}")
