import joblib
import pandas as pd

from config import (
    MODEL_DIR,
)

LOOKUP_DIR = (
    MODEL_DIR /
    "lookups"
)

DELAY_RATE_FEATURES = [
    ("ROUTE", "route_delay_lookup", "ROUTE_DELAY_RATE"),
    ("ORIGIN", "origin_delay_lookup", "ORIGIN_DELAY_RATE"),
    ("DEST", "dest_delay_lookup", "DEST_DELAY_RATE"),
    ("OP_UNIQUE_CARRIER", "carrier_delay_lookup", "CARRIER_DELAY_RATE"),
    ("MONTH", "month_delay_lookup", "MONTH_DELAY_RATE"),
    ("DAY_OF_WEEK", "day_delay_lookup", "DAY_OF_WEEK_DELAY_RATE"),
    ("DEP_HOUR", "hour_delay_lookup", "DEP_HOUR_DELAY_RATE"),
]

COUNT_FEATURES = [
    ("ROUTE", "route_count_lookup", "ROUTE_FLIGHT_COUNT"),
    ("ORIGIN", "origin_count_lookup", "ORIGIN_FLIGHT_COUNT"),
    ("DEST", "dest_count_lookup", "DEST_FLIGHT_COUNT"),
    ("OP_UNIQUE_CARRIER", "carrier_count_lookup", "CARRIER_FLIGHT_COUNT"),
    ("MONTH", "month_count_lookup", "MONTH_FLIGHT_COUNT"),
]

INTERACTION_DELAY_FEATURES = [
    (
        "CARRIER_ROUTE",
        "carrier_route_delay_lookup",
        "CARRIER_ROUTE_DELAY_RATE"
    ),
    (
        "ORIGIN_HOUR",
        "origin_hour_delay_lookup",
        "ORIGIN_HOUR_DELAY_RATE"
    ),
    (
        "DEST_HOUR",
        "dest_hour_delay_lookup",
        "DEST_HOUR_DELAY_RATE"
    ),
    (
        "CARRIER_MONTH",
        "carrier_month_delay_lookup",
        "CARRIER_MONTH_DELAY_RATE"
    ),
    (
        "ROUTE_MONTH",
        "route_month_delay_lookup",
        "ROUTE_MONTH_DELAY_RATE"
    ),
]

def load_lookups():
    lookups = {}

    for file_path in LOOKUP_DIR.glob(
        "*.joblib"
    ):

        lookups[
            file_path.stem
        ] = joblib.load(
            file_path
        )

    print(
        f"Loaded {len(lookups)} lookup tables."
    )

    return lookups

def build_base_dataframe(flight):
    """
    Convert user input into a one-row dataframe.
    """
    departure = pd.to_datetime(
        flight["departure_datetime"]
    )

    df = pd.DataFrame(
        {
            "YEAR": [
                departure.year
            ],
            "MONTH": [
                departure.month
            ],
            "DAY_OF_MONTH": [
                departure.day
            ],
            "DAY_OF_WEEK": [
                departure.dayofweek
            ],
            "OP_UNIQUE_CARRIER": [
                flight["carrier"]
            ],
            "ORIGIN": [
                flight["origin"]
            ],
            "DEST": [
                flight["destination"]
            ],
            "FL_DATE": [
                departure
            ],
            "CRS_DEP_TIME": [
                departure.hour * 100
                + departure.minute
            ]
        }
    )

    return df

def create_time_features(df):
    """
    Create time-based features.
    """

    df["MONTH"] = (
        df["FL_DATE"]
        .dt.month
    )

    df["DAY_OF_WEEK"] = (
        df["FL_DATE"]
        .dt.dayofweek
    )

    df["DEP_HOUR"] = (
        df["CRS_DEP_TIME"] // 100
    )

    return df

def create_route_feature(df):
    """
    Create route feature.
    """

    df["ROUTE"] = (
        df["ORIGIN"]
        + "_"
        + df["DEST"]
    )

    return df

def create_boolean_features(df):
    """
    Create boolean features.
    """

    df["IS_WEEKEND"] = (
        df["DAY_OF_WEEK"] >= 5
    ).astype(int)

    df["IS_RED_EYE"] = (
        (
            df["DEP_HOUR"] <= 5
        )
        |
        (
            df["DEP_HOUR"] >= 22
        )
    ).astype(int)

    df["IS_PEAK_HOUR"] = (
        (
            (df["DEP_HOUR"] >= 6)
            &
            (df["DEP_HOUR"] <= 9)
        )
        |
        (
            (df["DEP_HOUR"] >= 16)
            &
            (df["DEP_HOUR"] <= 19)
        )
    ).astype(int)

    return df

def create_distance_features(
    df,
    lookups
):
    """
    Add distance-based features.
    """

    route_distance_lookup = lookups[
        "route_distance_lookup"
    ]

    global_distance = (
        route_distance_lookup
        .median()
    )

    df["DISTANCE"] = (
        df["ROUTE"]
        .map(route_distance_lookup)
        .fillna(global_distance)
    )

    bins = [
        0,
        250,
        500,
        1000,
        2000,
        float("inf")
    ]

    labels = [
        0,
        1,
        2,
        3,
        4
    ]

    df["DISTANCE_BUCKET"] = pd.cut(
        df["DISTANCE"],
        bins=bins,
        labels=labels,
        include_lowest=True
    ).astype(int)

    return df

def add_delay_rate_features(
    df,
    lookups
):
    """
    Add historical delay-rate features.
    """

    global_delay_rate = lookups[
        "global_delay_rate"
    ]

    for (
        lookup_column,
        lookup_name,
        feature_name
    ) in DELAY_RATE_FEATURES:

        lookup_table = lookups[
            lookup_name
        ]

        df[feature_name] = (
            df[lookup_column]
            .map(lookup_table)
            .fillna(global_delay_rate)
        )

    return df

