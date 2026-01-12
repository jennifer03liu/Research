*** SPSS Syntax for T1 Cross-Sectional Regression Path Analysis ***.
* 說明：RI-CLPM 需要 T1, T2 多波資料才能執行。
* 目標：先以 T1 資料檢驗變數間的「橫斷面關聯」，作為初步驗證。
* 路徑假設：CP (HCP/JCP) -> DP -> CI
* 人格特質 (PP)：暫時視為自變項(前因)放入模型。

*** 模型 1：檢驗 X (高原, PP) 對 M (拖延) 的影響 ***.
* 依變項：DP_Mean.
* 自變項：控制變項(年齡,年資), PP, HCP, JCP.
REGRESSION
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN
  /DEPENDENT DP_Mean
  /METHOD=ENTER Age NowJobTenure
  /METHOD=ENTER PP_Mean
  /METHOD=ENTER HCP_Mean JCP_Mean.

*** 模型 2：檢驗 X (高原, PP) 和 M (拖延) 對 Y (無所作為) 的影響 ***.
* 依變項：CI_Mean.
* 自變項：控制變項, PP, HCP, JCP, 以及中介變項 DP.
* 若 DP 顯著，且 HCP/JCP 影響變小，則支持中介效果。
REGRESSION
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA CHANGE
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN
  /DEPENDENT CI_Mean
  /METHOD=ENTER Age NowJobTenure
  /METHOD=ENTER PP_Mean
  /METHOD=ENTER HCP_Mean JCP_Mean
  /METHOD=ENTER DP_Mean.
