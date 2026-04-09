import pandas as pd
import os
import openpyxl
from openpyxl.styles import Border, Side, Alignment, Font, PatternFill

OUTPUT_DIR = r"g:\其他電腦\我的 PC\NSYSU_HRM\Thesis_LM\05_會議報告與關聯圖\報告簡報"
excel_path = os.path.join(OUTPUT_DIR, "Canva_Tables_SPSS_Style_v2.xlsx")

# ============================================================
# 既有表格（保留原版）
# ============================================================

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

# ============================================================
# 第三章 — 第二節：問卷發放與回收摘要表
# ============================================================
df_survey = pd.DataFrame([
    ["第一階段 (T1)", "510", "460", "27", "433", "84.9%",
     "剔除：注意力題未通過 50 人、不符就業資格 25 人、重複填答 2 人"],
    ["第二階段 (T2)", "433*", "387", "6", "386", "89.1%",
     "剔除：注意力題未通過 5 人、配對失敗 1 人"],
    ["第三階段 (T3)", "386*", "279", "2", "277", "71.8%",
     "最終三波完整配對樣本"],
], columns=["施測波次", "發放份數", "回收份數", "剔除份數", "有效份數", "有效回收率", "備註"])

# ============================================================
# 第三章 — 第三節：量表摘要表
# ============================================================
df_scales = pd.DataFrame([
    [
        "職涯高原\nCareer Plateau (CP)",
        "Milliman (1992)",
        "英文原版\n由研究者翻譯",
        "2（階層停滯 HP、\n工作內容停滯 JCP）",
        "12\n（各 6 題）",
        "五點 Likert\n(1=非常不同意\n5=非常同意)",
        "HP：題 4、6（R）\nJCP：題 7–11（R）",
        "HP: α = .85\nJCP: α = .77\nCP: α = .79",
        "「我在這間公司晉升的可能性是有限的。」\n「我的工作讓我感到有挑戰性。」（R）"
    ],
    [
        "決策拖延\nDecisional Procrastination (DP)",
        "Mann et al. (1997)",
        "英文原版\n由研究者翻譯",
        "1（單維度）",
        "5",
        "五點 Likert\n(1=完全不符合我\n5=完全符合我)",
        "無",
        "α = .81",
        "「在做出最終決定之前，我花了很多時間在處理瑣碎的事情上。」"
    ],
    [
        "職涯無所作為\nCareer Inaction (CI)",
        "D'Huyvetter et al. (2025)",
        "英文原版\n由研究者翻譯",
        "1（單維度）",
        "8\n（另含 1 題注意力測試題，不計分）",
        "五點 Likert\n(1=完全不同意\n5=完全同意)",
        "無",
        "α = .90",
        "「我想調整或改變自己的職涯，但我沒有積極追求。」"
    ],
    [
        "主動性人格\nProactive Personality (PP)",
        "Parker (1998)；\n選自 Bateman &\nCrant (1993)",
        "英文原版\n由研究者翻譯",
        "1（單維度）",
        "6",
        "五點 Likert\n(1=完全不同意\n5=完全同意)",
        "無",
        "α = .75",
        "「對於我看不順眼的事物，我會改正它。」"
    ],
], columns=[
    "構念（中/英文）",
    "量表來源",
    "原文語言",
    "向度數",
    "題數",
    "計分尺度",
    "反向題",
    "本研究 Cronbach's α",
    "範例題"
])

# ============================================================
# 第三章 — 第三節/第四章：CFA 適配指標摘要表（跑完 Mplus 後填入）
# ============================================================
df_cfa = pd.DataFrame([
    ["M1：五因子模型\n（HP / JCP / PP / DP / CI）",
     "[待填]", "[待填]", "[待填]", "[待填]", "[待填]", "假設模型（理論模型）"],
    ["M2：四因子模型\n（CP 合併 / PP / DP / CI）",
     "[待填]", "[待填]", "[待填]", "[待填]", "[待填]", "比較：HP+JCP 合併為單一 CP"],
    ["M3：三因子模型\n（CP / DP / CI，主路徑）",
     "[待填]", "[待填]", "[待填]", "[待填]", "[待填]", "比較：排除 PP"],
    ["M4：單因子模型\n（所有題項合併）",
     "[待填]", "[待填]", "[待填]", "[待填]", "[待填]", "最差情境（CMV 極端檢驗）"],
], columns=["模型", "χ²（df）", "CFI", "TLI", "RMSEA [90% CI]", "SRMR", "備註"])

