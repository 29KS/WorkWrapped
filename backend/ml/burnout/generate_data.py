import pandas as pd
import numpy as np

np.random.seed(42)
n = 500

avg_hours = np.random.uniform(6, 13, n)
total_hours = avg_hours * np.random.randint(20, 30, n)
attendance = np.random.uniform(60, 100, n)
late_arrivals = np.random.randint(0, 15, n)
missed_checkouts = np.random.randint(0, 10, n)
idle_warning_days = np.random.randint(0, 20, n)
geo_out_of_range = np.random.randint(0, 25, n)
pending_tasks = np.random.randint(0, 30, n)
overdue_tasks = np.random.randint(0, 10, n)


def label(i):
    score = 0

    if avg_hours[i] > 10:
        score += 2
    elif avg_hours[i] > 9:
        score += 1

    if attendance[i] < 75:
        score += 2
    elif attendance[i] < 85:
        score += 1

    if late_arrivals[i] > 8:
        score += 2
    elif late_arrivals[i] > 4:
        score += 1

    if pending_tasks[i] > 15:
        score += 2
    elif pending_tasks[i] > 8:
        score += 1

    if overdue_tasks[i] > 5:
        score += 2
    elif overdue_tasks[i] > 2:
        score += 1

    if idle_warning_days[i] > 12:
        score += 1

    if missed_checkouts[i] > 5:
        score += 1

    if score >= 7:
        return "High"
    elif score >= 4:
        return "Medium"
    else:
        return "Low"


burnout = [label(i) for i in range(n)]

df = pd.DataFrame({
    "avgHours": avg_hours.round(2),
    "totalHours": total_hours.round(2),
    "attendance": attendance.round(2),
    "lateArrivals": late_arrivals,
    "missedCheckouts": missed_checkouts,
    "idleWarningDays": idle_warning_days,
    "geoOutOfRange": geo_out_of_range,
    "pendingTasks": pending_tasks,
    "overdueTasks": overdue_tasks,
    "burnout": burnout
})

df.to_csv("ml/burnout/dataset.csv", index=False)
print(f"Dataset saved — {len(df)} rows")
print(df["burnout"].value_counts())