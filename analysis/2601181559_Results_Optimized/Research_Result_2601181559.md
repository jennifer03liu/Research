# 研究分析結果報告 (Research Analysis Report)

## 表 1. 敘述性統計與信度分析 (Descriptive Statistics & Reliability)
| Variable           |   Items |   Mean |   SD |   Alpha |
|:-------------------|--------:|-------:|-----:|--------:|
| 階層停滯 (HP)      |       6 |   3.1  | 0.92 |    0.85 |
| 工作內容停滯 (JCP) |       6 |   2.41 | 0.68 |    0.77 |
| 主動型人格 (PP)    |       6 |   3.55 | 0.6  |    0.75 |
| 決策拖延 (DP)      |       5 |   2.81 | 0.85 |    0.83 |
| 職涯無所作為 (CI)  |       8 |   3    | 0.9  |    0.9  |

## 表 2. 相關係數矩陣 (Correlation Matrix)
| Variable           | 階層停滯 (HP)   | 工作內容停滯 (JCP)   | 主動型人格 (PP)   | 決策拖延 (DP)   | 職涯無所作為 (CI)   |
|:-------------------|:----------------|:---------------------|:------------------|:----------------|:--------------------|
| 階層停滯 (HP)      | 1.00            | 0.24***              | -0.13*            | 0.14**          | 0.39***             |
| 工作內容停滯 (JCP) | 0.24***         | 1.00                 | -0.11*            | -0.01           | 0.20***             |
| 主動型人格 (PP)    | -0.13*          | -0.11*               | 1.00              | -0.19***        | -0.21***            |
| 決策拖延 (DP)      | 0.14**          | -0.01                | -0.19***          | 1.00            | 0.42***             |
| 職涯無所作為 (CI)  | 0.39***         | 0.20***              | -0.21***          | 0.42***         | 1.00                |

## 表 3. 模型適配度指標 (Model Fit Indices)
|   DoF |   DoF Baseline |     chi2 |   chi2 p-value |   chi2 Baseline |      CFI |      GFI |     AGFI |      NFI |      TLI |     RMSEA |      AIC |     BIC |   LogLik | Model                    | Description                                |
|------:|---------------:|---------:|---------------:|----------------:|---------:|---------:|---------:|---------:|---------:|----------:|---------:|--------:|---------:|:-------------------------|:-------------------------------------------|
|   424 |            465 | 1165.26  |              0 |         6405.84 | 0.875227 | 0.818094 | 0.800504 | 0.818094 | 0.863161 | 0.0662766 | 138.159  | 425.364 |  2.92045 | Model_1_5Factors         | 原始五因子模型 (HP, JCP, PP, DP, CI)       |
|   428 |            465 | 2234.32  |              0 |         6405.84 | 0.695949 | 0.651206 | 0.621053 | 0.651206 | 0.669664 | 0.102975  | 124.8    | 396.05  |  5.59979 | Model_2_4Factors_CP      | 四因子: 合併階層與工作內容停滯 (CP=HP+JCP) |
|   269 |            300 |  872.921 |              0 |         5554.42 | 0.885064 | 0.842842 | 0.824731 | 0.842842 | 0.871819 | 0.0751056 | 107.624  | 331.006 |  2.18777 | Model_3_4Factors_NoPP    | 四因子: 排除主動型人格 (No PP)             |
|   272 |            300 | 1931.5   |              0 |         5554.42 | 0.684171 | 0.652259 | 0.616462 | 0.652259 | 0.651659 | 0.123812  |  96.3183 | 307.733 |  4.84085 | Model_4_3Factors_CP_NoPP | 三因子: 合併CP且排除PP (CP, DP, CI)        |
|   293 |            325 |  918.06  |              0 |         5170.06 | 0.87099  | 0.822428 | 0.803034 | 0.822428 | 0.8569   | 0.0732125 | 111.398  | 342.758 |  2.3009  | Model_5_4Factors_NoDP    | 四因子: 排除決策拖延 (No DP)               |
|   296 |            325 | 1983.8   |              0 |         5170.06 | 0.651645 | 0.616291 | 0.578698 | 0.616291 | 0.617516 | 0.119694  | 100.056  | 319.449 |  4.97192 | Model_6_3Factors_CP_NoDP | 三因子: 合併CP且排除DP (CP, PP, CI)        |

