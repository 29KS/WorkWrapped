import os
import pandas as pd
import pickle

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.join(BASE_DIR, "dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "burnout_model.pkl")


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

df = pd.read_csv(DATASET_PATH)


# --------------------------------------------------
# Features
# --------------------------------------------------

features = [
    "avgHours",
    "totalHours",
    "attendance",
    "lateArrivals",
    "missedCheckouts",
    "idleWarningDays",
    "geoOutOfRange",
    "pendingTasks",
    "overdueTasks"
]

X = df[features]
y = df["burnout"]


# --------------------------------------------------
# Encode target labels
# --------------------------------------------------

encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)


# --------------------------------------------------
# Train/Test Split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.2,
    random_state=42,
    stratify=y_encoded
)


# --------------------------------------------------
# Train Random Forest
# --------------------------------------------------

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)


# --------------------------------------------------
# Evaluation
# --------------------------------------------------

y_pred = model.predict(X_test)

print("\nBurnout Model Evaluation:")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=encoder.classes_
    )
)


# --------------------------------------------------
# Save model + encoder
# --------------------------------------------------

with open(MODEL_PATH, "wb") as f:
    pickle.dump(
        {
            "model": model,
            "encoder": encoder,
            "features": features
        },
        f
    )


print(f"\nModel saved successfully to:")
print(MODEL_PATH)