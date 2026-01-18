
# Model Optimization Strategy

1. **Step 1: Clean Attributes (Item Reduction)**
   - **Why?** Bad items (low loading) act like "noise". They distort the fit of *every* model. If an item doesn't measure "HP" well in a 5-factor model, it likely won't measure "HP+JCP" well in a 4-factor model either.
   - **Action:** Use Model 1 (5 factors) as the baseline. Remove items with loadings < 0.50 or 0.55 first. This clears the fog.

2. **Step 2: Model Comparison**
   - **Why?** Once the data is clean(er), the comparison between models becomes fair. You are comparing "good distinct factors" vs "good merged factors".
   - **Action:** Compare AIC/BIC/CFI of the clean models.

3. **Step 3: Fine-tuning**
   - **Why?** After picking the winner (e.g., Model 2), you might prune 1-2 more borderline items to reach perfection (CFI > 0.90).

**Summary for User:**
Yes, identifying the best model is key, but if you have "garbage items", all models will look bad.
**Recommendation:** Clean up obvious bad items using Model 1 first. Then compare models.
