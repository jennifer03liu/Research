# 研究分析結果報告 (Research Analysis Report)

## 表 1. 敘述性統計與信度分析 (Descriptive Statistics & Reliability)
| Variable           |   Items |   Mean |   SD |   Alpha |
|:-------------------|--------:|-------:|-----:|--------:|
| 階層停滯 (HP)      |       6 |   3.1  | 0.92 |    0.85 |
| 工作內容停滯 (JCP) |       5 |   2.19 | 0.8  |    0.87 |
| 主動型人格 (PP)    |       6 |   3.55 | 0.6  |    0.76 |
| 決策拖延 (DP)      |       5 |   2.81 | 0.86 |    0.83 |
| 職涯無所作為 (CI)  |       8 |   3    | 0.91 |    0.9  |

## 表 2. 相關係數矩陣 (Correlation Matrix)
| Variable           | 階層停滯 (HP)   | 工作內容停滯 (JCP)   | 主動型人格 (PP)   | 決策拖延 (DP)   | 職涯無所作為 (CI)   |
|:-------------------|:----------------|:---------------------|:------------------|:----------------|:--------------------|
| 階層停滯 (HP)      | 1.00            | 0.23***              | -0.13*            | 0.15**          | 0.39***             |
| 工作內容停滯 (JCP) | 0.23***         | 1.00                 | -0.19***          | 0.00            | 0.20***             |
| 主動型人格 (PP)    | -0.13*          | -0.19***             | 1.00              | -0.19***        | -0.21***            |
| 決策拖延 (DP)      | 0.15**          | 0.00                 | -0.19***          | 1.00            | 0.42***             |
| 職涯無所作為 (CI)  | 0.39***         | 0.20***              | -0.21***          | 0.42***         | 1.00                |

## 表 3. 模型適配度指標 (Model Fit Indices)
|   DoF |   DoF Baseline |     chi2 |   chi2 p-value |   chi2 Baseline |      CFI |      GFI |     AGFI |      NFI |      TLI |     RMSEA |      AIC |     BIC |   LogLik | Model                    | Description                                |
|------:|---------------:|---------:|---------------:|----------------:|---------:|---------:|---------:|---------:|---------:|----------:|---------:|--------:|---------:|:-------------------------|:-------------------------------------------|
|   395 |            435 | 1070.86  |              0 |         6247.03 | 0.883713 | 0.82858  | 0.811221 | 0.82858  | 0.871937 | 0.0659834 | 134.564  | 412.909 |  2.71793 | Model_1_5Factors         | 原始五因子模型 (HP, JCP, PP, DP, CI)       |
|   399 |            435 | 2131.36  |              0 |         6247.03 | 0.701935 | 0.65882  | 0.628037 | 0.65882  | 0.675042 | 0.105108  | 121.181  | 383.62  |  5.40955 | Model_2_4Factors_CP      | 四因子: 合併階層與工作內容停滯 (CP=HP+JCP) |
|   246 |            276 |  811.582 |              0 |         5430.14 | 0.890266 | 0.850541 | 0.832314 | 0.850541 | 0.876884 | 0.0764864 | 103.88   | 318.603 |  2.05985 | Model_3_4Factors_NoPP    | 四因子: 排除主動型人格 (No PP)             |
|   249 |            276 | 1861.35  |              0 |         5430.14 | 0.687174 | 0.657219 | 0.62005  | 0.657219 | 0.653253 | 0.128361  |  92.5515 | 295.345 |  4.72423 | Model_4_3Factors_CP_NoPP | 三因子: 合併CP且排除PP (CP, DP, CI)        |
|   269 |            300 |  835.111 |              0 |         5029.55 | 0.880303 | 0.833959 | 0.814824 | 0.833959 | 0.866509 | 0.0731776 | 107.761  | 330.437 |  2.11957 | Model_5_4Factors_NoDP    | 四因子: 排除決策拖延 (No DP)               |
|   272 |            300 | 1891.98  |              0 |         5029.55 | 0.657476 | 0.623827 | 0.585103 | 0.623827 | 0.622216 | 0.123105  |  96.396  | 307.143 |  4.80198 | Model_6_3Factors_CP_NoDP | 三因子: 合併CP且排除DP (CP, PP, CI)        |

