import axios from "axios";

import type {
  ConnectionRequest,
  ConnectionResult,
} from "@/types/flight";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

export async function analyzeConnection(
  request: ConnectionRequest
): Promise<ConnectionResult> {
  const response =
    await api.post<ConnectionResult>(
      "/connection",
      request
    );

  return response.data;
}

export default api;