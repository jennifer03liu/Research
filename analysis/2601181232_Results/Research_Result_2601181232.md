# Research Analysis Report

## Table 1. Descriptive Statistics and Reliability
| Variable           |   Items |   Mean |   SD |   Alpha |
|:-------------------|--------:|-------:|-----:|--------:|
| 階層停滯 (HP)      |       6 |   3.1  | 0.92 |    0.85 |
| 工作內容停滯 (JCP) |       6 |   2.41 | 0.68 |    0.77 |
| 主動型人格 (PP)    |       6 |   3.55 | 0.6  |    0.76 |
| 決策拖延 (DP)      |       5 |   2.81 | 0.86 |    0.83 |
| 職涯無所作為 (CI)  |       8 |   3    | 0.91 |    0.9  |

## Table 2. Correlation Matrix
| Variable           | 階層停滯 (HP)   | 工作內容停滯 (JCP)   | 主動型人格 (PP)   | 決策拖延 (DP)   | 職涯無所作為 (CI)   |
|:-------------------|:----------------|:---------------------|:------------------|:----------------|:--------------------|
| 階層停滯 (HP)      | 1.00            | 0.23***              | -0.13*            | 0.15**          | 0.39***             |
| 工作內容停滯 (JCP) | 0.23***         | 1.00                 | -0.11*            | -0.01           | 0.19***             |
| 主動型人格 (PP)    | -0.13*          | -0.11*               | 1.00              | -0.19***        | -0.21***            |
| 決策拖延 (DP)      | 0.15**          | -0.01                | -0.19***          | 1.00            | 0.42***             |
| 職涯無所作為 (CI)  | 0.39***         | 0.19***              | -0.21***          | 0.42***         | 1.00                |

## Table 3. Model Fit Indices
|   DoF |   DoF Baseline |     chi2 |   chi2 p-value |   chi2 Baseline |      CFI |      GFI |     AGFI |      NFI |      TLI |     RMSEA |     AIC |     BIC |   LogLik | Model                    | Description                              |
|------:|---------------:|---------:|---------------:|----------------:|---------:|---------:|---------:|---------:|---------:|----------:|--------:|--------:|---------:|:-------------------------|:-----------------------------------------|
|   424 |            465 | 1149.86  |              0 |         6327.46 | 0.876186 | 0.818275 | 0.800703 | 0.818275 | 0.864213 | 0.0660003 | 138.163 | 424.46  |  2.91842 | Model_1_5Factors         | Original 5 Factors (HP, JCP, PP, DP, CI) |
|   428 |            465 | 2211.78  |              0 |         6327.46 | 0.695728 | 0.650447 | 0.620229 | 0.650447 | 0.669424 | 0.10298   | 124.773 | 395.165 |  5.61366 | Model_2_4Factors_CP      | 4 Factors: CP(HP+JCP), PP, DP, CI        |
|   269 |            300 |  860.908 |              0 |         5480.68 | 0.885747 | 0.842919 | 0.824817 | 0.842919 | 0.87258  | 0.0748264 | 107.63  | 330.306 |  2.18505 | Model_3_4Factors_NoPP    | 4 Factors: HP, JCP, DP, CI (Exclude PP)  |
|   272 |            300 | 1911.89  |              0 |         5480.68 | 0.68346  | 0.651158 | 0.615248 | 0.651158 | 0.650875 | 0.123859  |  96.295 | 307.042 |  4.85252 | Model_4_3Factors_CP_NoPP | 3 Factors: CP, DP, CI (Exclude PP)       |
|   293 |            325 |  908.663 |              0 |         5104.54 | 0.871188 | 0.821989 | 0.802548 | 0.821989 | 0.85712  | 0.0731209 | 111.387 | 342.016 |  2.30625 | Model_5_4Factors_NoDP    | 4 Factors: HP, JCP, PP, CI (Exclude DP)  |
|   296 |            325 | 1966.97  |              0 |         5104.54 | 0.650391 | 0.614663 | 0.57691  | 0.614663 | 0.616139 | 0.119851  | 100.015 | 318.715 |  4.99231 | Model_6_3Factors_CP_NoDP | 3 Factors: CP, PP, CI (Exclude DP)       |

