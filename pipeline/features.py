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

    carrier_route_lookup = compute_delay_rate(
        history_df,
        "CARRIER_ROUTE"
    )

    origin_hour_lookup = compute_delay_rate(
        history_df,
        "ORIGIN_HOUR"
    )

    dest_hour_lookup = compute_delay_rate(
        history_df,
        "DEST_HOUR"
    )

    carrier_month_lookup = compute_delay_rate(
        history_df,
        "CARRIER_MONTH"
    )

    route_month_lookup = compute_delay_rate(
        history_df,
        "ROUTE_MONTH"
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
            carrier_route_lookup,
            "CARRIER_ROUTE_DELAY_RATE",
            global_delay_rate
        )

        df = add_delay_rate_feature(
            df,
            "ORIGIN_HOUR",
            origin_hour_lookup,
            "ORIGIN_HOUR_DELAY_RATE",
            global_delay_rate
        )

        df = add_delay_rate_feature(
            df,
            "DEST_HOUR",
            dest_hour_lookup,
            "DEST_HOUR_DELAY_RATE",
            global_delay_rate
        )

        df = add_delay_rate_feature(
            df,
            "CARRIER_MONTH",
            carrier_month_lookup,
            "CARRIER_MONTH_DELAY_RATE",
            global_delay_rate
        )

        df = add_delay_rate_feature(
            df,
            "ROUTE_MONTH",
            route_month_lookup,
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