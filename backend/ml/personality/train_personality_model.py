import pandas as pd
import pickle
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder


# Project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# File paths
DATASET_PATH = BASE_DIR / "ml" / "personality" / "personality_dataset.csv"
MODEL_PATH = BASE_DIR / "ml" / "personality" / "personality_model.pkl"


# Load dataset
df = pd.read_csv(DATASET_PATH)

print(f"Dataset loaded: {DATASET_PATH}")
print(f"Dataset shape: {df.shape}")


# Features used for prediction
features = [
    "tasks_completed",
    "avg_completion_hrs",
    "attendance",
    "projects",
    "avg_hours",
    "ontime_pct"
]


# Prepare input and target
X = df[features]
y = df["label"]


# Encode target labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)


# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.2,
    random_state=42
)


# Create and train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)


# Evaluate model
y_pred = model.predict(X_test)

print("\nPersonality Model Evaluation:")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=le.classes_
    )
)


# Save model and label encoder
with open(MODEL_PATH, "wb") as f:
    pickle.dump(
        {
            "model": model,
            "encoder": le,
            "features": features
        },
        f
    )


print(f"\nModel saved successfully to: {MODEL_PATH}")