## Table 4. Factor Loadings (Standardized)
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
| JCP4_R | JCP    |      0.904 | 0.0       | 0.052      | Model_1_5Factors         |
| JCP5_R | JCP    |      0.416 | 0.0       | 0.057      | Model_1_5Factors         |
| JCP6   | JCP    |     -0.063 | 0.23      | 0.065      | Model_1_5Factors         |
| PP1    | PP     |      0.434 |           |            | Model_1_5Factors         |
| PP2    | PP     |      0.733 | 0.0       | 0.23       | Model_1_5Factors         |
| PP3    | PP     |      0.556 | 0.0       | 0.191      | Model_1_5Factors         |
| PP4    | PP     |      0.65  | 0.0       | 0.179      | Model_1_5Factors         |
| PP5    | PP     |      0.778 | 0.0       | 0.244      | Model_1_5Factors         |
| PP6    | PP     |      0.386 | 0.0       | 0.157      | Model_1_5Factors         |
| DP1    | DP     |      0.305 |           |            | Model_1_5Factors         |
| DP2    | DP     |      0.803 | 0.0       | 0.524      | Model_1_5Factors         |
| DP3    | DP     |      0.803 | 0.0       | 0.518      | Model_1_5Factors         |
| DP4    | DP     |      0.847 | 0.0       | 0.54       | Model_1_5Factors         |
| DP5    | DP     |      0.811 | 0.0       | 0.554      | Model_1_5Factors         |
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
| JCP6   | CP     |     -0.005 | 0.921     | 0.067      | Model_2_4Factors_CP      |
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
| JCP2_R | JCP    |      0.823 | 0.0       | 0.052      | Model_3_4Factors_NoPP    |
| JCP3_R | JCP    |      0.843 | 0.0       | 0.054      | Model_3_4Factors_NoPP    |
| JCP4_R | JCP    |      0.904 | 0.0       | 0.052      | Model_3_4Factors_NoPP    |
| JCP5_R | JCP    |      0.416 | 0.0       | 0.057      | Model_3_4Factors_NoPP    |
| JCP6   | JCP    |     -0.058 | 0.268     | 0.065      | Model_3_4Factors_NoPP    |
| DP1    | DP     |      0.308 |           |            | Model_3_4Factors_NoPP    |
| DP2    | DP     |      0.802 | 0.0       | 0.516      | Model_3_4Factors_NoPP    |
| DP3    | DP     |      0.805 | 0.0       | 0.513      | Model_3_4Factors_NoPP    |
| DP4    | DP     |      0.847 | 0.0       | 0.533      | Model_3_4Factors_NoPP    |
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
| JCP6   | CP     |     -0.002 | 0.963     | 0.067      | Model_4_3Factors_CP_NoPP |
| DP1    | DP     |      0.306 |           |            | Model_4_3Factors_CP_NoPP |
| DP2    | DP     |      0.802 | 0.0       | 0.52       | Model_4_3Factors_CP_NoPP |
| DP3    | DP     |      0.805 | 0.0       | 0.516      | Model_4_3Factors_CP_NoPP |
| DP4    | DP     |      0.847 | 0.0       | 0.537      | Model_4_3Factors_CP_NoPP |
| DP5    | DP     |      0.809 | 0.0       | 0.55       | Model_4_3Factors_CP_NoPP |
| CI1    | CI     |      0.641 |           |            | Model_4_3Factors_CP_NoPP |
| CI2    | CI     |      0.751 | 0.0       | 0.092      | Model_4_3Factors_CP_NoPP |
| CI3    | CI     |      0.667 | 0.0       | 0.096      | Model_4_3Factors_CP_NoPP |
| CI4    | CI     |      0.743 | 0.0       | 0.095      | Model_4_3Factors_CP_NoPP |
| CI5    | CI     |      0.769 | 0.0       | 0.093      | Model_4_3Factors_CP_NoPP |
| CI6    | CI     |      0.692 | 0.0       | 0.096      | Model_4_3Factors_CP_NoPP |
| CI7    | CI     |      0.711 | 0.0       | 0.094      | Model_4_3Factors_CP_NoPP |
| CI8    | CI     |      0.793 | 0.0       | 0.092      | Model_4_3Factors_CP_NoPP |
| HP1    | HP     |      0.695 |           |            | Model_5_4Factors_NoDP    |
| HP2    | HP     |      0.829 | 0.0       | 0.093      | Model_5_4Factors_NoDP    |
| HP3    | HP     |      0.903 | 0.0       | 0.095      | Model_5_4Factors_NoDP    |
| HP4_R  | HP     |      0.447 | 0.0       | 0.075      | Model_5_4Factors_NoDP    |
| HP5    | HP     |      0.742 | 0.0       | 0.085      | Model_5_4Factors_NoDP    |
| HP6_R  | HP     |      0.519 | 0.0       | 0.072      | Model_5_4Factors_NoDP    |
| JCP1_R | JCP    |      0.811 |           |            | Model_5_4Factors_NoDP    |
| JCP2_R | JCP    |      0.823 | 0.0       | 0.052      | Model_5_4Factors_NoDP    |
| JCP3_R | JCP    |      0.844 | 0.0       | 0.054      | Model_5_4Factors_NoDP    |
| JCP4_R | JCP    |      0.903 | 0.0       | 0.052      | Model_5_4Factors_NoDP    |
| JCP5_R | JCP    |      0.416 | 0.0       | 0.057      | Model_5_4Factors_NoDP    |
| JCP6   | JCP    |     -0.063 | 0.228     | 0.065      | Model_5_4Factors_NoDP    |
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
| HP5    | CP     |      0.776 | 0.0       | 0.081      | Model_6_3Factors_CP_NoDP |
| HP6_R  | CP     |      0.555 | 0.0       | 0.07       | Model_6_3Factors_CP_NoDP |
| JCP1_R | CP     |      0.294 | 0.0       | 0.066      | Model_6_3Factors_CP_NoDP |
| JCP2_R | CP     |      0.319 | 0.0       | 0.064      | Model_6_3Factors_CP_NoDP |
| JCP3_R | CP     |      0.376 | 0.0       | 0.066      | Model_6_3Factors_CP_NoDP |
| JCP4_R | CP     |      0.277 | 0.0       | 0.066      | Model_6_3Factors_CP_NoDP |
| JCP5_R | CP     |      0.148 | 0.006     | 0.06       | Model_6_3Factors_CP_NoDP |
| JCP6   | CP     |     -0.005 | 0.921     | 0.067      | Model_6_3Factors_CP_NoDP |
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

