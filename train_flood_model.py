# =============================
# Flood Risk XGBoost Training
# =============================

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ------------------------------
# Load Data
# ------------------------------
dataset_path = "data/rainfall_flood_dataset.csv"   # Change if different name
df = pd.read_csv(dataset_path)

print("Dataset Loaded:", df.shape)
print(df.head())

# ------------------------------
# Feature Selection
# ------------------------------
feature_cols = ["rain_last_1d", "rain_last_3d", "rain_last_7d", "humidity", "wind_speed", "elevation"]
X = df[feature_cols]
y = df["flood_risk"]  # 0 = Low, 1 = Medium/High

# ------------------------------
# Train Test Split
# ------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ------------------------------
# Train XGBoost Model
# ------------------------------
model = xgb.XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="logloss"
)

print("Training Model...")
model.fit(X_train, y_train)

# ------------------------------
# Evaluation
# ------------------------------
preds = model.predict(X_test)
acc = accuracy_score(y_test, preds)

print("Accuracy:", acc)
print("\nClassification Report:\n", classification_report(y_test, preds))

# ------------------------------
# Confusion Matrix
# ------------------------------
cm = confusion_matrix(y_test, preds)
sns.heatmap(cm, annot=True, cmap="Blues", fmt="g")
plt.title("Confusion Matrix - Flood Risk")
plt.show()

# ------------------------------
# Export Model
# ------------------------------
artifact = {
    "model": model,
    "features": feature_cols
}

os.makedirs("ml", exist_ok=True)
joblib.dump(artifact, "ml/flood_xgb.joblib")

print("🔥 Model successfully saved → ml/flood_xgb.joblib")
