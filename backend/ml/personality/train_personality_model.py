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

DATASET_PATH = os.path.join(
    BASE_DIR,
    "personality_dataset.csv"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "personality_model.pkl"
)


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

df = pd.read_csv(DATASET_PATH)


# --------------------------------------------------
# Features
# --------------------------------------------------

features = [
    "tasks_completed",
    "avg_completion_hrs",
    "attendance",
    "projects",
    "avg_hours",
    "ontime_pct"
]

X = df[features]
y = df["label"]


# --------------------------------------------------
# Encode labels
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
# Train model
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

print("\nPersonality Model Evaluation:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=encoder.classes_
    )
)


# --------------------------------------------------
# Save model
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


print("\nModel saved successfully to:")
print(MODEL_PATH)