## 表 4. 因素負荷量 (Factor Loadings - Standardized)
| lval   | rval   |   Est. Std | p-value   | Std. Err   | Model                    |
|:-------|:-------|-----------:|:----------|:-----------|:-------------------------|
| HP1    | HP     |      0.697 |           |            | Model_1_5Factors         |
| HP2    | HP     |      0.832 | 0.0       | 0.092      | Model_1_5Factors         |
| HP3    | HP     |      0.905 | 0.0       | 0.094      | Model_1_5Factors         |
| HP4_R  | HP     |      0.455 | 0.0       | 0.074      | Model_1_5Factors         |
| HP5    | HP     |      0.746 | 0.0       | 0.084      | Model_1_5Factors         |
| HP6_R  | HP     |      0.523 | 0.0       | 0.072      | Model_1_5Factors         |
| JCP1_R | JCP    |      0.811 |           |            | Model_1_5Factors         |
| JCP2_R | JCP    |      0.824 | 0.0       | 0.052      | Model_1_5Factors         |
| JCP3_R | JCP    |      0.845 | 0.0       | 0.053      | Model_1_5Factors         |
| JCP4_R | JCP    |      0.902 | 0.0       | 0.052      | Model_1_5Factors         |
| JCP5_R | JCP    |      0.418 | 0.0       | 0.056      | Model_1_5Factors         |
| JCP6   | JCP    |     -0.059 | 0.258     | 0.064      | Model_1_5Factors         |
| PP1    | PP     |      0.435 |           |            | Model_1_5Factors         |
| PP2    | PP     |      0.732 | 0.0       | 0.228      | Model_1_5Factors         |
| PP3    | PP     |      0.555 | 0.0       | 0.19       | Model_1_5Factors         |
| PP4    | PP     |      0.651 | 0.0       | 0.178      | Model_1_5Factors         |
| PP5    | PP     |      0.775 | 0.0       | 0.242      | Model_1_5Factors         |
| PP6    | PP     |      0.377 | 0.0       | 0.155      | Model_1_5Factors         |
| DP1    | DP     |      0.303 |           |            | Model_1_5Factors         |
| DP2    | DP     |      0.8   | 0.0       | 0.529      | Model_1_5Factors         |
| DP3    | DP     |      0.8   | 0.0       | 0.524      | Model_1_5Factors         |
| DP4    | DP     |      0.848 | 0.0       | 0.547      | Model_1_5Factors         |
| DP5    | DP     |      0.813 | 0.0       | 0.562      | Model_1_5Factors         |
| CI1    | CI     |      0.641 |           |            | Model_1_5Factors         |
| CI2    | CI     |      0.752 | 0.0       | 0.091      | Model_1_5Factors         |
| CI3    | CI     |      0.663 | 0.0       | 0.095      | Model_1_5Factors         |
| CI4    | CI     |      0.741 | 0.0       | 0.094      | Model_1_5Factors         |
| CI5    | CI     |      0.767 | 0.0       | 0.093      | Model_1_5Factors         |
| CI6    | CI     |      0.689 | 0.0       | 0.096      | Model_1_5Factors         |
| CI7    | CI     |      0.71  | 0.0       | 0.093      | Model_1_5Factors         |
| CI8    | CI     |      0.793 | 0.0       | 0.092      | Model_1_5Factors         |
| HP1    | CP     |      0.718 |           |            | Model_2_4Factors_CP      |
| HP2    | CP     |      0.779 | 0.0       | 0.087      | Model_2_4Factors_CP      |
| HP3    | CP     |      0.853 | 0.0       | 0.088      | Model_2_4Factors_CP      |
| HP4_R  | CP     |      0.472 | 0.0       | 0.072      | Model_2_4Factors_CP      |
| HP5    | CP     |      0.779 | 0.0       | 0.08       | Model_2_4Factors_CP      |
| HP6_R  | CP     |      0.56  | 0.0       | 0.069      | Model_2_4Factors_CP      |
| JCP1_R | CP     |      0.306 | 0.0       | 0.066      | Model_2_4Factors_CP      |
| JCP2_R | CP     |      0.325 | 0.0       | 0.063      | Model_2_4Factors_CP      |
| JCP3_R | CP     |      0.38  | 0.0       | 0.065      | Model_2_4Factors_CP      |
| JCP4_R | CP     |      0.281 | 0.0       | 0.065      | Model_2_4Factors_CP      |
| JCP5_R | CP     |      0.158 | 0.003     | 0.06       | Model_2_4Factors_CP      |
| JCP6   | CP     |      0.004 | 0.947     | 0.066      | Model_2_4Factors_CP      |
| PP1    | PP     |      0.434 |           |            | Model_2_4Factors_CP      |
| PP2    | PP     |      0.727 | 0.0       | 0.228      | Model_2_4Factors_CP      |
| PP3    | PP     |      0.563 | 0.0       | 0.192      | Model_2_4Factors_CP      |
| PP4    | PP     |      0.649 | 0.0       | 0.179      | Model_2_4Factors_CP      |
| PP5    | PP     |      0.778 | 0.0       | 0.244      | Model_2_4Factors_CP      |
| PP6    | PP     |      0.376 | 0.0       | 0.155      | Model_2_4Factors_CP      |
| DP1    | DP     |      0.305 |           |            | Model_2_4Factors_CP      |
| DP2    | DP     |      0.8   | 0.0       | 0.52       | Model_2_4Factors_CP      |
| DP3    | DP     |      0.8   | 0.0       | 0.515      | Model_2_4Factors_CP      |
| DP4    | DP     |      0.848 | 0.0       | 0.538      | Model_2_4Factors_CP      |
| DP5    | DP     |      0.812 | 0.0       | 0.553      | Model_2_4Factors_CP      |
| CI1    | CI     |      0.641 |           |            | Model_2_4Factors_CP      |
| CI2    | CI     |      0.752 | 0.0       | 0.091      | Model_2_4Factors_CP      |
| CI3    | CI     |      0.664 | 0.0       | 0.096      | Model_2_4Factors_CP      |
| CI4    | CI     |      0.742 | 0.0       | 0.095      | Model_2_4Factors_CP      |
| CI5    | CI     |      0.766 | 0.0       | 0.093      | Model_2_4Factors_CP      |
| CI6    | CI     |      0.69  | 0.0       | 0.096      | Model_2_4Factors_CP      |
| CI7    | CI     |      0.708 | 0.0       | 0.093      | Model_2_4Factors_CP      |
| CI8    | CI     |      0.793 | 0.0       | 0.092      | Model_2_4Factors_CP      |
| HP1    | HP     |      0.697 |           |            | Model_3_4Factors_NoPP    |
| HP2    | HP     |      0.832 | 0.0       | 0.092      | Model_3_4Factors_NoPP    |
| HP3    | HP     |      0.905 | 0.0       | 0.094      | Model_3_4Factors_NoPP    |
| HP4_R  | HP     |      0.455 | 0.0       | 0.074      | Model_3_4Factors_NoPP    |
| HP5    | HP     |      0.746 | 0.0       | 0.084      | Model_3_4Factors_NoPP    |
| HP6_R  | HP     |      0.524 | 0.0       | 0.072      | Model_3_4Factors_NoPP    |
| JCP1_R | JCP    |      0.81  |           |            | Model_3_4Factors_NoPP    |
| JCP2_R | JCP    |      0.824 | 0.0       | 0.052      | Model_3_4Factors_NoPP    |
| JCP3_R | JCP    |      0.844 | 0.0       | 0.053      | Model_3_4Factors_NoPP    |
| JCP4_R | JCP    |      0.902 | 0.0       | 0.052      | Model_3_4Factors_NoPP    |
| JCP5_R | JCP    |      0.418 | 0.0       | 0.056      | Model_3_4Factors_NoPP    |
| JCP6   | JCP    |     -0.054 | 0.3       | 0.064      | Model_3_4Factors_NoPP    |
| DP1    | DP     |      0.308 |           |            | Model_3_4Factors_NoPP    |
| DP2    | DP     |      0.799 | 0.0       | 0.51       | Model_3_4Factors_NoPP    |
| DP3    | DP     |      0.802 | 0.0       | 0.506      | Model_3_4Factors_NoPP    |
| DP4    | DP     |      0.848 | 0.0       | 0.527      | Model_3_4Factors_NoPP    |
| DP5    | DP     |      0.81  | 0.0       | 0.541      | Model_3_4Factors_NoPP    |
| CI1    | CI     |      0.641 |           |            | Model_3_4Factors_NoPP    |
| CI2    | CI     |      0.751 | 0.0       | 0.091      | Model_3_4Factors_NoPP    |
| CI3    | CI     |      0.664 | 0.0       | 0.096      | Model_3_4Factors_NoPP    |
| CI4    | CI     |      0.741 | 0.0       | 0.095      | Model_3_4Factors_NoPP    |
| CI5    | CI     |      0.768 | 0.0       | 0.093      | Model_3_4Factors_NoPP    |
| CI6    | CI     |      0.688 | 0.0       | 0.096      | Model_3_4Factors_NoPP    |
| CI7    | CI     |      0.71  | 0.0       | 0.093      | Model_3_4Factors_NoPP    |
| CI8    | CI     |      0.793 | 0.0       | 0.092      | Model_3_4Factors_NoPP    |
| HP1    | CP     |      0.718 |           |            | Model_4_3Factors_CP_NoPP |
| HP2    | CP     |      0.783 | 0.0       | 0.087      | Model_4_3Factors_CP_NoPP |
| HP3    | CP     |      0.855 | 0.0       | 0.087      | Model_4_3Factors_CP_NoPP |
| HP4_R  | CP     |      0.471 | 0.0       | 0.072      | Model_4_3Factors_CP_NoPP |
| HP5    | CP     |      0.778 | 0.0       | 0.08       | Model_4_3Factors_CP_NoPP |
| HP6_R  | CP     |      0.558 | 0.0       | 0.069      | Model_4_3Factors_CP_NoPP |
| JCP1_R | CP     |      0.301 | 0.0       | 0.066      | Model_4_3Factors_CP_NoPP |
| JCP2_R | CP     |      0.321 | 0.0       | 0.063      | Model_4_3Factors_CP_NoPP |
| JCP3_R | CP     |      0.376 | 0.0       | 0.065      | Model_4_3Factors_CP_NoPP |
| JCP4_R | CP     |      0.277 | 0.0       | 0.065      | Model_4_3Factors_CP_NoPP |
| JCP5_R | CP     |      0.156 | 0.003     | 0.06       | Model_4_3Factors_CP_NoPP |
| JCP6   | CP     |      0.007 | 0.901     | 0.066      | Model_4_3Factors_CP_NoPP |
| DP1    | DP     |      0.307 |           |            | Model_4_3Factors_CP_NoPP |
| DP2    | DP     |      0.799 | 0.0       | 0.513      | Model_4_3Factors_CP_NoPP |
| DP3    | DP     |      0.802 | 0.0       | 0.51       | Model_4_3Factors_CP_NoPP |
| DP4    | DP     |      0.848 | 0.0       | 0.531      | Model_4_3Factors_CP_NoPP |
| DP5    | DP     |      0.81  | 0.0       | 0.545      | Model_4_3Factors_CP_NoPP |
| CI1    | CI     |      0.641 |           |            | Model_4_3Factors_CP_NoPP |
| CI2    | CI     |      0.752 | 0.0       | 0.091      | Model_4_3Factors_CP_NoPP |
| CI3    | CI     |      0.666 | 0.0       | 0.096      | Model_4_3Factors_CP_NoPP |
| CI4    | CI     |      0.743 | 0.0       | 0.095      | Model_4_3Factors_CP_NoPP |
| CI5    | CI     |      0.767 | 0.0       | 0.093      | Model_4_3Factors_CP_NoPP |
| CI6    | CI     |      0.689 | 0.0       | 0.096      | Model_4_3Factors_CP_NoPP |
| CI7    | CI     |      0.708 | 0.0       | 0.093      | Model_4_3Factors_CP_NoPP |
| CI8    | CI     |      0.792 | 0.0       | 0.092      | Model_4_3Factors_CP_NoPP |
| HP1    | HP     |      0.697 |           |            | Model_5_4Factors_NoDP    |
| HP2    | HP     |      0.832 | 0.0       | 0.092      | Model_5_4Factors_NoDP    |
| HP3    | HP     |      0.905 | 0.0       | 0.094      | Model_5_4Factors_NoDP    |
| HP4_R  | HP     |      0.455 | 0.0       | 0.074      | Model_5_4Factors_NoDP    |
| HP5    | HP     |      0.746 | 0.0       | 0.084      | Model_5_4Factors_NoDP    |
| HP6_R  | HP     |      0.524 | 0.0       | 0.072      | Model_5_4Factors_NoDP    |
| JCP1_R | JCP    |      0.809 |           |            | Model_5_4Factors_NoDP    |
| JCP2_R | JCP    |      0.825 | 0.0       | 0.052      | Model_5_4Factors_NoDP    |
| JCP3_R | JCP    |      0.846 | 0.0       | 0.053      | Model_5_4Factors_NoDP    |
| JCP4_R | JCP    |      0.901 | 0.0       | 0.052      | Model_5_4Factors_NoDP    |
| JCP5_R | JCP    |      0.418 | 0.0       | 0.056      | Model_5_4Factors_NoDP    |
| JCP6   | JCP    |     -0.059 | 0.256     | 0.064      | Model_5_4Factors_NoDP    |
| PP1    | PP     |      0.433 |           |            | Model_5_4Factors_NoDP    |
| PP2    | PP     |      0.736 | 0.0       | 0.231      | Model_5_4Factors_NoDP    |
| PP3    | PP     |      0.557 | 0.0       | 0.192      | Model_5_4Factors_NoDP    |
| PP4    | PP     |      0.647 | 0.0       | 0.179      | Model_5_4Factors_NoDP    |
| PP5    | PP     |      0.774 | 0.0       | 0.244      | Model_5_4Factors_NoDP    |
| PP6    | PP     |      0.376 | 0.0       | 0.156      | Model_5_4Factors_NoDP    |
| CI1    | CI     |      0.636 |           |            | Model_5_4Factors_NoDP    |
| CI2    | CI     |      0.747 | 0.0       | 0.092      | Model_5_4Factors_NoDP    |
| CI3    | CI     |      0.663 | 0.0       | 0.097      | Model_5_4Factors_NoDP    |
| CI4    | CI     |      0.739 | 0.0       | 0.096      | Model_5_4Factors_NoDP    |
| CI5    | CI     |      0.765 | 0.0       | 0.094      | Model_5_4Factors_NoDP    |
| CI6    | CI     |      0.689 | 0.0       | 0.097      | Model_5_4Factors_NoDP    |
| CI7    | CI     |      0.716 | 0.0       | 0.095      | Model_5_4Factors_NoDP    |
| CI8    | CI     |      0.799 | 0.0       | 0.093      | Model_5_4Factors_NoDP    |
| HP1    | CP     |      0.718 |           |            | Model_6_3Factors_CP_NoDP |
| HP2    | CP     |      0.78  | 0.0       | 0.087      | Model_6_3Factors_CP_NoDP |
| HP3    | CP     |      0.853 | 0.0       | 0.088      | Model_6_3Factors_CP_NoDP |
| HP4_R  | CP     |      0.472 | 0.0       | 0.072      | Model_6_3Factors_CP_NoDP |
| HP5    | CP     |      0.779 | 0.0       | 0.08       | Model_6_3Factors_CP_NoDP |
| HP6_R  | CP     |      0.56  | 0.0       | 0.069      | Model_6_3Factors_CP_NoDP |
| JCP1_R | CP     |      0.305 | 0.0       | 0.066      | Model_6_3Factors_CP_NoDP |
| JCP2_R | CP     |      0.324 | 0.0       | 0.063      | Model_6_3Factors_CP_NoDP |
| JCP3_R | CP     |      0.38  | 0.0       | 0.065      | Model_6_3Factors_CP_NoDP |
| JCP4_R | CP     |      0.28  | 0.0       | 0.065      | Model_6_3Factors_CP_NoDP |
| JCP5_R | CP     |      0.158 | 0.003     | 0.06       | Model_6_3Factors_CP_NoDP |
| JCP6   | CP     |      0.004 | 0.945     | 0.066      | Model_6_3Factors_CP_NoDP |
| PP1    | PP     |      0.432 |           |            | Model_6_3Factors_CP_NoDP |
| PP2    | PP     |      0.731 | 0.0       | 0.231      | Model_6_3Factors_CP_NoDP |
| PP3    | PP     |      0.564 | 0.0       | 0.194      | Model_6_3Factors_CP_NoDP |
| PP4    | PP     |      0.646 | 0.0       | 0.18       | Model_6_3Factors_CP_NoDP |
| PP5    | PP     |      0.777 | 0.0       | 0.246      | Model_6_3Factors_CP_NoDP |
| PP6    | PP     |      0.376 | 0.0       | 0.156      | Model_6_3Factors_CP_NoDP |
| CI1    | CI     |      0.636 |           |            | Model_6_3Factors_CP_NoDP |
| CI2    | CI     |      0.747 | 0.0       | 0.093      | Model_6_3Factors_CP_NoDP |
| CI3    | CI     |      0.664 | 0.0       | 0.097      | Model_6_3Factors_CP_NoDP |
| CI4    | CI     |      0.74  | 0.0       | 0.096      | Model_6_3Factors_CP_NoDP |
| CI5    | CI     |      0.764 | 0.0       | 0.094      | Model_6_3Factors_CP_NoDP |
| CI6    | CI     |      0.69  | 0.0       | 0.097      | Model_6_3Factors_CP_NoDP |
| CI7    | CI     |      0.715 | 0.0       | 0.095      | Model_6_3Factors_CP_NoDP |
| CI8    | CI     |      0.798 | 0.0       | 0.093      | Model_6_3Factors_CP_NoDP |

