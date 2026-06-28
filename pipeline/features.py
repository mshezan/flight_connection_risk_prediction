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
        "LATE_AIRCRAFT_DELAY"
    ]

    df = df.drop(
        columns=columns_to_drop
    )

    print(
        f"Removed {len(columns_to_drop)} leakage columns"
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

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
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

    history_df = create_route_feature(
        history_df
    )

    global_delay_rate = compute_global_delay_rate(
        history_df
    )

    route_lookup = compute_delay_rate(
        history_df,
        "ROUTE"
    )

    carrier_lookup = compute_delay_rate(
        history_df,
        "OP_UNIQUE_CARRIER"
    )

    origin_lookup = compute_delay_rate(
        history_df,
        "ORIGIN"
    )

    for file_path in all_files:

        print("\n" + "=" * 50)
        print(file_path.name)

        df = pd.read_parquet(
            file_path
        )

        df = create_time_features(df)

        df = create_route_feature(df)

        df = add_delay_rate_feature(
            df,
            "ROUTE",
            route_lookup,
            "ROUTE_DELAY_RATE",
            global_delay_rate
        )

        df = add_delay_rate_feature(
            df,
            "OP_UNIQUE_CARRIER",
            carrier_lookup,
            "CARRIER_DELAY_RATE",
            global_delay_rate
        )

        df = add_delay_rate_feature(
            df,
            "ORIGIN",
            origin_lookup,
            "ORIGIN_DELAY_RATE",
            global_delay_rate
        )

        df = remove_leakage_columns(df)

        validate_features(df)

        save_feature_file(
            df,
            file_path
        )

if __name__ == "__main__":
    main()