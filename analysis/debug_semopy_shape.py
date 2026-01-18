
import semopy
import pandas as pd
import numpy as np

# Create dummy data
data = pd.DataFrame(np.random.randn(100, 3), columns=['A', 'B', 'C'])
desc = "A =~ B + C"
model = semopy.Model(desc)
model.fit(data)

stats = semopy.calc_stats(model)
print("Type:", type(stats))
print("Shape:", stats.shape)
print("Columns:", stats.columns if hasattr(stats, 'columns') else "No columns")
print("Index:", stats.index)

print("\n--- transposed ---")
stats_t = stats.T
print("Transposed Shape:", stats_t.shape)