## 表 5. 收斂效度 (Convergent Validity - CR & AVE)
| Variable   |   AVE |    CR | Status   |
|:-----------|------:|------:|:---------|
| HP1        | 0.501 | 0.858 | Good     |
| HP2        | 0.651 | 0.918 | Good     |
| HP3        | 0.774 | 0.954 | Good     |
| HP4_R      | 0.215 | 0.621 | Check    |
| HP5        | 0.581 | 0.893 | Good     |
| HP6_R      | 0.294 | 0.714 | Check    |
| JCP1_R     | 0.374 | 0.748 | Check    |
| JCP2_R     | 0.392 | 0.765 | Check    |
| JCP3_R     | 0.429 | 0.797 | Check    |
| JCP4_R     | 0.446 | 0.791 | Check    |
| JCP5_R     | 0.1   | 0.356 | Check    |
| JCP6       | 0.002 | 0.004 | Check    |
| PP1        | 0.188 | 0.48  | Check    |
| PP2        | 0.535 | 0.822 | Good     |
| PP3        | 0.313 | 0.646 | Check    |
| PP4        | 0.42  | 0.743 | Check    |
| PP5        | 0.602 | 0.858 | Good     |
| PP6        | 0.142 | 0.398 | Check    |
| DP1        | 0.093 | 0.292 | Check    |
| DP2        | 0.639 | 0.876 | Good     |
| DP3        | 0.641 | 0.877 | Good     |
| DP4        | 0.72  | 0.911 | Good     |
| DP5        | 0.658 | 0.885 | Good     |
| CI1        | 0.409 | 0.806 | Check    |
| CI2        | 0.563 | 0.885 | Good     |
| CI3        | 0.441 | 0.825 | Check    |
| CI4        | 0.549 | 0.88  | Good     |
| CI5        | 0.587 | 0.895 | Good     |
| CI6        | 0.475 | 0.845 | Check    |
| CI7        | 0.506 | 0.86  | Good     |
| CI8        | 0.631 | 0.911 | Good     |

