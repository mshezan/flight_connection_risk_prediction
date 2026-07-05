from datetime import datetime

from model.predict import (
    DelayPredictor
)

AVERAGE_DELAY_WHEN_DELAYED = 42

def calculate_layover(
    first_flight,
    second_flight
):
    """
    Calculate scheduled layover in minutes.
    """

    arrival = datetime.fromisoformat(
        first_flight["arrival_datetime"]
    )

    departure = datetime.fromisoformat(
        second_flight["departure_datetime"]
    )

    layover = (
        departure - arrival
    ).total_seconds() / 60

    return int(layover)

def predict_flight(
    predictor,
    flight
):
    """
    Predict delay for one flight.
    """

    prediction = (
        predictor.predict_delay(
            flight
        )
    )

    return prediction

def estimate_expected_delay(
    prediction
):
    """
    Estimate delay minutes.
    """

    probability = prediction[
        "delay_probability"
    ]

    expected_delay = (
        probability
        *
        AVERAGE_DELAY_WHEN_DELAYED
    )

    return expected_delay

def calculate_connection_risk(
    layover_minutes,
    expected_delay
):
    """
    Calculate connection risk.
    """

    remaining_buffer = (
        layover_minutes
        - expected_delay
    )

    risk_score = (
        expected_delay
        / layover_minutes
    )

    risk_score = min(
        risk_score,
        1.0
    )

    return {
        "remaining_buffer": round(
            remaining_buffer,
            1
        ),
        "risk_score": round(
            risk_score,
            3
        )
    }

def classify_risk(
    risk_score
):
    """
    Classify connection risk.
    """

    if risk_score < 0.30:
        return "Low"

    if risk_score < 0.60:
        return "Medium"

    if risk_score < 0.85:
        return "High"

    return "Critical"

def analyze_itinerary(
    itinerary
):

    predictor = DelayPredictor()

    first_flight = itinerary[0]
    second_flight = itinerary[1]

    prediction = predict_flight(
        predictor,
        first_flight
    )

    layover = calculate_layover(
        first_flight,
        second_flight
    )

    expected_delay = estimate_expected_delay(
        prediction
    )

    risk = calculate_connection_risk(
        layover,
        expected_delay
    )

    risk_level = classify_risk(
        risk["risk_score"]
    )

    return {
        "first_flight": prediction,
        "layover_minutes": layover,
        "expected_delay_minutes": round(
            expected_delay,
            1
        ),
        "remaining_buffer": risk[
            "remaining_buffer"
        ],
        "risk_score": risk[
            "risk_score"
        ],
        "risk_level": risk_level
    }

def main():

    itinerary = [
        {
            "carrier": "AA",
            "origin": "PHL",
            "destination": "LAX",
            "departure_datetime": "2026-06-29T13:22:00",
            "arrival_datetime": "2026-06-29T16:18:00"
        },
        {
            "carrier": "AA",
            "origin": "LAX",
            "destination": "SFO",
            "departure_datetime": "2026-06-29T17:00:00",
            "arrival_datetime": "2026-06-29T18:30:00"
        }
    ]

    result = analyze_itinerary(
        itinerary
    )

    print(result)


if __name__ == "__main__":
    main()