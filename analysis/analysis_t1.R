# ==========================================
# R Script: T1 CFA Analysis (lavaan)
# ==========================================

# 1. Install/Load Packages
if (!require("lavaan")) install.packages("lavaan")
if (!require("semTools")) install.packages("semTools")
library(lavaan)
library(semTools)

# 2. Load Data
# Please ensure the CSV file is in your working directory
filename <- "T1_0105_377_SPSS.csv"
if (file.exists(filename)) {
  data <- read.csv(filename)
  cat("Data loaded successfully. N =", nrow(data), "\n")
} else {
  stop("CSV file not found! Please check the filename.")
}

# 3. Define Model
# Based on your structure:
# HCP (6 items), JCP (6 items), PP (6 items), DP (5 items), CI (8 items)
# Note: Ensure column names in CSV match these exactly (e.g. HCP1, HCP2...)
model <- '
  # Measurement Model
  HCP =~ HCP1 + HCP2 + HCP3 + HCP4_R + HCP5 + HCP6_R
  JCP =~ JCP1_R + JCP2_R + JCP3_R + JCP4_R + JCP5_R
  PP  =~ PP1 + PP2 + PP3 + PP4 + PP5 + PP6
  DP  =~ DP1 + DP2 + DP3 + DP4 + DP5
  CI  =~ CI1 + CI2 + CI3 + CI4 + CI5 + CI6 + CI7 + CI8
  
  # Correlated Errors (optional, if modification indices suggest)
'

# 4. Run Analysis
cat("\nRunning CFA...\n")
fit <- cfa(model, data = data, missing = "fiml") # FIML handles missing data

# 5. Output Results
summary(fit, fit.measures = TRUE, standardized = TRUE)

# Reliability (Cronbach alpha & CR)
reliability(fit)

# Factor Correlations
inspect(fit, "cor.lv")
