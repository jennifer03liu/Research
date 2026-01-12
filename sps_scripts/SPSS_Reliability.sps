*** SPSS Syntax for Reliability Analysis (Cronbach's Alpha) ***.

* 1. HCP (職涯高原) - 6 items (Note: 4,6 are reversed).
RELIABILITY
  /VARIABLES=HCP1 HCP2 HCP3 HCP4_R HCP5 HCP6_R
  /SCALE('Hierarchical Career Plateau') ALL
  /MODEL=ALPHA
  /SUMMARY=TOTAL.

* 2. JCP (職務內容高原) - 6 items (Note: 1-5 are reversed).
RELIABILITY
  /VARIABLES=JCP1_R JCP2_R JCP3_R JCP4_R JCP5_R JCP6
  /SCALE('Job Content Plateau') ALL
  /MODEL=ALPHA
  /SUMMARY=TOTAL.

* 3. PP (主動性人格) - 6 items.
RELIABILITY
  /VARIABLES=PP1 PP2 PP3 PP4 PP5 PP6
  /SCALE('Proactive Personality') ALL
  /MODEL=ALPHA
  /SUMMARY=TOTAL.

* 4. DP (決策拖延) - 5 items.
RELIABILITY
  /VARIABLES=DP1 DP2 DP3 DP4 DP5
  /SCALE('Decisional Procrastination') ALL
  /MODEL=ALPHA
  /SUMMARY=TOTAL.

* 5. CI (職涯無所作為) - 8 items.
RELIABILITY
  /VARIABLES=CI1 CI2 CI3 CI4 CI5 CI6 CI7 CI8
  /SCALE('Career Inaction') ALL
  /MODEL=ALPHA
  /SUMMARY=TOTAL.
