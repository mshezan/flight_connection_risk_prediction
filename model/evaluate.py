import joblib
import pandas as pd

from sklearn.metrics import (
    average_precision_score,
    classification_report
)

from config import (
    FEATURE_DIR,
    MODEL_PATH
)

def get_test_files():

    files = sorted(
        FEATURE_DIR.glob(
            "features_2025_*.parquet"
        )
    )

    print(
        f"Found {len(files)} test files"
    )

    return files

def load_model():

    print(
        "\nLoading Model..."
    )

    model = joblib.load(
        MODEL_PATH
    )

    print(
        "Model Loaded"
    )

    return model

def load_test_data(files):

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

    df = pd.concat(
        dfs,
        ignore_index=True
    )

    print(
        f"\nTotal Test Rows: "
        f"{len(df):,}"
    )

    y_test = df[
        "ARR_DEL15"
    ]

    X_test = df.drop(
        columns=[
            "ARR_DEL15",
            "FL_DATE"
        ]
    )

    print(
        f"Feature Columns: "
        f"{len(X_test.columns)}"
    )

    return (
        X_test,
        y_test
    )

def evaluate_model(
    model,
    X_test,
    y_test
):

    print(
        "\nEvaluating..."
    )

    probabilities = (
        model.predict_proba(
            X_test
        )[:, 1]
    )

    predictions = (
        model.predict(
            X_test
        )
    )

    ap_score = (
        average_precision_score(
            y_test,
            probabilities
        )
    )

    print(
        "\nAverage Precision Score"
    )

    print(ap_score)

    print(
        "\nClassification Report"
    )

    print(
        classification_report(
            y_test,
            predictions
        )
    )

def main():

    files = get_test_files()

    model = load_model()

    X_test, y_test = load_test_data(
        files
    )

    evaluate_model(
        model,
        X_test,
        y_test
    )


if __name__ == "__main__":
    main()