## 表 4. 因素負荷量 (Factor Loadings - Standardized)
| lval   | rval   |   Est. Std | p-value   | Std. Err   | Model                    |
|:-------|:-------|-----------:|:----------|:-----------|:-------------------------|
| HP1    | HP     |      0.695 |           |            | Model_1_5Factors         |
| HP2    | HP     |      0.83  | 0.0       | 0.093      | Model_1_5Factors         |
| HP3    | HP     |      0.904 | 0.0       | 0.095      | Model_1_5Factors         |
| HP4_R  | HP     |      0.447 | 0.0       | 0.075      | Model_1_5Factors         |
| HP5    | HP     |      0.741 | 0.0       | 0.085      | Model_1_5Factors         |
| HP6_R  | HP     |      0.519 | 0.0       | 0.072      | Model_1_5Factors         |
| JCP1_R | JCP    |      0.812 |           |            | Model_1_5Factors         |
| JCP2_R | JCP    |      0.822 | 0.0       | 0.052      | Model_1_5Factors         |
| JCP3_R | JCP    |      0.843 | 0.0       | 0.054      | Model_1_5Factors         |
| JCP4_R | JCP    |      0.905 | 0.0       | 0.052      | Model_1_5Factors         |
| JCP5_R | JCP    |      0.415 | 0.0       | 0.057      | Model_1_5Factors         |
| PP1    | PP     |      0.434 |           |            | Model_1_5Factors         |
| PP2    | PP     |      0.733 | 0.0       | 0.229      | Model_1_5Factors         |
| PP3    | PP     |      0.556 | 0.0       | 0.191      | Model_1_5Factors         |
| PP4    | PP     |      0.649 | 0.0       | 0.179      | Model_1_5Factors         |
| PP5    | PP     |      0.778 | 0.0       | 0.244      | Model_1_5Factors         |
| PP6    | PP     |      0.386 | 0.0       | 0.157      | Model_1_5Factors         |
| DP1    | DP     |      0.305 |           |            | Model_1_5Factors         |
| DP2    | DP     |      0.803 | 0.0       | 0.524      | Model_1_5Factors         |
| DP3    | DP     |      0.803 | 0.0       | 0.519      | Model_1_5Factors         |
| DP4    | DP     |      0.847 | 0.0       | 0.541      | Model_1_5Factors         |
| DP5    | DP     |      0.811 | 0.0       | 0.555      | Model_1_5Factors         |
| CI1    | CI     |      0.641 |           |            | Model_1_5Factors         |
| CI2    | CI     |      0.752 | 0.0       | 0.092      | Model_1_5Factors         |
| CI3    | CI     |      0.664 | 0.0       | 0.096      | Model_1_5Factors         |
| CI4    | CI     |      0.741 | 0.0       | 0.095      | Model_1_5Factors         |
| CI5    | CI     |      0.769 | 0.0       | 0.094      | Model_1_5Factors         |
| CI6    | CI     |      0.692 | 0.0       | 0.096      | Model_1_5Factors         |
| CI7    | CI     |      0.713 | 0.0       | 0.094      | Model_1_5Factors         |
| CI8    | CI     |      0.795 | 0.0       | 0.092      | Model_1_5Factors         |
| HP1    | CP     |      0.716 |           |            | Model_2_4Factors_CP      |
| HP2    | CP     |      0.777 | 0.0       | 0.088      | Model_2_4Factors_CP      |
| HP3    | CP     |      0.851 | 0.0       | 0.089      | Model_2_4Factors_CP      |
| HP4_R  | CP     |      0.464 | 0.0       | 0.073      | Model_2_4Factors_CP      |
| HP5    | CP     |      0.776 | 0.0       | 0.081      | Model_2_4Factors_CP      |
| HP6_R  | CP     |      0.555 | 0.0       | 0.07       | Model_2_4Factors_CP      |
| JCP1_R | CP     |      0.294 | 0.0       | 0.066      | Model_2_4Factors_CP      |
| JCP2_R | CP     |      0.319 | 0.0       | 0.064      | Model_2_4Factors_CP      |
| JCP3_R | CP     |      0.376 | 0.0       | 0.066      | Model_2_4Factors_CP      |
| JCP4_R | CP     |      0.277 | 0.0       | 0.066      | Model_2_4Factors_CP      |
| JCP5_R | CP     |      0.148 | 0.006     | 0.06       | Model_2_4Factors_CP      |
| PP1    | PP     |      0.432 |           |            | Model_2_4Factors_CP      |
| PP2    | PP     |      0.728 | 0.0       | 0.23       | Model_2_4Factors_CP      |
| PP3    | PP     |      0.564 | 0.0       | 0.193      | Model_2_4Factors_CP      |
| PP4    | PP     |      0.648 | 0.0       | 0.18       | Model_2_4Factors_CP      |
| PP5    | PP     |      0.781 | 0.0       | 0.247      | Model_2_4Factors_CP      |
| PP6    | PP     |      0.385 | 0.0       | 0.158      | Model_2_4Factors_CP      |
| DP1    | DP     |      0.304 |           |            | Model_2_4Factors_CP      |
| DP2    | DP     |      0.803 | 0.0       | 0.528      | Model_2_4Factors_CP      |
| DP3    | DP     |      0.803 | 0.0       | 0.522      | Model_2_4Factors_CP      |
| DP4    | DP     |      0.847 | 0.0       | 0.545      | Model_2_4Factors_CP      |
| DP5    | DP     |      0.811 | 0.0       | 0.558      | Model_2_4Factors_CP      |
| CI1    | CI     |      0.641 |           |            | Model_2_4Factors_CP      |
| CI2    | CI     |      0.752 | 0.0       | 0.092      | Model_2_4Factors_CP      |
| CI3    | CI     |      0.665 | 0.0       | 0.096      | Model_2_4Factors_CP      |
| CI4    | CI     |      0.742 | 0.0       | 0.095      | Model_2_4Factors_CP      |
| CI5    | CI     |      0.768 | 0.0       | 0.094      | Model_2_4Factors_CP      |
| CI6    | CI     |      0.692 | 0.0       | 0.096      | Model_2_4Factors_CP      |
| CI7    | CI     |      0.711 | 0.0       | 0.094      | Model_2_4Factors_CP      |
| CI8    | CI     |      0.794 | 0.0       | 0.092      | Model_2_4Factors_CP      |
| HP1    | HP     |      0.695 |           |            | Model_3_4Factors_NoPP    |
| HP2    | HP     |      0.829 | 0.0       | 0.093      | Model_3_4Factors_NoPP    |
| HP3    | HP     |      0.904 | 0.0       | 0.095      | Model_3_4Factors_NoPP    |
| HP4_R  | HP     |      0.447 | 0.0       | 0.075      | Model_3_4Factors_NoPP    |
| HP5    | HP     |      0.742 | 0.0       | 0.085      | Model_3_4Factors_NoPP    |
| HP6_R  | HP     |      0.519 | 0.0       | 0.072      | Model_3_4Factors_NoPP    |
| JCP1_R | JCP    |      0.812 |           |            | Model_3_4Factors_NoPP    |
| JCP2_R | JCP    |      0.822 | 0.0       | 0.052      | Model_3_4Factors_NoPP    |
| JCP3_R | JCP    |      0.842 | 0.0       | 0.054      | Model_3_4Factors_NoPP    |
| JCP4_R | JCP    |      0.905 | 0.0       | 0.052      | Model_3_4Factors_NoPP    |
| JCP5_R | JCP    |      0.416 | 0.0       | 0.057      | Model_3_4Factors_NoPP    |
| DP1    | DP     |      0.307 |           |            | Model_3_4Factors_NoPP    |
| DP2    | DP     |      0.802 | 0.0       | 0.517      | Model_3_4Factors_NoPP    |
| DP3    | DP     |      0.805 | 0.0       | 0.513      | Model_3_4Factors_NoPP    |
| DP4    | DP     |      0.847 | 0.0       | 0.534      | Model_3_4Factors_NoPP    |
| DP5    | DP     |      0.809 | 0.0       | 0.546      | Model_3_4Factors_NoPP    |
| CI1    | CI     |      0.641 |           |            | Model_3_4Factors_NoPP    |
| CI2    | CI     |      0.751 | 0.0       | 0.092      | Model_3_4Factors_NoPP    |
| CI3    | CI     |      0.665 | 0.0       | 0.096      | Model_3_4Factors_NoPP    |
| CI4    | CI     |      0.741 | 0.0       | 0.095      | Model_3_4Factors_NoPP    |
| CI5    | CI     |      0.77  | 0.0       | 0.093      | Model_3_4Factors_NoPP    |
| CI6    | CI     |      0.691 | 0.0       | 0.096      | Model_3_4Factors_NoPP    |
| CI7    | CI     |      0.713 | 0.0       | 0.094      | Model_3_4Factors_NoPP    |
| CI8    | CI     |      0.794 | 0.0       | 0.092      | Model_3_4Factors_NoPP    |
| HP1    | CP     |      0.716 |           |            | Model_4_3Factors_CP_NoPP |
| HP2    | CP     |      0.78  | 0.0       | 0.088      | Model_4_3Factors_CP_NoPP |
| HP3    | CP     |      0.854 | 0.0       | 0.089      | Model_4_3Factors_CP_NoPP |
| HP4_R  | CP     |      0.463 | 0.0       | 0.073      | Model_4_3Factors_CP_NoPP |
| HP5    | CP     |      0.774 | 0.0       | 0.081      | Model_4_3Factors_CP_NoPP |
| HP6_R  | CP     |      0.553 | 0.0       | 0.07       | Model_4_3Factors_CP_NoPP |
| JCP1_R | CP     |      0.29  | 0.0       | 0.066      | Model_4_3Factors_CP_NoPP |
| JCP2_R | CP     |      0.316 | 0.0       | 0.064      | Model_4_3Factors_CP_NoPP |
| JCP3_R | CP     |      0.372 | 0.0       | 0.066      | Model_4_3Factors_CP_NoPP |
| JCP4_R | CP     |      0.273 | 0.0       | 0.066      | Model_4_3Factors_CP_NoPP |
| JCP5_R | CP     |      0.147 | 0.006     | 0.06       | Model_4_3Factors_CP_NoPP |
| DP1    | DP     |      0.307 |           |            | Model_4_3Factors_CP_NoPP |
| DP2    | DP     |      0.802 | 0.0       | 0.519      | Model_4_3Factors_CP_NoPP |
| DP3    | DP     |      0.805 | 0.0       | 0.515      | Model_4_3Factors_CP_NoPP |
| DP4    | DP     |      0.847 | 0.0       | 0.536      | Model_4_3Factors_CP_NoPP |
| DP5    | DP     |      0.809 | 0.0       | 0.549      | Model_4_3Factors_CP_NoPP |
| CI1    | CI     |      0.641 |           |            | Model_4_3Factors_CP_NoPP |
| CI2    | CI     |      0.752 | 0.0       | 0.092      | Model_4_3Factors_CP_NoPP |
| CI3    | CI     |      0.667 | 0.0       | 0.096      | Model_4_3Factors_CP_NoPP |
| CI4    | CI     |      0.743 | 0.0       | 0.095      | Model_4_3Factors_CP_NoPP |
| CI5    | CI     |      0.769 | 0.0       | 0.093      | Model_4_3Factors_CP_NoPP |
| CI6    | CI     |      0.692 | 0.0       | 0.096      | Model_4_3Factors_CP_NoPP |
| CI7    | CI     |      0.711 | 0.0       | 0.094      | Model_4_3Factors_CP_NoPP |
| CI8    | CI     |      0.793 | 0.0       | 0.092      | Model_4_3Factors_CP_NoPP |
| HP1    | HP     |      0.695 |           |            | Model_5_4Factors_NoDP    |
| HP2    | HP     |      0.829 | 0.0       | 0.093      | Model_5_4Factors_NoDP    |
| HP3    | HP     |      0.904 | 0.0       | 0.095      | Model_5_4Factors_NoDP    |
| HP4_R  | HP     |      0.447 | 0.0       | 0.075      | Model_5_4Factors_NoDP    |
| HP5    | HP     |      0.742 | 0.0       | 0.085      | Model_5_4Factors_NoDP    |
| HP6_R  | HP     |      0.519 | 0.0       | 0.072      | Model_5_4Factors_NoDP    |
| JCP1_R | JCP    |      0.811 |           |            | Model_5_4Factors_NoDP    |
| JCP2_R | JCP    |      0.823 | 0.0       | 0.052      | Model_5_4Factors_NoDP    |
| JCP3_R | JCP    |      0.844 | 0.0       | 0.054      | Model_5_4Factors_NoDP    |
| JCP4_R | JCP    |      0.904 | 0.0       | 0.052      | Model_5_4Factors_NoDP    |
| JCP5_R | JCP    |      0.415 | 0.0       | 0.057      | Model_5_4Factors_NoDP    |
| PP1    | PP     |      0.432 |           |            | Model_5_4Factors_NoDP    |
| PP2    | PP     |      0.737 | 0.0       | 0.233      | Model_5_4Factors_NoDP    |
| PP3    | PP     |      0.558 | 0.0       | 0.193      | Model_5_4Factors_NoDP    |
| PP4    | PP     |      0.646 | 0.0       | 0.18       | Model_5_4Factors_NoDP    |
| PP5    | PP     |      0.777 | 0.0       | 0.247      | Model_5_4Factors_NoDP    |
| PP6    | PP     |      0.386 | 0.0       | 0.158      | Model_5_4Factors_NoDP    |
| CI1    | CI     |      0.637 |           |            | Model_5_4Factors_NoDP    |
| CI2    | CI     |      0.747 | 0.0       | 0.093      | Model_5_4Factors_NoDP    |
| CI3    | CI     |      0.664 | 0.0       | 0.097      | Model_5_4Factors_NoDP    |
| CI4    | CI     |      0.739 | 0.0       | 0.096      | Model_5_4Factors_NoDP    |
| CI5    | CI     |      0.767 | 0.0       | 0.095      | Model_5_4Factors_NoDP    |
| CI6    | CI     |      0.691 | 0.0       | 0.098      | Model_5_4Factors_NoDP    |
| CI7    | CI     |      0.719 | 0.0       | 0.095      | Model_5_4Factors_NoDP    |
| CI8    | CI     |      0.8   | 0.0       | 0.094      | Model_5_4Factors_NoDP    |
| HP1    | CP     |      0.716 |           |            | Model_6_3Factors_CP_NoDP |
| HP2    | CP     |      0.777 | 0.0       | 0.088      | Model_6_3Factors_CP_NoDP |
| HP3    | CP     |      0.852 | 0.0       | 0.089      | Model_6_3Factors_CP_NoDP |
| HP4_R  | CP     |      0.464 | 0.0       | 0.073      | Model_6_3Factors_CP_NoDP |
| HP5    | CP     |      0.775 | 0.0       | 0.081      | Model_6_3Factors_CP_NoDP |
| HP6_R  | CP     |      0.555 | 0.0       | 0.07       | Model_6_3Factors_CP_NoDP |
| JCP1_R | CP     |      0.294 | 0.0       | 0.066      | Model_6_3Factors_CP_NoDP |
| JCP2_R | CP     |      0.319 | 0.0       | 0.064      | Model_6_3Factors_CP_NoDP |
| JCP3_R | CP     |      0.376 | 0.0       | 0.066      | Model_6_3Factors_CP_NoDP |
| JCP4_R | CP     |      0.277 | 0.0       | 0.066      | Model_6_3Factors_CP_NoDP |
| JCP5_R | CP     |      0.148 | 0.006     | 0.06       | Model_6_3Factors_CP_NoDP |
| PP1    | PP     |      0.431 |           |            | Model_6_3Factors_CP_NoDP |
| PP2    | PP     |      0.731 | 0.0       | 0.233      | Model_6_3Factors_CP_NoDP |
| PP3    | PP     |      0.565 | 0.0       | 0.195      | Model_6_3Factors_CP_NoDP |
| PP4    | PP     |      0.645 | 0.0       | 0.181      | Model_6_3Factors_CP_NoDP |
| PP5    | PP     |      0.78  | 0.0       | 0.249      | Model_6_3Factors_CP_NoDP |
| PP6    | PP     |      0.385 | 0.0       | 0.158      | Model_6_3Factors_CP_NoDP |
| CI1    | CI     |      0.637 |           |            | Model_6_3Factors_CP_NoDP |
| CI2    | CI     |      0.747 | 0.0       | 0.093      | Model_6_3Factors_CP_NoDP |
| CI3    | CI     |      0.665 | 0.0       | 0.098      | Model_6_3Factors_CP_NoDP |
| CI4    | CI     |      0.74  | 0.0       | 0.096      | Model_6_3Factors_CP_NoDP |
| CI5    | CI     |      0.766 | 0.0       | 0.095      | Model_6_3Factors_CP_NoDP |
| CI6    | CI     |      0.692 | 0.0       | 0.098      | Model_6_3Factors_CP_NoDP |
| CI7    | CI     |      0.718 | 0.0       | 0.095      | Model_6_3Factors_CP_NoDP |
| CI8    | CI     |      0.799 | 0.0       | 0.094      | Model_6_3Factors_CP_NoDP |