## 表 6. 多模型比較摘要 (Model Comparison Summary)
比較不同假設模型的適配度指標。
| Model                    | Description                                |   DoF |      CFI |      TLI |     RMSEA |      AIC |     BIC |
|:-------------------------|:-------------------------------------------|------:|---------:|---------:|----------:|---------:|--------:|
| Model_1_5Factors         | 原始五因子模型 (HP, JCP, PP, DP, CI)       |   424 | 0.875227 | 0.863161 | 0.0662766 | 138.159  | 425.364 |
| Model_2_4Factors_CP      | 四因子: 合併階層與工作內容停滯 (CP=HP+JCP) |   428 | 0.695949 | 0.669664 | 0.102975  | 124.8    | 396.05  |
| Model_3_4Factors_NoPP    | 四因子: 排除主動型人格 (No PP)             |   269 | 0.885064 | 0.871819 | 0.0751056 | 107.624  | 331.006 |
| Model_4_3Factors_CP_NoPP | 三因子: 合併CP且排除PP (CP, DP, CI)        |   272 | 0.684171 | 0.651659 | 0.123812  |  96.3183 | 307.733 |
| Model_5_4Factors_NoDP    | 四因子: 排除決策拖延 (No DP)               |   293 | 0.87099  | 0.8569   | 0.0732125 | 111.398  | 342.758 |
| Model_6_3Factors_CP_NoDP | 三因子: 合併CP且排除DP (CP, PP, CI)        |   296 | 0.651645 | 0.617516 | 0.119694  | 100.056  | 319.449 |

