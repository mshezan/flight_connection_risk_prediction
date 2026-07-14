import { useState } from "react";
import {
  ChartNoAxesCombined,
  Plus,
} from "lucide-react";

import FlightCard from "./FlightCard";
import RiskSummary from "@/components/results/RiskSummary";

import {
  analyzeConnection,
} from "@/services/api";

import type {
  Flight,
  ConnectionResult,
} from "@/types/flight";


const emptyFlight = (): Flight => ({
  carrier: "",
  origin: "",
  destination: "",
  departure_datetime: "",
  arrival_datetime: "",
});


export default function SearchPanel() {

  /*
   * STATE
   *
   * We start with two flights because a connection
   * requires at least two flights.
   */
  const [flights, setFlights] = useState<Flight[]>([
    emptyFlight(),
    emptyFlight(),
  ]);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [result, setResult] =
    useState<ConnectionResult | null>(null);


  /*
   * UPDATE A FLIGHT
   *
   * When a flight's destination changes,
   * automatically use that airport as the
   * origin of the next flight.
   */
  function updateFlight(
    index: number,
    updatedFlight: Flight
  ) {

    const updatedFlights = [...flights];

    const previousDestination =
      updatedFlights[index].destination;

    updatedFlights[index] = updatedFlight;

    const destinationChanged =
      previousDestination !==
      updatedFlight.destination;

    const hasNextFlight =
      index < updatedFlights.length - 1;

    if (
      destinationChanged &&
      hasNextFlight
    ) {

      updatedFlights[index + 1] = {
        ...updatedFlights[index + 1],
        origin: updatedFlight.destination,
      };

    }

    setFlights(updatedFlights);

  }


  /*
   * ADD ANOTHER FLIGHT
   *
   * If the previous flight already has a destination,
   * automatically use it as the new flight's origin.
   */
  function addFlight() {

    const previousFlight =
      flights[flights.length - 1];

    const newFlight: Flight = {
      ...emptyFlight(),
      origin: previousFlight.destination,
    };

    setFlights([
      ...flights,
      newFlight,
    ]);

  }


  /*
   * REMOVE A FLIGHT
   *
   * We always keep at least two flights because
   * otherwise there is no connection to analyze.
   */
  function removeFlight(index: number) {

    if (flights.length <= 2) {
      return;
    }

    setFlights(
      flights.filter(
        (_, flightIndex) =>
          flightIndex !== index
      )
    );

  }


  /*
   * ANALYZE THE ITINERARY
   */
  async function handleAnalyzeConnection() {
    console.log("CURRENT FLIGHTS:", flights);
    /*
     * Clear any previous error or result.
     */
    setError("");
    setResult(null);


    /*
     * VALIDATION 1:
     * Make sure every field is completed.
     */
    const hasEmptyFields = flights.some(
      (flight) =>
        !flight.carrier ||
        !flight.origin ||
        !flight.destination ||
        !flight.departure_datetime ||
        !flight.arrival_datetime
    );

    if (hasEmptyFields) {

      setError(
        "Please complete all flight details before analyzing the connection."
      );

      return;

    }


    /*
     * VALIDATION 2:
     * Every flight must arrive after it departs.
     */
    const hasInvalidFlightTimes =
      flights.some(
        (flight) =>
          new Date(
            flight.arrival_datetime
          ) <=
          new Date(
            flight.departure_datetime
          )
      );

    if (hasInvalidFlightTimes) {

      setError(
        "Each flight must arrive after it departs."
      );

      return;

    }


    /*
     * VALIDATION 3:
     * Each connecting flight must depart after
     * the previous flight arrives.
     */
    for (
      let index = 0;
      index < flights.length - 1;
      index++
    ) {

      const currentArrival =
        new Date(
          flights[index].arrival_datetime
        );

      const nextDeparture =
        new Date(
          flights[index + 1]
            .departure_datetime
        );

      if (
        nextDeparture <= currentArrival
      ) {

        setError(
          `Flight ${index + 2} must depart after Flight ${index + 1} arrives.`
        );

        return;

      }

    }


    /*
     * All validation passed.
     * Start the loading state and call FastAPI.
     */
    setLoading(true);

    try {

      const connectionResult =
        await analyzeConnection({
          flights,
        });

      setResult(
        connectionResult
      );

    }

    catch (error) {

      console.error(
        "Connection analysis failed:",
        error
      );

      setError(
        "Unable to analyze the connection. Please check your itinerary and try again."
      );

    }

    finally {

      setLoading(false);

    }

  }


  return (

    <section className="space-y-5">

      {/* PAGE HEADING */}

      <div>

        <h2 className="text-2xl font-bold tracking-tight text-white lg:text-3xl">

          Build your{" "}

          <span className="bg-gradient-to-r from-[#8b7cff] to-[#a78bfa] bg-clip-text text-transparent">

            itinerary

          </span>

        </h2>


        <p className="mt-1.5 text-sm text-[#aeb9cc] lg:text-base">

          Add each flight in your journey and let the
          model estimate the probability of missing a
          connection.

        </p>

      </div>


      {/* FLIGHT CARDS */}

      <div className="space-y-4">

        {flights.map(
          (flight, index) => (

            <FlightCard

              key={index}

              flight={flight}

              flightNumber={
                index + 1
              }

              canDelete={
                flights.length > 2
              }

              onChange={(
                updatedFlight
              ) =>
                updateFlight(
                  index,
                  updatedFlight
                )
              }

              onDelete={() =>
                removeFlight(index)
              }

            />

          )
        )}

      </div>


      {/* ACTION BUTTONS */}

      <div className="flex flex-col gap-3 sm:flex-row">

        <button

          type="button"

          onClick={
            addFlight
          }

          className="
            inline-flex
            h-11
            items-center
            justify-center
            gap-2
            rounded-xl
            border
            border-[#6657e8]
            bg-transparent
            px-6
            font-semibold
            text-[#9487ff]
            transition
            hover:bg-[#6657e8]/10
            focus:outline-none
            focus:ring-2
            focus:ring-[#7c6cff]/50
          "

        >

          <Plus className="size-5" />

          Add Flight

        </button>


        <button

          type="button"

          onClick={
            handleAnalyzeConnection
          }

          disabled={
            loading
          }

          className="
            inline-flex
            h-11
            items-center
            justify-center
            gap-2
            rounded-xl
            bg-gradient-to-r
            from-[#6254e8]
            to-[#7c4ff2]
            px-7
            font-semibold
            text-white
            shadow-lg
            shadow-[#6254e8]/20
            transition
            hover:brightness-110
            disabled:cursor-not-allowed
            disabled:opacity-50
          "

        >

          <ChartNoAxesCombined
            className="size-5"
          />

          {
            loading
              ? "Analyzing..."
              : "Analyze Connection"
          }

        </button>

      </div>


      {/* ERROR MESSAGE */}

      {error && (

        <div
          className="
            rounded-xl
            border
            border-red-500/30
            bg-red-500/10
            p-4
            text-sm
            text-red-300
          "
        >

          {error}

        </div>

      )}


      {/* MODEL RESULT */}

      {result && (

        <RiskSummary
          result={result}
        />

      )}

    </section>

  );

}