## 表 5. 收斂效度 (Convergent Validity - CR & AVE)
| Variable   |   AVE |    CR | Status   |
|:-----------|------:|------:|:---------|
| HP1        | 0.498 | 0.856 | Check    |
| HP2        | 0.647 | 0.916 | Good     |
| HP3        | 0.772 | 0.953 | Good     |
| HP4_R      | 0.208 | 0.611 | Check    |
| HP5        | 0.575 | 0.89  | Good     |
| HP6_R      | 0.288 | 0.708 | Check    |
| JCP1_R     | 0.372 | 0.745 | Check    |
| JCP2_R     | 0.389 | 0.761 | Check    |
| JCP3_R     | 0.425 | 0.795 | Check    |
| JCP4_R     | 0.447 | 0.791 | Check    |
| JCP5_R     | 0.097 | 0.345 | Check    |
| PP1        | 0.187 | 0.479 | Check    |
| PP2        | 0.536 | 0.822 | Good     |
| PP3        | 0.314 | 0.647 | Check    |
| PP4        | 0.419 | 0.742 | Check    |
| PP5        | 0.607 | 0.861 | Good     |
| PP6        | 0.149 | 0.411 | Check    |
| DP1        | 0.094 | 0.292 | Check    |
| DP2        | 0.644 | 0.878 | Good     |
| DP3        | 0.646 | 0.88  | Good     |
| DP4        | 0.718 | 0.911 | Good     |
| DP5        | 0.656 | 0.884 | Good     |
| CI1        | 0.409 | 0.806 | Check    |
| CI2        | 0.562 | 0.885 | Good     |
| CI3        | 0.442 | 0.826 | Check    |
| CI4        | 0.549 | 0.88  | Good     |
| CI5        | 0.59  | 0.896 | Good     |
| CI6        | 0.478 | 0.846 | Check    |
| CI7        | 0.51  | 0.862 | Good     |
| CI8        | 0.633 | 0.912 | Good     |