## Table 5. Convergent Validity (CR & AVE)
| Variable   |   AVE |    CR | Status   |
|:-----------|------:|------:|:---------|
| HP1        | 0.498 | 0.856 | Check    |
| HP2        | 0.647 | 0.916 | Good     |
| HP3        | 0.771 | 0.953 | Good     |
| HP4_R      | 0.208 | 0.611 | Check    |
| HP5        | 0.575 | 0.89  | Good     |
| HP6_R      | 0.288 | 0.708 | Check    |
| JCP1_R     | 0.372 | 0.745 | Check    |
| JCP2_R     | 0.389 | 0.762 | Check    |
| JCP3_R     | 0.426 | 0.795 | Check    |
| JCP4_R     | 0.446 | 0.79  | Check    |
| JCP5_R     | 0.097 | 0.346 | Check    |
| JCP6       | 0.002 | 0.006 | Check    |
| PP1        | 0.187 | 0.479 | Check    |
| PP2        | 0.536 | 0.822 | Good     |
| PP3        | 0.314 | 0.647 | Check    |
| PP4        | 0.419 | 0.742 | Check    |
| PP5        | 0.607 | 0.861 | Good     |
| PP6        | 0.149 | 0.411 | Check    |
| DP1        | 0.094 | 0.292 | Check    |
| DP2        | 0.644 | 0.878 | Good     |
| DP3        | 0.646 | 0.88  | Good     |
| DP4        | 0.718 | 0.91  | Good     |
| DP5        | 0.656 | 0.884 | Good     |
| CI1        | 0.409 | 0.806 | Check    |
| CI2        | 0.562 | 0.885 | Good     |
| CI3        | 0.442 | 0.826 | Check    |
| CI4        | 0.549 | 0.88  | Good     |
| CI5        | 0.59  | 0.896 | Good     |
| CI6        | 0.478 | 0.846 | Check    |
| CI7        | 0.51  | 0.862 | Good     |
| CI8        | 0.633 | 0.912 | Good     |