| Model                    | lval   | rval   |    Est. Std | p-value                |
|:-------------------------|:-------|:-------|------------:|:-----------------------|
| Model_5_4Factors_NoDP    | JCP6   | JCP    | -0.0593028  | 0.25604876379924857    |
| Model_1_5Factors         | JCP6   | JCP    | -0.0590201  | 0.25825913583947546    |
| Model_3_4Factors_NoPP    | JCP6   | JCP    | -0.054171   | 0.2995503827593926     |
| Model_2_4Factors_CP      | JCP6   | CP     |  0.00353423 | 0.94682576968805       |
| Model_6_3Factors_CP_NoDP | JCP6   | CP     |  0.00362651 | 0.9454350027031306     |
| Model_4_3Factors_CP_NoPP | JCP6   | CP     |  0.00657677 | 0.9011915886947488     |
| Model_4_3Factors_CP_NoPP | JCP5_R | CP     |  0.156453   | 0.0031413321453335197  |
| Model_6_3Factors_CP_NoDP | JCP5_R | CP     |  0.157705   | 0.002918120571905769   |
| Model_2_4Factors_CP      | JCP5_R | CP     |  0.15803    | 0.0028624215901869032  |
| Model_4_3Factors_CP_NoPP | JCP4_R | CP     |  0.276904   | 1.717604145579088e-07  |
| Model_6_3Factors_CP_NoDP | JCP4_R | CP     |  0.280448   | 1.2065427146268348e-07 |
| Model_2_4Factors_CP      | JCP4_R | CP     |  0.281156   | 1.1238206409913687e-07 |
| Model_4_3Factors_CP_NoPP | JCP1_R | CP     |  0.301461   | 1.2616476530169507e-08 |
| Model_1_5Factors         | DP1    | DP     |  0.302615   | -                      |
| Model_2_4Factors_CP      | DP1    | DP     |  0.304933   | -                      |
| Model_6_3Factors_CP_NoDP | JCP1_R | CP     |  0.305018   | 8.608505241980424e-09  |
| Model_2_4Factors_CP      | JCP1_R | CP     |  0.305749   | 7.950704539183562e-09  |
| Model_4_3Factors_CP_NoPP | DP1    | DP     |  0.306902   | -                      |
| Model_3_4Factors_NoPP    | DP1    | DP     |  0.307994   | -                      |
| Model_4_3Factors_CP_NoPP | JCP2_R | CP     |  0.320705   | 1.4088756827845828e-09 |
| Model_6_3Factors_CP_NoDP | JCP2_R | CP     |  0.323991   | 9.712388671090366e-10  |
| Model_2_4Factors_CP      | JCP2_R | CP     |  0.324538   | 9.1268814728096e-10    |
| Model_6_3Factors_CP_NoDP | PP6    | PP     |  0.375503   | 3.481821186923639e-08  |
| Model_2_4Factors_CP      | PP6    | PP     |  0.375927   | 3.1520752452607326e-08 |
| Model_4_3Factors_CP_NoPP | JCP3_R | CP     |  0.376055   | 1.2538858840116518e-12 |
| Model_5_4Factors_NoDP    | PP6    | PP     |  0.376496   | 3.1032116210027993e-08 |
| Model_1_5Factors         | PP6    | PP     |  0.377342   | 2.7139546165955153e-08 |
| Model_6_3Factors_CP_NoDP | JCP3_R | CP     |  0.379597   | 7.889244812986362e-13  |
| Model_2_4Factors_CP      | JCP3_R | CP     |  0.380039   | 7.44737604918555e-13   |
| Model_5_4Factors_NoDP    | JCP5_R | JCP    |  0.417813   | 0.0                    |
| Model_1_5Factors         | JCP5_R | JCP    |  0.417987   | 0.0                    |
| Model_3_4Factors_NoPP    | JCP5_R | JCP    |  0.41845    | 0.0                    |
| Model_6_3Factors_CP_NoDP | PP1    | PP     |  0.432033   | -                      |
| Model_5_4Factors_NoDP    | PP1    | PP     |  0.432966   | -                      |
| Model_2_4Factors_CP      | PP1    | PP     |  0.433682   | -                      |
| Model_1_5Factors         | PP1    | PP     |  0.434764   | -                      |
| Model_3_4Factors_NoPP    | HP4_R  | HP     |  0.454976   | 0.0                    |
| Model_1_5Factors         | HP4_R  | HP     |  0.454987   | 0.0                    |
| Model_5_4Factors_NoDP    | HP4_R  | HP     |  0.455126   | 0.0                    |
| Model_4_3Factors_CP_NoPP | HP4_R  | CP     |  0.47126    | 0.0                    |
| Model_6_3Factors_CP_NoDP | HP4_R  | CP     |  0.472188   | 0.0                    |
| Model_2_4Factors_CP      | HP4_R  | CP     |  0.472268   | 0.0                    |
| Model_1_5Factors         | HP6_R  | HP     |  0.523415   | 0.0                    |
| Model_3_4Factors_NoPP    | HP6_R  | HP     |  0.52353    | 0.0                    |
| Model_5_4Factors_NoDP    | HP6_R  | HP     |  0.523628   | 0.0                    |
| Model_1_5Factors         | PP3    | PP     |  0.555182   | 3.919309321531728e-12  |
| Model_5_4Factors_NoDP    | PP3    | PP     |  0.556933   | 4.426903288390349e-12  |
| Model_4_3Factors_CP_NoPP | HP6_R  | CP     |  0.558134   | 0.0                    |
| Model_6_3Factors_CP_NoDP | HP6_R  | CP     |  0.560154   | 0.0                    |
| Model_2_4Factors_CP      | HP6_R  | CP     |  0.56047    | 0.0                    |
| Model_2_4Factors_CP      | PP3    | PP     |  0.562788   | 3.320232977443993e-12  |
| Model_6_3Factors_CP_NoDP | PP3    | PP     |  0.564014   | 3.770983525441807e-12  |