## 表 6. 多模型比較摘要 (Model Comparison Summary)
比較不同假設模型的適配度指標。
| Model                    | Description                                |   DoF |      CFI |      TLI |     RMSEA |      AIC |     BIC |
|:-------------------------|:-------------------------------------------|------:|---------:|---------:|----------:|---------:|--------:|
| Model_1_5Factors         | 原始五因子模型 (HP, JCP, PP, DP, CI)       |   395 | 0.883713 | 0.871937 | 0.0659834 | 134.564  | 412.909 |
| Model_2_4Factors_CP      | 四因子: 合併階層與工作內容停滯 (CP=HP+JCP) |   399 | 0.701935 | 0.675042 | 0.105108  | 121.181  | 383.62  |
| Model_3_4Factors_NoPP    | 四因子: 排除主動型人格 (No PP)             |   246 | 0.890266 | 0.876884 | 0.0764864 | 103.88   | 318.603 |
| Model_4_3Factors_CP_NoPP | 三因子: 合併CP且排除PP (CP, DP, CI)        |   249 | 0.687174 | 0.653253 | 0.128361  |  92.5515 | 295.345 |
| Model_5_4Factors_NoDP    | 四因子: 排除決策拖延 (No DP)               |   269 | 0.880303 | 0.866509 | 0.0731776 | 107.761  | 330.437 |
| Model_6_3Factors_CP_NoDP | 三因子: 合併CP且排除DP (CP, PP, CI)        |   272 | 0.657476 | 0.622216 | 0.123105  |  96.396  | 307.143 |

