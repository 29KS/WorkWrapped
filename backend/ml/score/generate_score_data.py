import pandas as pd
import numpy as np

np.random.seed(0)
n = 500

attendance = np.random.uniform(60, 100, n)
completion = np.random.uniform(40, 100, n)
projects = np.random.randint(1, 10, n)
hours = np.random.uniform(5, 13, n)
late_arrivals = np.random.randint(0, 15, n)

# score formula — weighted combination with some noise
score = (
    attendance * 0.25 +
    completion * 0.35 +
    projects * 2.0 +
    hours * 1.5 -
    late_arrivals * 1.2 +
    np.random.normal(0, 3, n)
)
score = np.clip(score, 0, 100).round(2)

df = pd.DataFrame({
    "attendance": attendance.round(2),
    "completion": completion.round(2),
    "projects": projects,
    "hours": hours.round(2),
    "late_arrivals": late_arrivals,
    "score": score
})

df.to_csv("ml/score/score_dataset.csv", index=False)
print(f"Score dataset saved — {len(df)} rows")
print(df.describe())