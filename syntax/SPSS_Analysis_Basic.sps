*** SPSS Syntax for Basic Analysis (Compute Composites & Descriptives) ***.

*** 1. 計算構面平均數 (Compute Composite Scores) ***.
* 使用 MEAN 函數計算平均值 (SPSS 會自動處理 system missing).

* HCP 職涯高原 (注意題項方向).
COMPUTE HCP_Mean = MEAN(HCP1, HCP2, HCP3, HCP4_R, HCP5, HCP6_R).
* JCP 職務內容高原 (注意題項方向).
COMPUTE JCP_Mean = MEAN(JCP1_R, JCP2_R, JCP3_R, JCP4_R, JCP5_R, JCP6).
* PP 主動性人格.
COMPUTE PP_Mean = MEAN(PP1, PP2, PP3, PP4, PP5, PP6).
* DP 決策拖延.
COMPUTE DP_Mean = MEAN(DP1, DP2, DP3, DP4, DP5).
* CI 職涯無所作為.
COMPUTE CI_Mean = MEAN(CI1, CI2, CI3, CI4, CI5, CI6, CI7, CI8).
EXECUTE.

* 設定標籤.
VARIABLE LABELS
  HCP_Mean "職涯高原 (平均)"
  JCP_Mean "職務內容高原 (平均)"
  PP_Mean "主動性人格 (平均)"
  DP_Mean "決策拖延 (平均)"
  CI_Mean "職涯無所作為 (平均)".

*** 2. 敘述性統計 (Descriptive Statistics) ***.

* (A) 類別變數：次數分配表 (Frequencies).
FREQUENCIES VARIABLES=Gender Education Marriage Position Industry OrgSize PM_Has PM_Result
  /ORDER=ANALYSIS.

* (B) 連續變數 & 構面得分：平均數與標準差 (Descriptives).
DESCRIPTIVES VARIABLES=Age NowJobTenure JobTenure WorkHours HCP_Mean JCP_Mean PP_Mean DP_Mean CI_Mean
  /STATISTICS=MEAN STDDEV MIN MAX.

*** 3. 相關分析 (Correlations) ***.
CORRELATIONS
  /VARIABLES=HCP_Mean JCP_Mean PP_Mean DP_Mean CI_Mean Age NowJobTenure
  /PRINT=TWOTAIL NOSIG
  /MISSING=PAIRWISE.
