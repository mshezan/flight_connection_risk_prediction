from fastapi import FastAPI
from api.schema import (
    FlightRequest,
    PredictionResponse,
    ConnectionRequest,
    ConnectionResponse
)

from model.predict import ( 
    DelayPredictor
)

from model.connection import (
    analyze_itinerary
)

from pipeline.features import (
    create_route_feature
)

app = FastAPI(
    title="Flight Connection Risk Predictor API",
    description="Backend API for predicting flight delays and missed connections.",
    version="1.0.0"
)

predictor = DelayPredictor()

@app.get("/")
def home():

    return {
        "message":"Flight Connection Risk Predictor API"
    }

@app.post(
    "/predict",
    response_model=PredictionResponse
)
def predict(
    flight: FlightRequest
):

    result = predictor.predict_delay(
        {
            "carrier": flight.carrier,
            "origin": flight.origin,
            "destination": flight.destination,
            "departure_datetime": flight.departure_datetime
        }
    )

    return result

@app.post(
    "/connection",
    response_model=ConnectionResponse
)
def connection(
    request: ConnectionRequest
):

    flights = []

    for flight in request.flights:
        flights.append(
            {
                "carrier": flight.carrier,
                "origin": flight.origin,
                "destination": flight.destination,
                "departure_datetime": flight.departure_datetime,
                "arrival_datetime": flight.arrival_datetime
            }
        )

    result = analyze_itinerary(flights)

    print(result)      # <-- add this temporarily

    return result