## Table 6. Model Comparison Summary
Comparison of alternative models metrics.
| Model                    | Description                              |   DoF |      CFI |      TLI |     RMSEA |     AIC |     BIC |
|:-------------------------|:-----------------------------------------|------:|---------:|---------:|----------:|--------:|--------:|
| Model_1_5Factors         | Original 5 Factors (HP, JCP, PP, DP, CI) |   424 | 0.876186 | 0.864213 | 0.0660003 | 138.163 | 424.46  |
| Model_2_4Factors_CP      | 4 Factors: CP(HP+JCP), PP, DP, CI        |   428 | 0.695728 | 0.669424 | 0.10298   | 124.773 | 395.165 |
| Model_3_4Factors_NoPP    | 4 Factors: HP, JCP, DP, CI (Exclude PP)  |   269 | 0.885747 | 0.87258  | 0.0748264 | 107.63  | 330.306 |
| Model_4_3Factors_CP_NoPP | 3 Factors: CP, DP, CI (Exclude PP)       |   272 | 0.68346  | 0.650875 | 0.123859  |  96.295 | 307.042 |
| Model_5_4Factors_NoDP    | 4 Factors: HP, JCP, PP, CI (Exclude DP)  |   293 | 0.871188 | 0.85712  | 0.0731209 | 111.387 | 342.016 |
| Model_6_3Factors_CP_NoDP | 3 Factors: CP, PP, CI (Exclude DP)       |   296 | 0.650391 | 0.616139 | 0.119851  | 100.015 | 318.715 |

