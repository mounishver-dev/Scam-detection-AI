import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import pickle

print("Scam Detection ML Training Started")

def load_csv(path):
    try:
        return pd.read_csv(path, encoding="utf-8")
    except:
        return pd.read_csv(path, encoding="latin-1")

data1 = load_csv("../data/spam.csv")
data2 = load_csv("../data/emails.csv")

data = pd.concat([data1, data2], ignore_index=True)

print("Dataset loaded successfully")
print("Total samples:", len(data))

if "text" in data.columns and "label" in data.columns:
    X = data["text"]
    y = data["label"]
elif "v1" in data.columns and "v2" in data.columns:
    X = data["v2"]
    y = data["v1"]
else:
    X = data.iloc[:, 1]
    y = data.iloc[:, 0]

y = y.str.lower().map({
    "spam": 1,
    "scam": 1,
    "fraud": 1,
    "ham": 0,
    "safe": 0,
    "normal": 0
})

X = X.astype(str)

vectorizer = TfidfVectorizer(
    ngram_range=(1, 3),
    max_features=12000,
    token_pattern=r"\b\w+\b"
)

X_vec = vectorizer.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_vec, y, test_size=0.2, random_state=42, stratify=y
)

model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced"
)

model.fit(X_train, y_train)

pred = model.predict(X_test)
accuracy = accuracy_score(y_test, pred)

print("\nModel Accuracy:", round(accuracy * 100, 2), "%")
print("\nClassification Report:\n", classification_report(y_test, pred))

pickle.dump(model, open("spam_model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("\nML Model Trained and Saved Successfully")
