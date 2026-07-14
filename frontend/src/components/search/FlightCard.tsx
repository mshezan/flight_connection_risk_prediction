import { Trash2 } from "lucide-react";

import AirportSelect from "./AirportSelect";
import AirlineSelect from "./AirlineSelect";

import type { Flight } from "@/types/flight";

interface FlightCardProps {
  flight: Flight;
  flightNumber: number;
  canDelete: boolean;
  onChange: (updatedFlight: Flight) => void;
  onDelete: () => void;
}

export default function FlightCard({
  flight,
  flightNumber,
  canDelete,
  onChange,
  onDelete,
}: FlightCardProps) {
  function updateField(
    field: keyof Flight,
    value: string
  ) {
    onChange({
      ...flight,
      [field]: value,
    });
  }

  const inputClasses = `
    h-14 w-full
    rounded-xl
    border border-[#2a3950]
    bg-[#0c182a]
    px-4
    text-base text-white
    outline-none
    transition
    [color-scheme:dark]
    focus:border-[#6f63e8]
    focus:ring-2
    focus:ring-[#6f63e8]/20
  `;

  return (
    <article
        className="
            rounded-2xl
            border border-[#26364d]
            bg-[#0d192b]
            p-5
            shadow-lg shadow-black/10
        "
        >
      <div className="mb-4 flex items-center justify-between gap-4">
        <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-[#8b7cff]">
                Flight
            </p>

            <h3 className="mt-1 text-xl font-bold text-white">
                Flight {flightNumber}
            </h3>
        </div>

        {canDelete && (
          <button
            type="button"
            onClick={onDelete}
            className="
              inline-flex h-11 items-center gap-2
              rounded-xl
              border border-red-500/50
              px-4
              font-medium text-red-400
              transition
              hover:bg-red-500/10
            "
          >
            <Trash2 className="size-4" />
            Remove
          </button>
        )}
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        <Field label="Airline">
          <AirlineSelect
            value={flight.carrier}
            onChange={(value) =>
              updateField("carrier", value)
            }
          />
        </Field>

        <Field label="Origin">
          <AirportSelect
            value={flight.origin}
            onChange={(value) =>
              updateField("origin", value)
            }
            placeholder="Select origin"
          />
        </Field>

        <Field label="Destination">
          <AirportSelect
            value={flight.destination}
            onChange={(value) =>
              updateField("destination", value)
            }
            placeholder="Select destination"
          />
        </Field>
      </div>

      <div className="mt-6 grid gap-5 lg:grid-cols-2">
        <Field label="Departure">
          <input
            type="datetime-local"
            value={flight.departure_datetime}
            onChange={(event) =>
              updateField(
                "departure_datetime",
                event.target.value
              )
            }
            className={inputClasses}
          />
        </Field>

        <Field label="Scheduled arrival">
          <input
            type="datetime-local"
            value={flight.arrival_datetime}
            onChange={(event) =>
              updateField(
                "arrival_datetime",
                event.target.value
              )
            }
            className={inputClasses}
          />
        </Field>
      </div>
    </article>
  );
}

interface FieldProps {
  label: string;
  children: React.ReactNode;
}

function Field({
  label,
  children,
}: FieldProps) {
  return (
    <div className="space-y-2.5">
      <label className="block text-sm font-medium text-[#d9e1ee]">
        {label}
      </label>

      {children}
    </div>
  );
}