| Model                    | lval   | rval   |   Est. Std | p-value                |
|:-------------------------|:-------|:-------|-----------:|:-----------------------|
| Model_4_3Factors_CP_NoPP | JCP5_R | CP     |   0.146657 | 0.005994982929204751   |
| Model_6_3Factors_CP_NoDP | JCP5_R | CP     |   0.147941 | 0.0055829658663772985  |
| Model_2_4Factors_CP      | JCP5_R | CP     |   0.148094 | 0.0055355330244724055  |
| Model_4_3Factors_CP_NoPP | JCP4_R | CP     |   0.273169 | 3.1078650164495514e-07 |
| Model_6_3Factors_CP_NoDP | JCP4_R | CP     |   0.276667 | 2.2082677197943212e-07 |
| Model_2_4Factors_CP      | JCP4_R | CP     |   0.277023 | 2.1318439324957694e-07 |
| Model_4_3Factors_CP_NoPP | JCP1_R | CP     |   0.290324 | 5.395919244755021e-08  |
| Model_6_3Factors_CP_NoDP | JCP1_R | CP     |   0.293883 | 3.735566900253673e-08  |
| Model_2_4Factors_CP      | JCP1_R | CP     |   0.294244 | 3.597060271864905e-08  |
| Model_2_4Factors_CP      | DP1    | DP     |   0.304382 | -                      |
| Model_1_5Factors         | DP1    | DP     |   0.30535  | -                      |
| Model_4_3Factors_CP_NoPP | DP1    | DP     |   0.306692 | -                      |
| Model_3_4Factors_NoPP    | DP1    | DP     |   0.307291 | -                      |
| Model_4_3Factors_CP_NoPP | JCP2_R | CP     |   0.31564  | 3.3949945077438315e-09 |
| Model_6_3Factors_CP_NoDP | JCP2_R | CP     |   0.318949 | 2.348960359555008e-09  |
| Model_2_4Factors_CP      | JCP2_R | CP     |   0.319137 | 2.2995374493461895e-09 |
| Model_4_3Factors_CP_NoPP | JCP3_R | CP     |   0.37223  | 3.191447106587475e-12  |
| Model_6_3Factors_CP_NoDP | JCP3_R | CP     |   0.375731 | 2.0246027077064355e-12 |
| Model_2_4Factors_CP      | JCP3_R | CP     |   0.375832 | 1.9972912213006566e-12 |
| Model_6_3Factors_CP_NoDP | PP6    | PP     |   0.384923 | 2.5765511280084752e-08 |
| Model_2_4Factors_CP      | PP6    | PP     |   0.385144 | 2.3558109907284575e-08 |
| Model_5_4Factors_NoDP    | PP6    | PP     |   0.386041 | 2.2776192043494348e-08 |
| Model_1_5Factors         | PP6    | PP     |   0.386228 | 2.0366549113859378e-08 |
| Model_5_4Factors_NoDP    | JCP5_R | JCP    |   0.41533  | 2.220446049250313e-16  |
| Model_1_5Factors         | JCP5_R | JCP    |   0.415414 | 2.220446049250313e-16  |
| Model_3_4Factors_NoPP    | JCP5_R | JCP    |   0.415917 | 2.220446049250313e-16  |
| Model_6_3Factors_CP_NoDP | PP1    | PP     |   0.430756 | -                      |
| Model_5_4Factors_NoDP    | PP1    | PP     |   0.431697 | -                      |
| Model_2_4Factors_CP      | PP1    | PP     |   0.432307 | -                      |
| Model_1_5Factors         | PP1    | PP     |   0.433741 | -                      |
| Model_1_5Factors         | HP4_R  | HP     |   0.447002 | 0.0                    |
| Model_3_4Factors_NoPP    | HP4_R  | HP     |   0.447117 | 0.0                    |
| Model_5_4Factors_NoDP    | HP4_R  | HP     |   0.447253 | 0.0                    |
| Model_4_3Factors_CP_NoPP | HP4_R  | CP     |   0.463305 | 0.0                    |
| Model_2_4Factors_CP      | HP4_R  | CP     |   0.464184 | 0.0                    |
| Model_6_3Factors_CP_NoDP | HP4_R  | CP     |   0.464199 | 0.0                    |
| Model_1_5Factors         | HP6_R  | HP     |   0.518589 | 0.0                    |
| Model_3_4Factors_NoPP    | HP6_R  | HP     |   0.51881  | 0.0                    |
| Model_5_4Factors_NoDP    | HP6_R  | HP     |   0.518998 | 0.0                    |
| Model_4_3Factors_CP_NoPP | HP6_R  | CP     |   0.553144 | 0.0                    |
| Model_6_3Factors_CP_NoDP | HP6_R  | CP     |   0.555206 | 0.0                    |
| Model_2_4Factors_CP      | HP6_R  | CP     |   0.555322 | 0.0                    |
| Model_1_5Factors         | PP3    | PP     |   0.556107 | 5.306421968498398e-12  |
| Model_5_4Factors_NoDP    | PP3    | PP     |   0.557906 | 6.1237681592274384e-12 |
| Model_2_4Factors_CP      | PP3    | PP     |   0.563651 | 4.668043729338933e-12  |
| Model_6_3Factors_CP_NoDP | PP3    | PP     |   0.564805 | 5.28177501735172e-12   |

