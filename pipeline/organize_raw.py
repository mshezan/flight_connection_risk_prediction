from pathlib import Path
import pandas as pd
import shutil

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"

folders = sorted(
    RAW_DIR.glob("T_ONTIME_REPORTING_*")
)

print(
    f"Found {len(folders)} folders"
)

OUTPUT_DIR = RAW_DIR / "csv"

OUTPUT_DIR.mkdir(
    exist_ok=True
)

for folder in folders:

    csv_file = (
        folder /
        "T_ONTIME_REPORTING.csv"
    )

    df = pd.read_csv(
        csv_file,
        nrows=1
    )

    date = pd.to_datetime(
        df["FL_DATE"].iloc[0]
    )

    output_name = (
        f"{date.year}_{date.month:02d}.csv"
    )

    output_path = (
        OUTPUT_DIR /
        output_name
    )

    date = pd.to_datetime(
    df["FL_DATE"].iloc[0]
    )

    output_name = (
        f"{date.year}_{date.month:02d}.csv"
    )

    output_path = (
        RAW_DIR /
        output_name
    )

    shutil.move(
        csv_file,
        output_path
    )

    folder.rmdir()

    print(
        f"Moved {output_name}"
    )