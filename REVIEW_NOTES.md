# Phase 1 repairs

## Concrete changes

- Removed embedded local database credentials and the MySQL dependency from the current notebook.
- Fixed execution-order problems and removed unsupported historical 93% recall claims from the current workflow.
- Defined prediction timing, excluded post-event/aggregated predictors, isolated users across splits, and prevented categorical target-encoding leakage.
- Added probability metrics and budgeted ranking lift instead of optimizing recall alone.

## Scope and remaining limits

Negative downsampling changes prevalence, so these scores and rates cannot be reported as population or campaign CTR. Without timestamps, temporal drift remains untested. Ranking lift is measured only on this downsampled benchmark; absolute click probability needs calibration on natural-prevalence logs.

Two compact model candidates (one for text) replace expensive grids and unnecessary neural networks.
The current notebook is an executable walkthrough of the Python implementation. Historical versions remain in Git history.
Source folders and unrelated local datasets were read without modification during discovery.

## Validation

- Full CLI execution generated the committed metrics, reports, plots, and held-out predictions.
- The updated notebook was executed with a fresh kernel.
- Saved-model batch inference was checked against the corresponding held-out scores.
- 10 focused pytest checks passed; they cover label validation, split isolation, preprocessing leakage, and task-specific failure cases.

See [results/REPORT.md](results/REPORT.md) and [results/metrics.json](results/metrics.json) for measured evidence.
