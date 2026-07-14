from pathlib import Path
import json

import joblib
import pandas as pd

from config import LOOKUP_DIR


ROOT = Path(__file__).resolve().parent.parent

AIRPORT_MASTER = ROOT / "data" / "us_airports.csv"
AIRLINE_MASTER = ROOT / "data" / "us_airlines.json"

OUTPUT_DIR = ROOT / "frontend" / "src" / "data"


def load_supported_codes():

    origin_lookup = joblib.load(
        LOOKUP_DIR / "origin_delay_lookup.joblib"
    )

    destination_lookup = joblib.load(
        LOOKUP_DIR / "dest_delay_lookup.joblib"
    )

    carrier_lookup = joblib.load(
        LOOKUP_DIR / "carrier_delay_lookup.joblib"
    )

    airports = (
        set(origin_lookup.keys())
        |
        set(destination_lookup.keys())
    )

    carriers = set(
        carrier_lookup.keys()
    )

    return airports, carriers


import pandas as pd


def build_airports(master_airports, supported_airports):

    df = pd.read_csv(master_airports)

    # Keep only airports that have an IATA code
    df = df[df["iata_code"].notna()]

    # Keep only airports supported by your ML model
    df = df[
        df["iata_code"].isin(supported_airports)
    ]

    # US airports only
    df = df[
        df["iso_country"] == "US"
    ]

    # Optional: only airports with scheduled commercial service
    df = df[
        df["scheduled_service"] == "yes"
    ]

    df = df.sort_values("municipality")

    airports = []

    for _, row in df.iterrows():

        airports.append(
            {
                "code": row["iata_code"],
                "city": row["municipality"],
                "state": row["iso_region"].replace("US-", ""),
                "name": row["name"],
                "display": f'{row["municipality"]}, {row["iso_region"].replace("US-", "")} ({row["iata_code"]})'
            }
        )

    return airports



def save_json(data, filename):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_DIR / filename,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )


def main():

    supported_airports, supported_carriers = (
        load_supported_codes()
    )

    print(
        f"Supported Airports: {len(supported_airports)}"
    )

    print(
        f"Supported Airlines: {len(supported_carriers)}"
    )

    airports = build_airports(
        AIRPORT_MASTER,
        supported_airports,
    )


    save_json(
        airports,
        "airports.json",
    )

    print(
        f"Saved {len(airports)} airports."
    )


if __name__ == "__main__":
    main()