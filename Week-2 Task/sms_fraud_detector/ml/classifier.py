"""
ml/classifier.py
-----------------
The core Machine Learning component of the application.

Pipeline:
    Raw SMS text
        -> preprocessor.clean_text()      (cleaning)
        -> TfidfVectorizer                 (turns text into numeric features)
        -> MultinomialNB                   (Naive Bayes classification)
        -> "spam" or "ham" + confidence %

Naive Bayes is a classic, well-understood algorithm for text
classification and is the standard textbook choice for SMS spam
detection, which is why it was chosen here over a more complex model.
"""

import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

import config
from ml.preprocessor import clean_text, extract_keywords


class SpamClassifier:
    """Wraps a TF-IDF vectorizer + Multinomial Naive Bayes model."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.model = MultinomialNB()
        self.is_trained = False
        self.accuracy = 0.0

    # ------------------------------------------------------------------
    # TRAINING
    # ------------------------------------------------------------------
    def train(self, database):
        """
        Train the classifier on every labeled message currently stored
        in the database's sms_messages table.

        The dataset is split into a training set and a held-out test
        set so we can honestly report how accurate the model is, rather
        than just measuring how well it memorized its own training data.
        """
        dataframe = database.get_training_dataframe()

        if dataframe.empty or dataframe["label"].nunique() < 2:
            # Not enough data to train a meaningful model yet.
            self.is_trained = False
            self.accuracy = 0.0
            return self.accuracy

        # Clean every message before vectorizing.
        cleaned_messages = dataframe["message_text"].apply(clean_text)
        labels = dataframe["label"]

        x_train, x_test, y_train, y_test = train_test_split(
            cleaned_messages,
            labels,
            test_size=config.TEST_SIZE,
            random_state=config.RANDOM_STATE,
            stratify=labels,
        )

        # Fit the vectorizer ONLY on the training split to avoid leaking
        # information from the test split into the model.
        x_train_vectorized = self.vectorizer.fit_transform(x_train)
        x_test_vectorized = self.vectorizer.transform(x_test)

        self.model.fit(x_train_vectorized, y_train)

        predictions = self.model.predict(x_test_vectorized)
        self.accuracy = accuracy_score(y_test, predictions)
        self.is_trained = True

        # Re-fit on the FULL dataset afterwards so the deployed model
        # benefits from every available example, now that we already
        # have an honest accuracy score from the held-out test split.
        full_vectorized = self.vectorizer.fit_transform(cleaned_messages)
        self.model.fit(full_vectorized, labels)

        # Persist the trained artifacts and the accuracy score.
        self._save_model()
        database.save_model_metrics(self.accuracy, len(dataframe))

        return self.accuracy

    # ------------------------------------------------------------------
    # PREDICTION
    # ------------------------------------------------------------------
    def predict(self, message_text):
        """
        Classify a single SMS message.

        Returns a dictionary with:
            label               -> "spam" or "ham"
            confidence          -> float 0-100 (%)
            keywords            -> list of suspicious keywords found
            keywords_string     -> same list joined as "kw1, kw2"
        """
        if not self.is_trained:
            raise RuntimeError(
                "The classifier has not been trained yet. Call train() first."
            )

        cleaned = clean_text(message_text)
        vectorized = self.vectorizer.transform([cleaned])

        prediction = str(self.model.predict(vectorized)[0])
        probabilities = self.model.predict_proba(vectorized)[0]

        # predict_proba returns probabilities in the same order as
        # self.model.classes_, so we look up the probability that
        # matches whichever class was actually predicted.
        class_index = list(self.model.classes_).index(prediction)
        confidence = round(float(probabilities[class_index]) * 100, 2)

        keywords = extract_keywords(message_text)

        return {
            "label": prediction,
            "confidence": confidence,
            "keywords": keywords,
            "keywords_string": ", ".join(keywords),
        }

    # ------------------------------------------------------------------
    # PERSISTENCE
    # ------------------------------------------------------------------
    def _save_model(self):
        """Save the trained vectorizer and model to disk with pickle."""
        with open(config.VECTORIZER_PATH, "wb") as file:
            pickle.dump(self.vectorizer, file)
        with open(config.CLASSIFIER_PATH, "wb") as file:
            pickle.dump(self.model, file)

    def load_saved_model(self):
        """
        Load a previously trained vectorizer/model from disk, if they
        exist. Returns True if a saved model was found and loaded.
        """
        if not (config.VECTORIZER_PATH.exists() and config.CLASSIFIER_PATH.exists()):
            return False

        with open(config.VECTORIZER_PATH, "rb") as file:
            self.vectorizer = pickle.load(file)
        with open(config.CLASSIFIER_PATH, "rb") as file:
            self.model = pickle.load(file)

        self.is_trained = True
        return True
