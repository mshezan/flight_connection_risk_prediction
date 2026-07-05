import pandas as pd

from config import (
    PROCESSED_DIR,
    FEATURE_DIR
)

INPUT_DIR = PROCESSED_DIR
OUTPUT_DIR = FEATURE_DIR

def load_training_history(files):

    dfs = []

    for file_path in files:

        df = pd.read_parquet(
            file_path
        )

        print(
            f"Loaded {file_path.name}: "
            f"{len(df):,} rows"
        )

        dfs.append(df)

    history_df = pd.concat(
        dfs,
        ignore_index=True
    )

    print(
        f"\nTraining History Rows: "
        f"{len(history_df):,}"
    )

    return history_df

def get_training_files():

    files = sorted(
        list(
            INPUT_DIR.glob(
                "clean_2023_*.parquet"
            )
        )
        +
        list(
            INPUT_DIR.glob(
                "clean_2024_*.parquet"
            )
        )
    )

    print(
        f"Found {len(files)} training files"
    )

    return files

def create_time_features(df):
    """
    Create features from date and time columns.
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

    print("Created:")
    print("- MONTH")
    print("- DAY_OF_WEEK")
    print("- DEP_HOUR")

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

    print("Created: ROUTE")

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

    print("Created:")
    print("- CARRIER_ROUTE")
    print("- ORIGIN_HOUR")
    print("- DEST_HOUR")
    print("- CARRIER_MONTH")
    print("- ROUTE_MONTH")

    return df

def create_boolean_features(df):
    """
    Create simple boolean features.
    """

    df["IS_WEEKEND"] = (
        df["DAY_OF_WEEK"] >= 5
    ).astype(int)

    df["IS_RED_EYE"] = (
        (
            df["DEP_HOUR"] >= 22
        )
        |
        (
            df["DEP_HOUR"] <= 5
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

    print("Created:")
    print("- IS_WEEKEND")
    print("- IS_RED_EYE")
    print("- IS_PEAK_HOUR")

    return df

def create_distance_features(df):
    """
    Create distance-based features.
    """

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

    print("Created:")
    print("- DISTANCE_BUCKET")

    return df

def remove_leakage_columns(df):
    """
    Remove columns unavailable before departure.
    """

    columns_to_drop = [
        "DEP_DELAY",
        "DEP_DELAY_NEW",
        "DEP_DEL15",
        "ARR_DELAY",
        "ARR_DELAY_NEW",
        "CARRIER_DELAY",
        "WEATHER_DELAY",
        "NAS_DELAY",
        "LATE_AIRCRAFT_DELAY",
        "CANCELLED",
        "DIVERTED",
    ]

    existing_columns = [
        column
        for column in columns_to_drop
        if column in df.columns
    ]

    df = df.drop(
        columns=existing_columns
    )

    print(
        f"Removed {len(existing_columns)} leakage columns"
    )

    return df   

def validate_features(df):

    print("\nValidation")

    print(
        "Rows:",
        len(df)
    )

    print(
        "Columns:",
        len(df.columns)
    )

    print("\nFeature Columns:")

    print(
        df.columns.tolist()
    )

    print(
        "\nNew Features:"
    )

    new_columns = [
        column
        for column in df.columns
        if (
            "RATE" in column
            or
            "COUNT" in column
            or
            "BUCKET" in column
            or
            column.startswith("IS_")
        )
    ]

    for column in sorted(new_columns):

        print(column)

    return df

def save_feature_file(
    df,
    file_path
):

    output_name = (
        file_path.name
        .replace(
            "clean_",
            "features_"
        )
    )

    output_path = (
        OUTPUT_DIR /
        output_name
    )

    df.to_parquet(
        output_path,
        index=False
    )

    print(
        f"Saved: {output_path}"
    )

def compute_delay_rate(history_df,column_name):

    delay_rate = (
        history_df
        .groupby(column_name)["ARR_DEL15"]
        .mean()
    )

    print(
        f"\nComputed {column_name} Delay Rates"
    )

    print(
        f"Groups: {len(delay_rate):,}"
    )

    return delay_rate

def compute_flight_count(history_df,column_name):
    flight_count = (
        history_df
        .groupby(column_name)
        .size()
    )

    print(
        f"\nComputed {column_name} Flight Counts"
    )

    print(
        f"Groups: {len(flight_count):,}"
    )

    return flight_count

def compute_global_delay_rate(history_df):

    global_delay_rate = (
        history_df["ARR_DEL15"]
        .mean()
    )

    print(
        "\nGlobal Delay Rate"
    )

    print(
        global_delay_rate
    )

    return global_delay_rate

def add_delay_rate_feature(
    df,
    lookup_column,
    lookup_table,
    new_column,
    global_delay_rate
):

    df[new_column] = (
        df[lookup_column]
        .map(lookup_table)
        .fillna(global_delay_rate)
    )

    print(
        f"\nAdded {new_column}"
    )

    return df

def add_count_feature(
    df,
    lookup_column,
    lookup_table,
    new_column
):

    df[new_column] = (
        df[lookup_column]
        .map(lookup_table)
        .fillna(0)
    )

    print(
        f"\nAdded {new_column}"
    )

    return df

def create_popularity_features(df):
    """
    Create popularity-based features.
    """

    df["ROUTE_POPULARITY_BUCKET"] = pd.qcut(
        df["ROUTE_FLIGHT_COUNT"],
        q=5,
        labels=False,
        duplicates="drop"
    )

    print("Created:")
    print("- ROUTE_POPULARITY_BUCKET")

    return df

def remove_temporary_columns(df):
    """
    Remove temporary columns used only for feature creation.
    """

    columns = [
        "CARRIER_ROUTE",
        "ORIGIN_HOUR",
        "DEST_HOUR",
        "CARRIER_MONTH",
        "ROUTE_MONTH",
    ]

    existing = [
        column
        for column in columns
        if column in df.columns
    ]

    df = df.drop(
        columns=existing
    )

    print(
        f"Removed {len(existing)} temporary columns"
    )

    return df

def compute_route_distance_lookup(
    history_df
):

    route_distance = (
        history_df
        .groupby("ROUTE")["DISTANCE"]
        .median()
    )

    print(
        "\nComputed Route Distance Lookup"
    )

    print(
        f"Routes: {len(route_distance):,}"
    )

    return route_distance

def compute_route_popularity_lookup(
    route_count_lookup
):
    """
    Compute popularity bucket for each route.
    """

    route_counts = (
        route_count_lookup
        .reset_index()
    )

    route_counts.columns = [
        "ROUTE",
        "COUNT"
    ]

    route_counts[
        "ROUTE_POPULARITY_BUCKET"
    ] = pd.qcut(
        route_counts["COUNT"],
        q=5,
        labels=False,
        duplicates="drop"
    )

    lookup = (
        route_counts
        .set_index("ROUTE")[
            "ROUTE_POPULARITY_BUCKET"
        ]
    )

    print(
        "\nComputed Route Popularity Lookup"
    )

    print(
        f"Routes: {len(lookup):,}"
    )

    return lookup

def compute_airport_id_lookup(
    history_df,
    airport_column,
    airport_id_column
):
    """
    Compute airport code -> airport ID lookup.
    """

    lookup = (
        history_df
        .groupby(airport_column)[airport_id_column]
        .first()
    )

    print(
        f"\nComputed {airport_column} Airport ID Lookup"
    )

    print(
        f"Airports: {len(lookup):,}"
    )

    return lookup

def compute_route_elapsed_lookup(
    history_df
):
    """
    Compute typical scheduled elapsed time for each route.
    """

    lookup = (
        history_df
        .groupby("ROUTE")["CRS_ELAPSED_TIME"]
        .median()
    )

    print(
        "\nComputed Route Elapsed Lookup"
    )

    print(
        f"Routes: {len(lookup):,}"
    )

    return lookup

def get_all_files():

    files = sorted(
        INPUT_DIR.glob(
            "*.parquet"
        )
    )

    print(
        f"Found {len(files)} files"
    )

    return files

import joblib

from pathlib import Path

from config import MODEL_DIR

def save_lookup_table(
    lookup,
    filename
):
    """
    Save one lookup table.
    """

    lookup_dir = (
        MODEL_DIR /
        "lookups"
    )

    lookup_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        lookup_dir /
        filename
    )

    joblib.dump(
        lookup,
        output_path
    )

    print(
        f"Saved: {output_path}"
    )

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    training_files = get_training_files()

    all_files = get_all_files()

    history_df = load_training_history(
        training_files
    )

    history_df = create_time_features(
        history_df
    )

    history_df = create_route_feature(
        history_df
    )

    history_df = create_boolean_features(
        history_df
    )

    history_df = create_distance_features(
        history_df
    )

    history_df = create_interaction_features(
        history_df
    )

    global_delay_rate = compute_global_delay_rate(
        history_df
    )

    route_delay_lookup = compute_delay_rate(
        history_df,
        "ROUTE"
    )

    carrier_delay_lookup = compute_delay_rate(
        history_df,
        "OP_UNIQUE_CARRIER"
    )

    origin_delay_lookup = compute_delay_rate(
        history_df,
        "ORIGIN"
    )

    dest_delay_lookup = compute_delay_rate(
    history_df,
    "DEST"
    )

    month_delay_lookup = compute_delay_rate(
        history_df,
        "MONTH"
    )

    day_delay_lookup = compute_delay_rate(
        history_df,
        "DAY_OF_WEEK"
    )

    hour_delay_lookup = compute_delay_rate(
        history_df,
        "DEP_HOUR"
    )

    route_count_lookup = compute_flight_count(
        history_df,
        "ROUTE"
    )

    route_popularity_bucket_lookup = (
        compute_route_popularity_lookup(
            route_count_lookup
        )
    )

    origin_count_lookup = compute_flight_count(
        history_df,
        "ORIGIN"
    )

    dest_count_lookup = compute_flight_count(
        history_df,
        "DEST"
    )

    carrier_count_lookup = compute_flight_count(
        history_df,
        "OP_UNIQUE_CARRIER"
    )

    month_count_lookup = compute_flight_count(
        history_df,
        "MONTH"
    )

    carrier_route_delay_lookup = compute_delay_rate(
        history_df,
        "CARRIER_ROUTE"
    )

    origin_hour_delay_lookup = compute_delay_rate(
        history_df,
        "ORIGIN_HOUR"
    )

    dest_hour_delay_lookup = compute_delay_rate(
        history_df,
        "DEST_HOUR"
    )

    carrier_month_delay_lookup = compute_delay_rate(
        history_df,
        "CARRIER_MONTH"
    )

    route_month_delay_lookup = compute_delay_rate(
        history_df,
        "ROUTE_MONTH"
    )

    route_distance_lookup = compute_route_distance_lookup(
        history_df
    )

    origin_airport_id_lookup = compute_airport_id_lookup(
        history_df,
        "ORIGIN",
        "ORIGIN_AIRPORT_ID"
    )

    dest_airport_id_lookup = compute_airport_id_lookup(
        history_df,
        "DEST",
        "DEST_AIRPORT_ID"
    )

    route_elapsed_lookup = (
        compute_route_elapsed_lookup(
            history_df
        )
    )

    route_popularity_bucket_lookup = (
        compute_route_popularity_lookup(
            route_count_lookup
        )
    )

    lookup_tables = {
        "route_delay_lookup.joblib": route_delay_lookup,
        "origin_delay_lookup.joblib": origin_delay_lookup,
        "dest_delay_lookup.joblib": dest_delay_lookup,
        "carrier_delay_lookup.joblib": carrier_delay_lookup,
        "month_delay_lookup.joblib": month_delay_lookup,
        "day_delay_lookup.joblib": day_delay_lookup,
        "hour_delay_lookup.joblib": hour_delay_lookup,

        "route_count_lookup.joblib": route_count_lookup,
        "route_popularity_bucket_lookup.joblib": route_popularity_bucket_lookup,
        "origin_count_lookup.joblib": origin_count_lookup,
        "dest_count_lookup.joblib": dest_count_lookup,
        "carrier_count_lookup.joblib": carrier_count_lookup,
        "month_count_lookup.joblib": month_count_lookup,

        "carrier_route_delay_lookup.joblib": carrier_route_delay_lookup,
        "origin_hour_delay_lookup.joblib": origin_hour_delay_lookup,
        "dest_hour_delay_lookup.joblib": dest_hour_delay_lookup,
        "carrier_month_delay_lookup.joblib": carrier_month_delay_lookup,
        "route_month_delay_lookup.joblib": route_month_delay_lookup,
        "route_distance_lookup.joblib": route_distance_lookup,
        "global_delay_rate.joblib": global_delay_rate,
        "origin_airport_id_lookup.joblib":origin_airport_id_lookup,
        "dest_airport_id_lookup.joblib":dest_airport_id_lookup,
        "route_elapsed_lookup.joblib":route_elapsed_lookup,
        "route_popularity_bucket_lookup.joblib":route_popularity_bucket_lookup,
    }

    for filename, lookup in lookup_tables.items():
        save_lookup_table(
            lookup,
            filename
        )

    for file_path in all_files:

        print("\n" + "=" * 50)
        print(file_path.name)

        df = pd.read_parquet(
            file_path
        )

        df = create_time_features(df)

        df = create_route_feature(df)

        df =create_boolean_features(df)
        
        df = create_distance_features(df)

        df = create_interaction_features(df)

        df = add_delay_rate_feature(
            df,
            "ROUTE",
            route_delay_lookup,
            "ROUTE_DELAY_RATE",
            global_delay_rate
        )

        df = add_delay_rate_feature(
            df,
            "OP_UNIQUE_CARRIER",
            carrier_delay_lookup,
            "CARRIER_DELAY_RATE",
            global_delay_rate
        )

        df = add_delay_rate_feature(
            df,
            "ORIGIN",
            origin_delay_lookup,
            "ORIGIN_DELAY_RATE",
            global_delay_rate
        )

        df = add_delay_rate_feature(
            df,
            "DEST",
            dest_delay_lookup,
            "DEST_DELAY_RATE",
            global_delay_rate
        )

        df = add_delay_rate_feature(
            df,
            "MONTH",
            month_delay_lookup,
            "MONTH_DELAY_RATE",
            global_delay_rate
        )

        df = add_delay_rate_feature(
            df,
            "DAY_OF_WEEK",
            day_delay_lookup,
            "DAY_OF_WEEK_DELAY_RATE",
            global_delay_rate
        )

        df = add_delay_rate_feature(
            df,
            "DEP_HOUR",
            hour_delay_lookup,
            "DEP_HOUR_DELAY_RATE",
            global_delay_rate
        )

        df = add_count_feature(
            df,
            "ROUTE",
            route_count_lookup,
            "ROUTE_FLIGHT_COUNT"
        )

        df = add_count_feature(
            df,
            "ORIGIN",
            origin_count_lookup,
            "ORIGIN_FLIGHT_COUNT"
        )

        df = add_count_feature(
            df,
            "DEST",
            dest_count_lookup,
            "DEST_FLIGHT_COUNT"
        )

        df = add_count_feature(
            df,
            "OP_UNIQUE_CARRIER",
            carrier_count_lookup,
            "CARRIER_FLIGHT_COUNT"
        )

        df = add_count_feature(
            df,
            "MONTH",
            month_count_lookup,
            "MONTH_FLIGHT_COUNT"
        )

        df = create_popularity_features(
            df
        )

        df = add_delay_rate_feature(
            df,
            "CARRIER_ROUTE",
            carrier_route_delay_lookup,
            "CARRIER_ROUTE_DELAY_RATE",
            global_delay_rate
        )

        df = add_delay_rate_feature(
            df,
            "ORIGIN_HOUR",
            origin_hour_delay_lookup,
            "ORIGIN_HOUR_DELAY_RATE",
            global_delay_rate
        )

        df = add_delay_rate_feature(
            df,
            "DEST_HOUR",
            dest_hour_delay_lookup,
            "DEST_HOUR_DELAY_RATE",
            global_delay_rate
        )

        df = add_delay_rate_feature(
            df,
            "CARRIER_MONTH",
            carrier_month_delay_lookup,
            "CARRIER_MONTH_DELAY_RATE",
            global_delay_rate
        )

        df = add_delay_rate_feature(
            df,
            "ROUTE_MONTH",
            route_month_delay_lookup,
            "ROUTE_MONTH_DELAY_RATE",
            global_delay_rate
        )
        df = remove_temporary_columns(df)

        df = remove_leakage_columns(df)

        df=validate_features(df)

        save_feature_file(
            df,
            file_path
        )

if __name__ == "__main__":
    main()