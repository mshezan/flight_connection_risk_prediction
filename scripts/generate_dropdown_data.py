from pathlib import Path
import json

import joblib

from config import LOOKUP_DIR

def load_lookup_tables():

    origin_lookup = joblib.load(
        LOOKUP_DIR / "origin_delay_lookup.joblib"
    )

    destination_lookup = joblib.load(
        LOOKUP_DIR / "dest_delay_lookup.joblib"
    )

    carrier_lookup = joblib.load(
        LOOKUP_DIR / "carrier_delay_lookup.joblib"
    )

    return (
        origin_lookup,
        destination_lookup,
        carrier_lookup
    )

def extract_airports(
    origin_lookup,
    destination_lookup
):

    airports = sorted(
        set(origin_lookup.keys())
        |
        set(destination_lookup.keys())
    )

    return airports

def extract_carriers(
    carrier_lookup
):

    carriers = sorted(
        carrier_lookup.keys()
    )

    return carriers

def save_json(
    data,
    filename
):

    output_path = (
        Path("frontend")
        / "src"
        / "data"
        / filename
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )

    print(
        f"Saved {output_path}"
    )

def main():

    (
        origin_lookup,
        destination_lookup,
        carrier_lookup
    ) = load_lookup_tables()

    airports = extract_airports(
        origin_lookup,
        destination_lookup
    )

    carriers = extract_carriers(
        carrier_lookup
    )

    save_json(
        airports,
        "airports.json"
    )

    save_json(
        carriers,
        "airlines.json"
    )


if __name__ == "__main__":
    main()