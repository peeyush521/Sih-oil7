from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from data_loader import load_industrial_dataset

class ClassificationEngine:
    def __init__(self):
        self.model = make_pipeline(TfidfVectorizer(), LogisticRegression())
        
        # Train on the realistic IHM Stefanini dataset simulation
        dataset = load_industrial_dataset()
        X_train = [record["Description"] for record in dataset]
        
        # We'll predict the Critical Risk Category
        y_train = [record["Critical Risk"] for record in dataset]
        
        # Ensure at least 2 classes for LogisticRegression to work
        if len(set(y_train)) < 2:
            X_train.append("Dummy text to prevent crash")
            y_train.append("Other Risk")
            
        self.model.fit(X_train, y_train)
        
    def classify(self, text: str) -> str:
        return self.model.predict([text])[0]

classifier = None
def get_classification_engine():
    global classifier
    if classifier is None:
        classifier = ClassificationEngine()
    return classifier