## 📈 績效考核對職涯停滯之影響分析 (Performance Appraisal Impact)

### 1. 績效考核幫助程度 (Utility)
- **高幫助組 (High)**: 填答 4 (有幫助), 5 (非常有幫助)
- **低幫助組 (Low)**: 填答 1 (完全沒幫助) ~ 3 (普通)

| Variable   |   High Help (N=170) |   Low Help (N=201) |   Diff | p-value   |
|:-----------|--------------------:|-------------------:|-------:|:----------|
| HP         |                2.7  |               3.41 |  -0.71 | 0.000 *** |
| JCP        |                2.18 |               2.57 |  -0.39 | 0.000 *** |
| PP         |                3.63 |               3.46 |   0.17 | 0.005 **  |
| DP         |                2.72 |               2.86 |  -0.14 | 0.115     |
| CI         |                2.76 |               3.2  |  -0.44 | 0.000 *** |

> **解讀**：若 Diff 為負且顯著(*)，代表「覺得有幫助的人」該變項分數顯著較低 (例如停滯感較低)。

### 2. 是否有績效考核 (Existence)
- **有 (Yes)**: PM_Has = 1
- **無 (No)**: PM_Has = 0

| Variable   |   Yes (N=371) |   No (N=28) |   Diff |   p-value |
|:-----------|--------------:|------------:|-------:|----------:|
| HP         |          3.09 |        3.25 |  -0.16 |     0.442 |
| JCP        |          2.39 |        2.61 |  -0.22 |     0.215 |
| PP         |          3.54 |        3.73 |  -0.19 |     0.09  |
| DP         |          2.8  |        2.96 |  -0.17 |     0.403 |
| CI         |          3    |        3.1  |  -0.1  |     0.621 |