# ============================================================
# 第四章：敘述統計與相關矩陣（更新版，含本研究 α）
# ============================================================
df_desc_corr = pd.DataFrame([
    ["1. 職涯高原 (CP)", "2.76", "0.61", "(.79)", "", "", "", "", ""],
    ["2. 階層停滯 (HP)", "3.11", "0.90", ".84***", "(.85)", "", "", "", ""],
    ["3. 工作內容停滯 (JCP)", "2.42", "0.68", ".69***", ".18**", "(.77)", "", "", ""],
    ["4. 決策拖延 (DP)", "2.75", "0.81", ".08", ".09", ".03", "(.81)", "", ""],
    ["5. 職涯無所作為 (CI)", "2.99", "0.90", ".35***", ".37***", ".15*", ".36***", "(.90)", ""],
    ["6. 主動性人格 (PP)", "3.55", "0.57", "-.14*", "-.12*", "-.09", "-.14*", "-.15*", "(.75)"],
], columns=["變數", "M", "SD", "1", "2", "3", "4", "5", "6"])

# ============================================================
# 輸出 Excel
# ============================================================
with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    df_attrition.to_excel(writer, sheet_name='樣本流失檢定', index=False)
    df_corr.to_excel(writer, sheet_name='相關矩陣與信度', index=False)
    df_pp.to_excel(writer, sheet_name='PP分析防禦表', index=False)
    df_survey.to_excel(writer, sheet_name='CH3_問卷發放回收', index=False)
    df_scales.to_excel(writer, sheet_name='CH3_量表摘要', index=False)
    df_cfa.to_excel(writer, sheet_name='CH3_CFA適配指標', index=False)
    df_desc_corr.to_excel(writer, sheet_name='CH4_敘述統計與相關矩陣', index=False)

# ============================================================
# SPSS 學術格式樣式套用
# ============================================================
wb = openpyxl.load_workbook(excel_path)

thick_border = Side(border_style="thick", color="000000")
thin_border  = Side(border_style="thin",  color="000000")
no_border    = Side(border_style=None)

HEADER_FILL   = PatternFill("solid", start_color="D9D9D9")  # 淺灰 header
PENDING_FILL  = PatternFill("solid", start_color="FFF2CC")  # 淡黃 = 待填
NOTE_FILL     = PatternFill("solid", start_color="E2EFDA")  # 淡綠 = 備註

# 每個 sheet 的特殊設定：左對齊欄
LEFT_ALIGN_SHEETS = {
    '相關矩陣與信度': [1],
    'PP分析防禦表': [1, 2],
    'CH3_問卷發放回收': [7],
    'CH3_量表摘要': [1, 2, 4, 6, 9],
    'CH3_CFA適配指標': [1, 7],
    'CH4_敘述統計與相關矩陣': [1],
}

for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    max_row = ws.max_row
    max_col = ws.max_column
    left_cols = LEFT_ALIGN_SHEETS.get(sheet_name, [])

    # 自動欄寬
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                for line in str(cell.value).split('\n'):
                    length = sum(2 if ord(c) > 127 else 1 for c in line)
                    if length > max_length:
                        max_length = length
            except:
                pass
        ws.column_dimensions[column].width = min(max_length + 4, 55)

    for row_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=max_row, min_col=1, max_col=max_col), 1):
        is_header = (row_idx == 1)
        is_last   = (row_idx == max_row)

        for cell in row:
            col_idx = cell.column
            is_left = col_idx in left_cols

            cell.font = Font(name='Times New Roman', size=12, bold=is_header)
            cell.alignment = Alignment(
                horizontal='left' if is_left else 'center',
                vertical='center',
                wrap_text=True
            )

            # Header 底色
            if is_header:
                cell.fill = HEADER_FILL

            # 待填欄位 highlight
            if cell.value and '[待填]' in str(cell.value):
                cell.fill = PENDING_FILL
                cell.font = Font(name='Times New Roman', size=12, color='C00000')

            # 備註欄 highlight（CH3_問卷發放回收）
            if sheet_name == 'CH3_問卷發放回收' and col_idx == 7 and not is_header:
                cell.fill = NOTE_FILL

            # Borders（SPSS 學術格式：橫線，無縱線）
            top    = thick_border if is_header else no_border
            bottom = thin_border  if is_header else (thick_border if is_last else no_border)
            cell.border = Border(top=top, bottom=bottom, left=no_border, right=no_border)

    # 凍結首列
    ws.freeze_panes = ws['A2']

wb.save(excel_path)
print(f"[OK] Excel output: {excel_path}")
print(f"     Sheets: {', '.join(wb.sheetnames)}")