## 📈 績效考核對職涯停滯之影響分析 (Performance Appraisal Impact)

### 1. 績效考核幫助程度 (Utility)
- **高幫助組 (High)**: 填答 4 (有幫助), 5 (非常有幫助)
- **低幫助組 (Low)**: 填答 1 (完全沒幫助) ~ 3 (普通)

| Variable   |   High Help (N=167) |   Low Help (N=200) |   Diff | p-value   |
|:-----------|--------------------:|-------------------:|-------:|:----------|
| HP         |                2.71 |               3.42 |  -0.71 | 0.000 *** |
| JCP        |                1.91 |               2.4  |  -0.5  | 0.000 *** |
| PP         |                3.63 |               3.45 |   0.17 | 0.006 **  |
| DP         |                2.72 |               2.86 |  -0.14 | 0.113     |
| CI         |                2.75 |               3.2  |  -0.45 | 0.000 *** |

> **解讀**：若 Diff 為負且顯著(*)，代表「覺得有幫助的人」該變項分數顯著較低 (例如停滯感較低)。

### 2. 是否有績效考核 (Existence)
- **有 (Yes)**: PM_Has = 1
- **無 (No)**: PM_Has = 0

| Variable   |   Yes (N=367) |   No (N=27) |   Diff |   p-value |
|:-----------|--------------:|------------:|-------:|----------:|
| HP         |          3.09 |        3.19 |  -0.09 |     0.658 |
| JCP        |          2.18 |        2.28 |  -0.1  |     0.633 |
| PP         |          3.53 |        3.72 |  -0.19 |     0.104 |
| DP         |          2.8  |        2.98 |  -0.18 |     0.383 |
| CI         |          3    |        3.08 |  -0.09 |     0.683 |

