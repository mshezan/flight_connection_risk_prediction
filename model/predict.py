import joblib

from config import (
    MODEL_PATH,
)

from model.feature_builder import (
    build_features,
    load_lookups,
)

def load_model():
    """
    Load trained model.
    """

    print("Loading model...")

    model = joblib.load(
        MODEL_PATH
    )

    print("Model loaded.")

    return model

class DelayPredictor:

    def __init__(self):

        self.model = load_model()

        self.lookups = load_lookups()

    def predict_probability(
        self,
        flight
    ):
        """
        Predict probability of arrival delay.
        """

        features = build_features(
            flight,
            self.lookups
        )

        probability = (
            self.model
            .predict_proba(features)[0][1]
        )

        return probability
    
    def predict(
        self,
        flight
    ):

        features = build_features(
            flight,
            self.lookups
        )

        prediction = (
            self.model
            .predict(features)[0]
        )

        return bool(prediction)
    
    def predict_delay(
        self,
        flight
    ):

        features = build_features(
            flight,
            self.lookups
        )

        probability = (
            self.model
            .predict_proba(features)[0][1]
        )

        prediction = bool(
            probability >= 0.5
        )

        return {
        "delay_probability": float(probability),
        "predicted_delay": bool(prediction),
        "risk_score": float(probability)
    }

def main():

    predictor = DelayPredictor()

    flight = {
        "carrier": "AA",
        "origin": "JFK",
        "destination": "DFW",
        "departure_datetime":
            "2026-07-15T09:20:00"
    }

    result = predictor.predict_delay(
        flight
    )

    print(result)

if __name__ == "__main__":
    main()