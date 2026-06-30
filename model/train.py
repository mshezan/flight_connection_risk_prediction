from pathlib import Path

import pandas as pd

import joblib

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder

from sklearn.metrics import (
    average_precision_score,
    classification_report
)

from config import (
    FEATURE_DIR,
    MODEL_PATH,
)

def get_feature_files():
    """
    Find all feature parquet files.
    """

    files = sorted(
        FEATURE_DIR.glob("*.parquet")
    )

    print(
        f"Found {len(files)} files"
    )

    return files

def load_all_data(files):

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

    df = df.sort_values(
        "FL_DATE"
    )

    print("\nCombined Dataset")

    print(
        f"Rows: {len(df):,}"
    )

    print(
        f"Columns: {len(df.columns)}"
    )

    return df

def time_split(df):

    train_df = df[
        df["FL_DATE"]
        .dt.year
        < 2025
    ]

    test_df = df[
        df["FL_DATE"]
        .dt.year
        == 2025
    ]

    X_train = train_df.drop(
        columns=[
            "ARR_DEL15",
            "FL_DATE"
        ]
    )

    y_train = train_df[
        "ARR_DEL15"
    ]

    X_test = test_df.drop(
        columns=[
            "ARR_DEL15",
            "FL_DATE"
        ]
    )

    y_test = test_df[
        "ARR_DEL15"
    ]

    print("\nTrain Set")

    print(
        f"Rows: {len(X_train):,}"
    )

    print("\nTest Set")

    print(
        f"Rows: {len(X_test):,}"
    )

    return (
        X_train,
        X_test,
        y_train,
        y_test
    )

def build_preprocessor():

    categorical_columns = [
        "OP_UNIQUE_CARRIER",
        "ORIGIN",
        "DEST",
        "ROUTE"
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OrdinalEncoder(
                    handle_unknown="use_encoded_value",
                    unknown_value=-1
                ),
                categorical_columns
            )
        ],
        remainder="passthrough"
    )

    print("\nCategorical Columns")
    print(categorical_columns)

    return preprocessor

def build_model(preprocessor):

    model = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced"
                )
            )
        ]
    )

    print("\nModel Pipeline Built")

    return model

def train_model(
    model,
    X_train,
    y_train
):

    print("\nTraining Model...")

    model.fit(
        X_train,
        y_train
    )

    print("Training Complete")

    return model

def evaluate_model(
    model,
    X_test,
    y_test
):

    print("\nEvaluating...")

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    predictions = model.predict(
        X_test
    )

    ap_score = average_precision_score(
        y_test,
        probabilities
    )

    print("\nAverage Precision Score")

    print(ap_score)

    print("\nClassification Report")

    print(
        classification_report(
            y_test,
            predictions
        )
    )

def save_model(model):

    joblib.dump(
        model,
        MODEL_PATH
    )

    print(
        f"\nSaved model: {MODEL_PATH}"
    )

def main():

    files = get_feature_files()

    df = load_all_data(files)

    X_train, X_test, y_train, y_test = time_split(df)

    preprocessor = build_preprocessor()

    model = build_model(
        preprocessor
    )

    model = train_model(
        model,
        X_train,
        y_train
    )

    evaluate_model(
        model,
        X_test,
        y_test
    )

    save_model(model)


if __name__ == "__main__":
    main()
