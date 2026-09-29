# Click Through Rate / Click Propensity

Estimate whether a search ad will be clicked and evaluate ranking quality and probability quality on a documented public benchmark.

**Start with the [executed notebook](Click%20Through%20Rate.ipynb) or the [results report](results/REPORT.md).**
The report includes held-out predictions, a baseline, a precision–recall curve, confusion counts,
and the assumptions needed to interpret the results.

## Measured result

The validation-selected **logistic_regression** achieves test average precision **0.2890**,
precision **25.5%**, recall **58.9%**, and F1 **0.3558**.
Test log loss is **0.4397**; baseline log loss is **0.4626**.
These are the recorded benchmark results from the supplied input, not a deployment claim.

Negative downsampling changes prevalence, so these scores and rates cannot be reported as population or campaign CTR. Without timestamps, temporal drift remains untested. Ranking lift is measured only on this downsampled benchmark; absolute click probability needs calibration on natural-prevalence logs.

## Run locally

Tested with Python **3.13.2**. Use Python 3.12 or newer and the pinned requirements:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python fetch_data.py
python analysis.py
```

After the documented public input is present, the analysis runs locally without cloud services or credentials.
The downloader verifies checksums and leaves a differing existing input untouched.
For your own labelled CSV, use `python analysis.py --data path/to/input.csv --output results/custom_run`.
The data must match the [documented schema](data/README.md).

For predictions on new unlabelled rows, first run training, then:

```bash
python predict.py --data examples/new_rows.csv --output results/new_predictions.csv
```

The model bundle contains the fitted preprocessing and the validation-selected threshold.
Positive-score meanings: 0=no click; 1=at least one click. Score scales reflect the training benchmark.

## Data and modelling choices

39,948 ad-context records distributed by OpenML as Click_prediction_small. There are 33,220 no-click and 6,728 click labels before deduplication; the publisher explicitly downsampled negatives to roughly a 5:1 ratio. This is a replacement benchmark, not the original receipt-ad MySQL dataset. A label denotes at least one click in an aggregated ad context, not the click count divided by impressions. The raw CSV is kept local and restored with `fetch_data.py`; only metrics and derived results are published, since the OpenML licence field is the generic 'Public'.

Treat ad/query identifiers as categorical, not numeric magnitudes. Exclude aggregate impression count, user ID as a feature, view counts, and click timestamps. Group known users and repeated anonymous contexts so they cannot cross partitions. Compare logistic regression and a bounded random forest. Select on validation log loss; report average precision, calibration errors, and fixed-budget ranking lift.

Sources, licence, sampling, schema, and SHA-256 checksums are in [data/README.md](data/README.md).

## Reviewer map

| File | What it demonstrates |
|---|---|
| `analysis.py` | Input validation, preprocessing, bounded model comparison, held-out evaluation |
| `workflow.py` | Split isolation, validation-only decisions, metrics, report generation |
| `predict.py` | Batch inference using the saved pipeline |
| `Click Through Rate.ipynb` | Executed walkthrough with current outputs |
| `results/REPORT.md` | Findings and limitations |
| `results/metrics.csv` | Validation and test metrics for every candidate |
| `results/predictions.csv` | Auditable held-out scores and labels |
| `results/splits.csv` | Split membership for every analysed row |
| `results/metrics.json` | Input hash, package versions, seed, and run settings |
| `tests/` | Input handling, leakage controls, metric correctness |

## Verification

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The notebook and CLI call the same implementation. Fixed seeds, pinned dependencies, and recorded input hashes
make the published run reproducible. Generated model files are local and ignored by Git.
See [REVIEW_NOTES.md](REVIEW_NOTES.md) for the repairs and remaining limits.
