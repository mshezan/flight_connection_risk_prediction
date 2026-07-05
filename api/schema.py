from pydantic import BaseModel  

class FlightRequest(BaseModel):

    carrier: str

    origin: str

    destination: str

    departure_datetime: str
    
    arrival_datetime : str

class ConnectionRequest(BaseModel):

    flights: list[FlightRequest]

class PredictionResponse(BaseModel):

    delay_probability: float

    predicted_delay: bool

    risk_score: float

class ConnectionResponse(BaseModel):

    layover_minutes: int

    expected_delay_minutes: float

    remaining_buffer: float

    risk_score: float

    risk_level: str