def add_count_features(
    df,
    lookups
):
    """
    Add historical flight-count features.
    """

    for (
        lookup_column,
        lookup_name,
        feature_name
    ) in COUNT_FEATURES:

        lookup_table = lookups[
            lookup_name
        ]

        median_count = lookup_table.median()

        df[feature_name] = (
            df[lookup_column]
            .map(lookup_table)
            .fillna(median_count)
        )

    return df

def create_interaction_features(df):
    """
    Create interaction features.
    """

    df["CARRIER_ROUTE"] = (
        df["OP_UNIQUE_CARRIER"]
        + "_"
        + df["ROUTE"]
    )

    df["ORIGIN_HOUR"] = (
        df["ORIGIN"]
        + "_"
        + df["DEP_HOUR"].astype(str)
    )

    df["DEST_HOUR"] = (
        df["DEST"]
        + "_"
        + df["DEP_HOUR"].astype(str)
    )

    df["CARRIER_MONTH"] = (
        df["OP_UNIQUE_CARRIER"]
        + "_"
        + df["MONTH"].astype(str)
    )

    df["ROUTE_MONTH"] = (
        df["ROUTE"]
        + "_"
        + df["MONTH"].astype(str)
    )

    return df

def add_interaction_delay_features(
    df,
    lookups
):

    global_delay_rate = lookups[
        "global_delay_rate"
    ]

    for (
        lookup_column,
        lookup_name,
        feature_name
    ) in INTERACTION_DELAY_FEATURES:

        lookup_table = lookups[
            lookup_name
        ]

        df[feature_name] = (
            df[lookup_column]
            .map(lookup_table)
            .fillna(global_delay_rate)
        )

    return df

def create_popularity_features(df):

    df["ROUTE_POPULARITY_BUCKET"] = pd.qcut(
        df["ROUTE_FLIGHT_COUNT"],
        q=5,
        labels=False,
        duplicates="drop"
    )

    return df

def remove_temporary_columns(df):

    columns = [
        "CARRIER_ROUTE",
        "ORIGIN_HOUR",
        "DEST_HOUR",
        "CARRIER_MONTH",
        "ROUTE_MONTH",
    ]

    df = df.drop(
        columns=columns,
        errors="ignore"
    )

    return df

def build_features(
    flight,
    lookups
):
    """
    Build all model features for a single flight.
    """

    df = build_base_dataframe(
        flight
    )

    df = create_time_features(
        df
    )

    df = create_route_feature(
        df
    )

    df = add_airport_id_features(
        df,
        lookups
    )

    df = add_schedule_features(
        df,
        lookups
    )

    df = create_boolean_features(
        df
    )

    df = create_distance_features(
        df,
        lookups
    )

    df = add_delay_rate_features(
        df,
        lookups
    )

    df = add_count_features(
        df,
        lookups
    )

    df = add_popularity_features(
        df,
        lookups
    )

    df = create_interaction_features(
        df
    )

    df = add_interaction_delay_features(
        df,
        lookups
    )

    df = remove_temporary_columns(
        df
    )

    integer_columns = [
        "CRS_ELAPSED_TIME",
        "CRS_ARR_TIME",
        "DISTANCE",
    ]

    df[integer_columns] = (
        df[integer_columns]
        .astype(int)
    )

    df = df.drop(
        columns=["FL_DATE"]
    )


    return df

def add_airport_id_features(
    df,
    lookups
):

    df["ORIGIN_AIRPORT_ID"] = (
        df["ORIGIN"]
        .map(
            lookups[
                "origin_airport_id_lookup"
            ]
        )
    )

    df["DEST_AIRPORT_ID"] = (
        df["DEST"]
        .map(
            lookups[
                "dest_airport_id_lookup"
            ]
        )
    )

    return df

def add_schedule_features(
    df,
    lookups
):
    elapsed_lookup = lookups[
        "route_elapsed_lookup"
    ]

    global_elapsed = (
        elapsed_lookup
        .median()
    )

    df["CRS_ELAPSED_TIME"] = (
        df["ROUTE"]
        .map(elapsed_lookup)
        .fillna(global_elapsed)
    )
    departure_minutes = (
        (df["CRS_DEP_TIME"] // 100) * 60
        +
        (df["CRS_DEP_TIME"] % 100)
    )

    arrival_minutes = (
        departure_minutes
        +
        df["CRS_ELAPSED_TIME"]
    )

    arrival_minutes %= 1440

    hours = (
        arrival_minutes // 60
    )

    minutes = (
        arrival_minutes % 60
    )

    df["CRS_ARR_TIME"] = (
        hours * 100
        +
        minutes
    )
    return df

def add_popularity_features(
    df,
    lookups
):

    df[
        "ROUTE_POPULARITY_BUCKET"
    ] = (
        df["ROUTE"]
        .map(
            lookups[
                "route_popularity_bucket_lookup"
            ]
        )
        .fillna(2)
        .astype(int)
    )

    return df

def validate_features(df):

    expected_columns = [
        ...
    ]

    missing = (
        set(expected_columns)
        -
        set(df.columns)
    )

    if missing:

        raise ValueError(
            f"Missing columns: {missing}"
        )

    return df

def main():

    lookups = load_lookups()

    flight = {
        "carrier": "AA",
        "origin": "JFK",
        "destination": "DFW",
        "departure_datetime":
            "2026-07-15T09:20:00"
    }

    df = build_features(
        flight,
        lookups
    )

    print(df.T)
    print("\nColumns:")
    print(df.columns.tolist())
    


if __name__ == "__main__":
    main()