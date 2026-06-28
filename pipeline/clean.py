from pathlib import Path
import pandas as pd

RAW_DIR = Path("../data/raw")
PROCESSED_DIR = Path("../data/processed")

def get_csv_files():
    """
    Find all CSV files in data/raw.
    """

    return sorted(
        RAW_DIR.glob("*.csv")
    )

def load_file(file_path):
    """
    Load one BTS CSV file.
    """

    df = pd.read_csv(file_path)

    print(
        f"Loaded {file_path.name}: "
        f"{len(df):,} rows"
    )

    return df

def convert_types(df):
    """
    Convert columns to proper types.
    """

    df["FL_DATE"] = pd.to_datetime(
        df["FL_DATE"],
        format="%m/%d/%Y %I:%M:%S %p"
    )

    return df

def remove_invalid_flights(df):
    """
    Remove cancelled and diverted flights.
    """

    rows_before = len(df)

    cancelled = (df["CANCELLED"] == 1).sum()
    diverted = (df["DIVERTED"] == 1).sum()

    df = df[df["CANCELLED"] == 0]
    df = df[df["DIVERTED"] == 0]

    rows_after = len(df)

    print(f"Rows before: {rows_before:,}")
    print(f"Cancelled removed: {cancelled:,}")
    print(f"Diverted removed: {diverted:,}")
    print(f"Rows after: {rows_after:,}")

    return df

def handle_missing_values(df):
    """
    Apply missing-value rules.
    """

    delay_columns = [
        "CARRIER_DELAY",
        "WEATHER_DELAY",
        "NAS_DELAY",
        "LATE_AIRCRAFT_DELAY"
    ]

    for column in delay_columns:

        missing_count = df[column].isna().sum()

        df[column] = df[column].fillna(0)

        print(
            f"{column}: filled "
            f"{missing_count:,} missing values"
        )

    rows_before = len(df)

    df = df.dropna(
        subset=["ARR_DEL15"]
    )

    rows_after = len(df)

    print(
        f"Dropped {rows_before - rows_after:,} rows "
        f"with missing ARR_DEL15"
    )

    return df

def validate_dataframe(df):
    """
    Verify cleaning worked.
    """

    print("\nValidation")

    print(
        "Cancelled flights:",
        (df["CANCELLED"] == 1).sum()
    )

    print(
        "Diverted flights:",
        (df["DIVERTED"] == 1).sum()
    )

    print(
        "Missing ARR_DEL15:",
        df["ARR_DEL15"].isna().sum()
    )

    print(
        "FL_DATE dtype:",
        df["FL_DATE"].dtype
    )

    return df

def save_clean_file(df, file_path):
    """
    Save cleaned dataframe as parquet.
    """

    output_name = (
        "clean_" +
        file_path.stem.replace(
            "flights_",
            ""
        ) +
        ".parquet"
    )

    output_path = (
        PROCESSED_DIR /
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
    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    files = get_csv_files()

    print(
        f"Found {len(files)} files"
    )

    for file_path in files:

        print("\n" + "=" * 50)
        print(file_path.name)

        df = load_file(file_path)

        df = convert_types(df)

        df = remove_invalid_flights(df)

        df = handle_missing_values(df)

        df = validate_dataframe(df)

        save_clean_file(
            df,
            file_path
        )
if __name__ == "__main__":
    main()