### 3. 績效考核結果性質 (Result Nature)
比較不同考核結果 (例如: 1=負面/普通, 2=正面... 需確認問卷定義) 之差異。

| Variable   |   F-value | p-value   |   Group 1 Mean |   Group 2 Mean |   Group 3 Mean |
|:-----------|----------:|:----------|---------------:|---------------:|---------------:|
| HP         |     28.52 | 0.000 *** |           4.22 |           3.35 |           2.78 |
| JCP        |     11.57 | 0.000 *** |           2.47 |           2.36 |           1.99 |
| PP         |      1.48 | 0.228     |           3.3  |           3.5  |           3.58 |
| DP         |      7.58 | 0.001 *** |           3.2  |           2.95 |           2.63 |
| CI         |     14.56 | 0.000 *** |           3.56 |           3.21 |           2.76 |

### 4. 績效考核形式 (Appraisal Forms)
比較「有採用某種形式(1)」 vs 「沒採用(0)」的差異。

#### 形式: Supervisor
| Variable   |   With Supervisor (N=345) |   No Supervisor (N=22) |   Diff |   p-value |
|:-----------|--------------------------:|-----------------------:|-------:|----------:|
| HP         |                      3.09 |                   3.11 |  -0.01 |     0.946 |
| JCP        |                      2.17 |                   2.29 |  -0.12 |     0.492 |
| PP         |                      3.54 |                   3.42 |   0.12 |     0.392 |
| DP         |                      2.79 |                   2.99 |  -0.2  |     0.279 |
| CI         |                      3    |                   2.98 |   0.01 |     0.937 |