### 3. 績效考核結果性質 (Result Nature)
比較不同考核結果 (例如: 1=負面/普通, 2=正面... 需確認問卷定義) 之差異。

| Variable   |   F-value | p-value   |   Group 1 Mean |   Group 2 Mean |   Group 3 Mean |
|:-----------|----------:|:----------|---------------:|---------------:|---------------:|
| HP         |     28.49 | 0.000 *** |           4.22 |           3.35 |           2.78 |
| JCP        |      9.61 | 0.000 *** |           2.56 |           2.54 |           2.25 |
| PP         |      1.52 | 0.219     |           3.3  |           3.5  |           3.58 |
| DP         |      7.53 | 0.001 *** |           3.2  |           2.95 |           2.63 |
| CI         |     14.38 | 0.000 *** |           3.56 |           3.21 |           2.76 |

### 4. 績效考核形式 (Appraisal Forms)
比較「有採用某種形式(1)」 vs 「沒採用(0)」的差異。

#### 形式: Supervisor
| Variable   |   With Supervisor (N=349) |   No Supervisor (N=22) |   Diff |   p-value |
|:-----------|--------------------------:|-----------------------:|-------:|----------:|
| HP         |                      3.09 |                   3.11 |  -0.02 |     0.921 |
| JCP        |                      2.39 |                   2.45 |  -0.06 |     0.654 |
| PP         |                      3.54 |                   3.42 |   0.13 |     0.382 |
| DP         |                      2.79 |                   2.99 |  -0.2  |     0.279 |
| CI         |                      3    |                   2.98 |   0.01 |     0.937 |

