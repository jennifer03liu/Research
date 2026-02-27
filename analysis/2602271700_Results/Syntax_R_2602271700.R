# R Syntax using lavaan package
library(lavaan)

# 1. Load Data
data <- read.csv('T1_data.csv')

# 2. Define Model
model <- '
  HP =~ HP1 + HP2 + HP3 + HP4_R + HP5 + HP6_R
  JCP =~ JCP1_R + JCP2_R + JCP3_R + JCP4_R + JCP5_R
  PP =~ PP1 + PP2 + PP3 + PP4 + PP5 + PP6
  DP =~ DP1 + DP2 + DP3 + DP4 + DP5
  CI =~ CI1 + CI2 + CI3 + CI4 + CI5 + CI6 + CI7 + CI8
'

# 3. Fit Model
fit <- cfa(model, data=data)

# 4. Summary & Fit Indices
summary(fit, fit.measures=TRUE, standardized=TRUE)
fitMeasures(fit, c('cfi', 'tli', 'rmsea', 'srmr'))