## 🚀 Optimization Suggestions
The following items have low factor loadings (< 0.60) and may benefit from removal to improve Model Fit (CFI).
| Model                    | lval   | rval   |    Est. Std | p-value                |
|:-------------------------|:-------|:-------|------------:|:-----------------------|
| Model_5_4Factors_NoDP    | JCP6   | JCP    | -0.0633255  | 0.22796649317168227    |
| Model_1_5Factors         | JCP6   | JCP    | -0.0631021  | 0.22954826646629511    |
| Model_3_4Factors_NoPP    | JCP6   | JCP    | -0.0581397  | 0.26838089213773353    |
| Model_2_4Factors_CP      | JCP6   | CP     | -0.00530483 | 0.9208356718012716     |
| Model_6_3Factors_CP_NoDP | JCP6   | CP     | -0.00529188 | 0.9210240833066392     |
| Model_4_3Factors_CP_NoPP | JCP6   | CP     | -0.00246545 | 0.96314843979255       |
| Model_4_3Factors_CP_NoPP | JCP5_R | CP     |  0.146672   | 0.005990438510933949   |
| Model_2_4Factors_CP      | JCP5_R | CP     |  0.148177   | 0.005510211683048327   |
| Model_6_3Factors_CP_NoDP | JCP5_R | CP     |  0.148198   | 0.005500870769857391   |
| Model_4_3Factors_CP_NoPP | JCP4_R | CP     |  0.273124   | 3.1199667960279953e-07 |
| Model_6_3Factors_CP_NoDP | JCP4_R | CP     |  0.276878   | 2.1621546020256233e-07 |
| Model_2_4Factors_CP      | JCP4_R | CP     |  0.277075   | 2.1238264391598705e-07 |
| Model_4_3Factors_CP_NoPP | JCP1_R | CP     |  0.290293   | 5.408984149468665e-08  |
| Model_6_3Factors_CP_NoDP | JCP1_R | CP     |  0.29409    | 3.654532099162111e-08  |
| Model_2_4Factors_CP      | JCP1_R | CP     |  0.29433    | 3.570415563203255e-08  |
| Model_2_4Factors_CP      | DP1    | DP     |  0.304352   | -                      |
| Model_1_5Factors         | DP1    | DP     |  0.305444   | -                      |
| Model_4_3Factors_CP_NoPP | DP1    | DP     |  0.306437   | -                      |
| Model_3_4Factors_NoPP    | DP1    | DP     |  0.307511   | -                      |
| Model_4_3Factors_CP_NoPP | JCP2_R | CP     |  0.315628   | 3.3952070044307447e-09 |
| Model_6_3Factors_CP_NoDP | JCP2_R | CP     |  0.319111   | 2.3057582509977692e-09 |
| Model_2_4Factors_CP      | JCP2_R | CP     |  0.319219   | 2.283313538242737e-09  |
| Model_4_3Factors_CP_NoPP | JCP3_R | CP     |  0.372232   | 3.1812330547609236e-12 |
| Model_6_3Factors_CP_NoDP | JCP3_R | CP     |  0.375956   | 1.964428619771752e-12  |
| Model_2_4Factors_CP      | JCP3_R | CP     |  0.375967   | 1.9693136010801027e-12 |
| Model_6_3Factors_CP_NoDP | PP6    | PP     |  0.384896   | 2.5676660131424e-08    |
| Model_2_4Factors_CP      | PP6    | PP     |  0.385011   | 2.3711247187918616e-08 |
| Model_5_4Factors_NoDP    | PP6    | PP     |  0.386006   | 2.2762716822555262e-08 |
| Model_1_5Factors         | PP6    | PP     |  0.386251   | 2.0380756193816296e-08 |
| Model_1_5Factors         | JCP5_R | JCP    |  0.415896   | 2.220446049250313e-16  |
| Model_5_4Factors_NoDP    | JCP5_R | JCP    |  0.415966   | 2.220446049250313e-16  |
| Model_3_4Factors_NoPP    | JCP5_R | JCP    |  0.416379   | 2.220446049250313e-16  |
| Model_6_3Factors_CP_NoDP | PP1    | PP     |  0.430884   | -                      |
| Model_5_4Factors_NoDP    | PP1    | PP     |  0.431723   | -                      |
| Model_2_4Factors_CP      | PP1    | PP     |  0.43232    | -                      |
| Model_1_5Factors         | PP1    | PP     |  0.433664   | -                      |
| Model_1_5Factors         | HP4_R  | HP     |  0.447008   | 0.0                    |
| Model_3_4Factors_NoPP    | HP4_R  | HP     |  0.447102   | 0.0                    |
| Model_5_4Factors_NoDP    | HP4_R  | HP     |  0.447257   | 0.0                    |
| Model_4_3Factors_CP_NoPP | HP4_R  | CP     |  0.463298   | 0.0                    |
| Model_2_4Factors_CP      | HP4_R  | CP     |  0.464298   | 0.0                    |
| Model_6_3Factors_CP_NoDP | HP4_R  | CP     |  0.464349   | 0.0                    |
| Model_1_5Factors         | HP6_R  | HP     |  0.518588   | 0.0                    |
| Model_3_4Factors_NoPP    | HP6_R  | HP     |  0.518824   | 0.0                    |
| Model_5_4Factors_NoDP    | HP6_R  | HP     |  0.518977   | 0.0                    |
| Model_4_3Factors_CP_NoPP | HP6_R  | CP     |  0.553155   | 0.0                    |
| Model_6_3Factors_CP_NoDP | HP6_R  | CP     |  0.555343   | 0.0                    |
| Model_2_4Factors_CP      | HP6_R  | CP     |  0.555457   | 0.0                    |
| Model_1_5Factors         | PP3    | PP     |  0.556115   | 5.331513008854927e-12  |
| Model_5_4Factors_NoDP    | PP3    | PP     |  0.557805   | 6.120437490153563e-12  |
| Model_2_4Factors_CP      | PP3    | PP     |  0.563603   | 4.669153952363558e-12  |
| Model_6_3Factors_CP_NoDP | PP3    | PP     |  0.564677   | 5.24824628200804e-12   |

