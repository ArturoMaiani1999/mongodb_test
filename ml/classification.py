# ml/classification.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from tqdm import trange
import joblib
import matplotlib.pyplot as plt
import numpy as np

# --------------------
# Load features
# --------------------
df = pd.read_csv("data/derived/students_features.csv")

# Create binary target: high performer vs low performer
df['high_performer'] = df['avg_grade'] > df['avg_grade'].median()

# Select features
X = df[['fullTime', 'max_grade', 'num_courses']].copy()
X['fullTime'] = X['fullTime'].astype(int)  # convert bool to int
y = df['high_performer']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# --------------------
# Random Forest setup
# --------------------
n_estimators = 100
clf = RandomForestClassifier(
    n_estimators=1,         # start with 1 tree
    warm_start=True,        # allow incremental training
    random_state=42,
    n_jobs=-1
)

# --------------------
# Training with progress bar
# --------------------
pbar = trange(1, n_estimators + 1, desc="Training trees")
for i in pbar:
    clf.n_estimators = i
    clf.fit(X_train, y_train)

    # Print metrics every 10 trees
    if i % 10 == 0:
        y_pred = clf.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        pbar.write(f"[{i} trees] Accuracy: {acc:.4f}, F1: {f1:.4f}")

# --------------------
# Save trained model
# --------------------
joblib.dump(clf, "ml/random_forest_students.pkl")
print("Training complete, model saved as ml/random_forest_students.pkl")

# --------------------
# Feature importance plot
# --------------------
importances = clf.feature_importances_
features = X.columns
indices = np.argsort(importances)[::-1]

plt.figure(figsize=(6,4))
plt.title("Feature Importances")
plt.bar(range(len(importances)), importances[indices], color='skyblue')
plt.xticks(range(len(importances)), [features[i] for i in indices])
plt.ylabel("Importance")
plt.tight_layout()
plt.show()