#### 形式: Self
| Variable   |   With Self (N=275) |   No Self (N=92) |   Diff |   p-value |
|:-----------|--------------------:|-----------------:|-------:|----------:|
| HP         |                3.1  |             3.06 |   0.05 |     0.681 |
| JCP        |                2.22 |             2.07 |   0.15 |     0.122 |
| PP         |                3.52 |             3.57 |  -0.06 |     0.454 |
| DP         |                2.77 |             2.87 |  -0.1  |     0.348 |
| CI         |                2.99 |             3.02 |  -0.03 |     0.757 |

#### 形式: Interview
| Variable   |   With Interview (N=261) |   No Interview (N=106) |   Diff | p-value   |
|:-----------|-------------------------:|-----------------------:|-------:|:----------|
| HP         |                     3.01 |                   3.29 |  -0.28 | 0.006 **  |
| JCP        |                     2.09 |                   2.39 |  -0.29 | 0.001 **  |
| PP         |                     3.56 |                   3.48 |   0.08 | 0.274     |
| DP         |                     2.75 |                   2.92 |  -0.17 | 0.088     |
| CI         |                     2.95 |                   3.11 |  -0.16 | 0.120     |

#### 形式: Other
| Variable   |   With Other (N=0) |   No Other (N=367) |   Diff | p-value   |
|:-----------|-------------------:|-------------------:|-------:|:----------|
| HP         |                nan |               3.09 |    nan | nan       |
| JCP        |                nan |               2.18 |    nan | nan       |
| PP         |                nan |               3.53 |    nan | nan       |
| DP         |                nan |               2.8  |    nan | nan       |
| CI         |                nan |               3    |    nan | nan       |



