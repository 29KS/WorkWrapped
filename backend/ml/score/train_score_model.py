import os
import pandas as pd
import pickle

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.join(
    BASE_DIR,
    "score_dataset.csv"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "score_model.pkl"
)


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

df = pd.read_csv(DATASET_PATH)


# --------------------------------------------------
# Features
# --------------------------------------------------

features = [
    "attendance",
    "completion",
    "projects",
    "hours",
    "late_arrivals"
]

X = df[features]
y = df["score"]


# --------------------------------------------------
# Train/Test Split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# --------------------------------------------------
# Linear Regression
# --------------------------------------------------

lr = LinearRegression()

lr.fit(X_train, y_train)

lr_predictions = lr.predict(X_test)

lr_mae = mean_absolute_error(
    y_test,
    lr_predictions
)

lr_r2 = r2_score(
    y_test,
    lr_predictions
)


# --------------------------------------------------
# Random Forest
# --------------------------------------------------

rf = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

rf.fit(X_train, y_train)

rf_predictions = rf.predict(X_test)

rf_mae = mean_absolute_error(
    y_test,
    rf_predictions
)

rf_r2 = r2_score(
    y_test,
    rf_predictions
)


# --------------------------------------------------
# Evaluation
# --------------------------------------------------

print("\nScore Model Evaluation:")

print(
    f"Linear Regression - "
    f"MAE: {lr_mae:.2f}, "
    f"R2: {lr_r2:.3f}"
)

print(
    f"Random Forest     - "
    f"MAE: {rf_mae:.2f}, "
    f"R2: {rf_r2:.3f}"
)


# --------------------------------------------------
# Select best model
# --------------------------------------------------

if rf_r2 >= lr_r2:
    best_model = rf
    best_name = "Random Forest"
else:
    best_model = lr
    best_name = "Linear Regression"


print(f"\nSelected model: {best_name}")


# --------------------------------------------------
# Save model
# --------------------------------------------------

with open(MODEL_PATH, "wb") as f:
    pickle.dump(
        {
            "model": best_model,
            "features": features,
            "model_name": best_name
        },
        f
    )


print("\nModel saved successfully to:")
print(MODEL_PATH)