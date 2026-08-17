import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder

df = pd.read_csv("ml/personality/personality_dataset.csv")

features = [
    "tasks_completed", "avg_completion_hrs",
    "attendance", "projects", "avg_hours", "ontime_pct"
]

X = df[features]
y = df["label"]

le = LabelEncoder()
y_encoded = le.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, target_names=le.classes_))

with open("ml/personality/personality_model.pkl", "wb") as f:
    pickle.dump({"model": model, "encoder": le}, f)

print("Model saved to ml/personality/personality_model.pkl")