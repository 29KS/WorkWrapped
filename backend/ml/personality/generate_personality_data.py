import pandas as pd
import numpy as np

np.random.seed(42)
n = 600

tasks_completed    = np.random.randint(10, 61, n)
avg_completion_hrs = np.random.uniform(0.5, 10, n)
attendance         = np.random.uniform(60, 100, n)
projects           = np.random.randint(1, 11, n)
avg_hours          = np.random.uniform(5, 13, n)
ontime_pct         = np.random.uniform(40, 100, n)


def label(i):
    # Speedster — finishes fast, many tasks
    if avg_completion_hrs[i] < 2.5 and tasks_completed[i] > 40:
        return "Speedster"
    # Consistency Champion — perfect attendance, high ontime
    elif attendance[i] >= 90 and ontime_pct[i] >= 85:
        return "Consistency Champion"
    # Problem Solver — high hours, many projects
    elif avg_hours[i] >= 9 and projects[i] >= 7:
        return "Problem Solver"
    # Multitasker — many projects, moderate everything
    elif projects[i] >= 6 and tasks_completed[i] >= 30:
        return "Multitasker"
    # Planner — low hours but high ontime, moderate tasks
    elif ontime_pct[i] >= 80 and avg_hours[i] < 8:
        return "Planner"
    else:
        return "Balanced Performer"


labels = [label(i) for i in range(n)]

df = pd.DataFrame({
    "tasks_completed":    tasks_completed,
    "avg_completion_hrs": avg_completion_hrs.round(2),
    "attendance":         attendance.round(2),
    "projects":           projects,
    "avg_hours":          avg_hours.round(2),
    "ontime_pct":         ontime_pct.round(2),
    "label":              labels
})

df.to_csv("ml/personality/personality_dataset.csv", index=False)
print(f"Dataset saved — {len(df)} rows")
print(df["label"].value_counts())