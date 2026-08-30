from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np
from data_loader import load_industrial_dataset

# Class merging map: combine similar categories for better generalization
CLASS_MAP = {
    "Slip/Fall": "Fall/Slip",
    "Fall": "Fall/Slip",
    "Chemical Spill": "Chemical/Gas Release",
    "Chemical": "Chemical/Gas Release",
    "Explosion": "Chemical/Gas Release",
    "Fire": "Chemical/Gas Release",
    "Burn": "Thermal/Burn",
    "Cut": "Cut/Abrasion",
    "Electrical Shock": "Electrical",
    "Electrical": "Electrical",
    "Crush": "Mechanical/Crush",
    "Manual Tools": "Manual/Mechanical",
}

# Threshold below which we flag as "Novel/Unknown" hazard
UNKNOWN_THRESHOLD = 0.35

class ClassificationEngine:
    def __init__(self):
        self.model = make_pipeline(
            TfidfVectorizer(
                max_features=3000,
                ngram_range=(1, 3),
                min_df=1,
                max_df=0.9,
                sublinear_tf=True
            ),
            LogisticRegression(
                max_iter=2000,
                C=0.5,
                class_weight="balanced",
                random_state=42
            )
        )

        # Train on expanded dataset with class merging
        dataset = load_industrial_dataset()
        X_all = [record["Description"] for record in dataset]
        y_raw = [record["Critical Risk"] for record in dataset]

        # Merge similar classes for better generalization
        y_all = [CLASS_MAP.get(label, label) for label in y_raw]

        # 80/20 train/test split for validation
        X_train, X_test, y_train, y_test = train_test_split(
            X_all, y_all, test_size=0.2, random_state=42, stratify=y_all
        )

        self.model.fit(X_train, y_train)

        # Evaluate on held-out test set
        y_pred = self.model.predict(X_test)
        self.test_accuracy = accuracy_score(y_test, y_pred)
        print(f"[classifier] Trained on {len(X_train)} reports, test accuracy: {self.test_accuracy*100:.1f}%")
        print(f"[classifier] Classes: {sorted(set(y_all))}")

        # Re-train on full data for deployment
        self.model.fit(X_all, y_all)

    def classify(self, text: str) -> str:
        """Simple classification — returns class label."""
        return self.classify_with_confidence(text)["class"]

    def classify_with_confidence(self, text: str) -> dict:
        """Classification with confidence score, per-class probabilities, and novelty detection."""
        probabilities = self.model.predict_proba([text])[0]
        classes = self.model.classes_
        max_idx = np.argmax(probabilities)
        confidence = probabilities[max_idx]
        predicted_class = classes[max_idx]

        # Build per-class breakdown
        per_class = {}
        for cls, prob in zip(classes, probabilities):
            per_class[cls] = round(float(prob) * 100, 1)

        # Sort by probability descending
        per_class_sorted = dict(sorted(per_class.items(), key=lambda x: x[1], reverse=True))

        # Novelty detection: if top prediction confidence is low, flag as novel
        is_novel = bool(confidence < UNKNOWN_THRESHOLD)
        final_class = "Novel Hazard (Low Confidence)" if is_novel else predicted_class

        return {
            "class": final_class,
            "confidence": round(float(confidence) * 100, 1),
            "per_class": per_class_sorted,
            "is_novel": bool(is_novel),
            "second_choice": classes[np.argsort(probabilities)[-2]] if len(classes) > 1 else None,
            "second_choice_confidence": round(float(np.sort(probabilities)[-2]) * 100, 1) if len(classes) > 1 else 0,
        }

    def get_metrics(self) -> dict:
        """Return training metrics for benchmark display."""
        return {
            "test_accuracy": round(self.test_accuracy * 100, 1),
            "num_classes": len(set(CLASS_MAP.values())),
            "class_mapping": CLASS_MAP,
        }


classifier = None
def get_classification_engine():
    global classifier
    if classifier is None:
        classifier = ClassificationEngine()
    return classifier
