export interface Flight {
  carrier: string;
  origin: string;
  destination: string;
  departure_datetime: string;
  arrival_datetime: string;
}

export interface ConnectionRequest {
  flights: Flight[];
}

export interface DelayPrediction {
  delay_probability: number;
  predicted_delay: boolean;
  risk_score: number;
}

export interface ConnectionResult {
  layover_minutes: number;
  expected_delay_minutes: number;
  remaining_buffer: number;
  risk_score: number;
  risk_level: string;
}