#### 形式: Self
| Variable   |   With Self (N=277) |   No Self (N=94) |   Diff |   p-value |
|:-----------|--------------------:|-----------------:|-------:|----------:|
| HP         |                3.1  |             3.05 |   0.05 |     0.689 |
| JCP        |                2.43 |             2.3  |   0.13 |     0.108 |
| PP         |                3.52 |             3.58 |  -0.06 |     0.431 |
| DP         |                2.77 |             2.87 |  -0.1  |     0.338 |
| CI         |                2.99 |             3.03 |  -0.04 |     0.719 |

#### 形式: Interview
| Variable   |   With Interview (N=265) |   No Interview (N=106) |   Diff | p-value   |
|:-----------|-------------------------:|-----------------------:|-------:|:----------|
| HP         |                     3    |                   3.29 |  -0.29 | 0.005 **  |
| JCP        |                     2.32 |                   2.57 |  -0.25 | 0.001 **  |
| PP         |                     3.56 |                   3.48 |   0.08 | 0.255     |
| DP         |                     2.75 |                   2.92 |  -0.17 | 0.089     |
| CI         |                     2.95 |                   3.11 |  -0.15 | 0.120     |

#### 形式: Other
| Variable   |   With Other (N=0) |   No Other (N=371) |   Diff | p-value   |
|:-----------|-------------------:|-------------------:|-------:|:----------|
| HP         |                nan |               3.09 |    nan | nan       |
| JCP        |                nan |               2.39 |    nan | nan       |
| PP         |                nan |               3.54 |    nan | nan       |
| DP         |                nan |               2.8  |    nan | nan       |
| CI         |                nan |               3    |    nan | nan       |



