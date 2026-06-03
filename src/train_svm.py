"""Train or evaluate the SVM-combined baseline."""

from __future__ import annotations

import argparse
import pickle
from pathlib import Path

from sklearn.metrics import classification_report
from sklearn.svm import SVC

from preprocess import add_binary_labels, load_feature_table
from gpsd_features import split_features_labels


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", default="data/Data_6kGoc/features.csv")
    parser.add_argument("--out", default="models/svm_combined.pkl")
    args = parser.parse_args()

    df = add_binary_labels(load_feature_table(args.features))
    x, y = split_features_labels(df)
    model = SVC(kernel="rbf", C=1.0, gamma="scale", probability=True)
    model.fit(x, y)
    preds = model.predict(x)
    print(classification_report(y, preds))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("wb") as handle:
        pickle.dump(model, handle)


if __name__ == "__main__":
    main()

