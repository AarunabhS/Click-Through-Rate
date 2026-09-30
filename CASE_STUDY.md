# Click Propensity and Ranking: case study

## Problem and outcome

Assess ad-context ranking, probability reliability, and error patterns under explicit sampling limits.

Average precision **0.2850**, precision **25.3%**, recall **56.4%**. Log loss **0.4411** versus baseline **0.4627**.

## Data and evaluation

The documented OpenML/Tencent benchmark is retained and deduplicated to 39,926 contexts. User/context groups remain disjoint across all four partitions. The negatives were downsampled upstream, so all score scales and observed click rates refer to the benchmark.

A calibrated model is retained only if it improves validation log loss. Cluster bootstrap resamples users/anonymous contexts. Fixed ranking budgets show positive capture and lift; validation-derived thresholds are separately tested. Depth and position error groups expose weak contexts. Three development-only group splits assess stability.

Model decisions use validation only. Preprocessing fits on fitting rows; probability calibration uses a disjoint reserve.
The test split is evaluated after model selection. Reusing known benchmarks during development is distinct from a new external validation.

## Findings, errors, and uncertainty

The [executed notebook](CTR_Phase2.ipynb) displays results and uncertainty from the same Python implementation.
[Current report](results/phase2/REPORT.md), [reliability plot](results/phase2/reliability.png),
[validation stability](results/phase2/validation_stability.csv), and [uncertainty intervals](results/phase2/uncertainty.json)
show performance with its practical limits. [Error rows](results/phase2/errors.csv) expose failures rather than hiding them.

A representative temporal benchmark was investigated through Criteo’s official dataset pages. The downloadable alternatives are substantially larger, require different schemas, and do not establish the missing original campaign’s prevalence or timestamps. No bulk archive was downloaded. Population CTR and future-campaign validation require documented impression logs; calibration alone cannot reconstruct unknown sampling.

## Reproduce

Tested with the phase-one pinned Python requirements. Use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python fetch_data.py
python phase2.py
```

Phase-one results and notebooks remain available. Phase-two outputs are written to `results/phase2/`.
Model bundles and locally retained raw inputs are ignored by Git. Data downloaders verify pinned hashes and preserve differing existing inputs.
Install `requirements-dev.txt` for `python -m pytest -q` or to execute the notebook.

## Batch prediction with the phase-two model

```bash
python predict.py --model results/phase2/model.joblib --data examples/new_rows.csv --output results/phase2/local/new_predictions.csv
```
