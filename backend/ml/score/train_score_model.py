import pandas as pd
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

df = pd.read_csv("ml/score/score_dataset.csv")

features = ["attendance", "completion", "projects", "hours", "late_arrivals"]
X = df[features]
y = df["score"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# train both and pick better one
lr = LinearRegression()
lr.fit(X_train, y_train)
lr_mae = mean_absolute_error(y_test, lr.predict(X_test))
lr_r2 = r2_score(y_test, lr.predict(X_test))

rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
rf_mae = mean_absolute_error(y_test, rf.predict(X_test))
rf_r2 = r2_score(y_test, rf.predict(X_test))

print(f"Linear Regression — MAE: {lr_mae:.2f}, R2: {lr_r2:.3f}")
print(f"Random Forest     — MAE: {rf_mae:.2f}, R2: {rf_r2:.3f}")

# use whichever has better R2
best_model = rf if rf_r2 >= lr_r2 else lr
best_name = "Random Forest" if rf_r2 >= lr_r2 else "Linear Regression"
print(f"\nSaving: {best_name}")

with open("ml/score/score_model.pkl", "wb") as f:
    pickle.dump({
        "model": best_model,
        "features": features,
        "model_name": best_name
    }, f)

print("Model saved to ml/score_model.pkl")