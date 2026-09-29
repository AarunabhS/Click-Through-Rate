"""Estimate click propensity on a documented, downsampled KDD search-ad benchmark."""
from __future__ import annotations
import argparse
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from workflow import (SEED, binary_labels, input_metadata, make_splits, numeric_features,
                      require_columns, run_experiment, write_report)

ROOT = Path(__file__).resolve().parent
NUMERIC = ["depth", "position"]
CATEGORICAL = ["ad_id", "advertiser_id", "query_id", "keyword_id", "title_id", "description_id"]
# Impression is an aggregated observation count, not a pre-impression feature.
# User ID is used for holdout grouping, never treated as a numerical magnitude.
EXCLUDED = ["impression", "user_id", "url_hash", "click", "clicked", "click_time", "view_count"]


def prepare_features(frame: pd.DataFrame) -> pd.DataFrame:
    require_columns(frame, [*NUMERIC, *CATEGORICAL])
    X = numeric_features(frame, NUMERIC)
    valid = X.dropna()
    if ((valid.depth < 1) | (valid.position < 1) | (valid.position > valid.depth)).any():
        raise ValueError("Ad position must be between 1 and the session depth.")
    if not np.equal(valid.to_numpy(), np.floor(valid.to_numpy())).all():
        raise ValueError("Depth and position must be integer counts.")
    for name in CATEGORICAL:
        X[name] = frame[name].map(lambda v: str(v).strip() if pd.notna(v) else np.nan).replace("", np.nan)
    return X


def load_data(path: Path):
    frame = pd.read_csv(path, dtype={k: "string" for k in [*CATEGORICAL, "user_id", "url_hash"]})
    require_columns(frame, ["click", "user_id", *NUMERIC, *CATEGORICAL])
    binary_labels(frame.click, "click")
    initial = len(frame)
    frame = frame.drop_duplicates().reset_index(drop=True)
    X, y = prepare_features(frame), binary_labels(frame.click, "click")
    context = pd.util.hash_pandas_object(X, index=False).astype(str)
    users = frame.user_id.fillna("0").astype(str).str.strip()
    groups = users.map(lambda v: "user:"+v if v not in ["0", "", "0.0"] else "")
    groups = groups.mask(groups == "", "anonymous-context:" + context)
    return X, y, groups, {"rows_read": initial, "rows_used": len(frame), "duplicates_removed": initial-len(frame),
        "split_strategy": "grouped 60/20/20; known users and identical anonymous contexts never cross partitions",
        "excluded_features": EXCLUDED,
        "benchmark_warning": "Majority class was downsampled upstream; click scores are not population CTR estimates."}


def preprocessing():
    return ColumnTransformer([
        ("numeric", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), NUMERIC),
        ("category", make_pipeline(SimpleImputer(strategy="most_frequent"),
            OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=5, max_categories=100)), CATEGORICAL),
    ], remainder="drop")


def run(data: Path = ROOT / "data/clicks.csv", output: Path = ROOT / "results"):
    data, output = Path(data), Path(output)
    X, y, groups, info = load_data(data)
    splits = make_splits(y, groups)
    models = {
        "baseline": DummyClassifier(strategy="prior"),
        "logistic_regression": make_pipeline(preprocessing(), LogisticRegression(max_iter=600, C=0.5, random_state=SEED)),
        "random_forest": make_pipeline(preprocessing(), RandomForestClassifier(
            n_estimators=70, max_depth=12, min_samples_leaf=12, n_jobs=2, random_state=SEED)),
    }
    summary, model, predictions = run_experiment(X, y, models, output,
        {"title": "Click Through Rate / Click Propensity", "class_names": ["No click", "Clicked"], **input_metadata(data), **info},
        splits=splits, selection_metric="log_loss")
    joblib.dump({"model": model, "threshold": summary["selected_threshold"]}, output / "model.joblib")
    ranked = predictions.sort_values(summary["selected_model"]+"_score", ascending=False)
    budgets = []
    for fraction in [0.05, 0.1, 0.2, 0.5, 1.0]:
        k = max(1, int(np.ceil(fraction * len(ranked))))
        top = ranked.iloc[:k]
        rate = float(top.actual.mean())
        budgets.append({"review_fraction": fraction, "rows": k, "observed_click_rate": rate,
                        "lift_vs_test_prevalence": rate / y.iloc[splits["test"]].mean(),
                        "clicks_captured": int(top.actual.sum())})
    pd.DataFrame(budgets).to_csv(output / "ranking_lift.csv", index=False, float_format="%.8f")
    write_report(output, summary,
        "Predict whether an ad was clicked using Tencent/KDD Cup 2012 data distributed as OpenML dataset 1220. "
        "The supplied 39,948-row subset is explicitly downsampled by its publisher. "
        "Use depth, position, and categorical ad/query attributes available when selecting an ad; "
        "exclude post-event view counts, click timestamps, and aggregate impression counts. "
        "Known users are kept in one partition, and identical anonymous contexts are grouped together.",
        "Model selection minimizes validation log loss because the task needs useful click-propensity scores, "
        "rather than recall obtained by flagging almost every impression. The F1-selected threshold is a "
        "demonstration decision rule, not an ad-serving policy. `ranking_lift.csv` shows the observed clicks "
        "captured within fixed ranking budgets on the untouched test set. "
        "Upstream negative downsampling changes prevalence: predicted scores and observed rates describe this benchmark, "
        "not a campaign's actual CTR. No timestamp is supplied, so temporal drift remains untested. "
        "The original receipt-ad MySQL data is unavailable; this benchmark is a replacement and does not reproduce "
        "the historical notebook's 93% recall claim. Production CTR requires representative impression logs, "
        "calibration on natural prevalence, and a time-based holdout.")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "data/clicks.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    try:
        result = run(args.data, args.output)
    except (ValueError, OSError) as error:
        parser.exit(2, f"Input error: {error}\n")
    print(f"Selected {result['selected_model']}; test log loss={result['test']['log_loss']:.4f}; report: {args.output / 'REPORT.md'}")


if __name__ == "__main__":
    main()
