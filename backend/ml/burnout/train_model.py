import os
import pandas as pd
import pickle

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder


# Get project root directory
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

# File paths
DATASET_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "burnout",
    "dataset.csv"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "burnout",
    "burnout_model.pkl"
)


# Load dataset
df = pd.read_csv(DATASET_PATH)

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


# Encode target labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)


# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.2,
    random_state=42
)


# Train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)


# Evaluate
y_pred = model.predict(X_test)

print(
    classification_report(
        y_test,
        y_pred,
        target_names=le.classes_
    )
)


# Save model + encoder
with open(MODEL_PATH, "wb") as f:
    pickle.dump(
        {
            "model": model,
            "encoder": le,
            "features": features
        },
        f
    )

print(f"Model saved to: {MODEL_PATH}")