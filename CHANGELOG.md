# Change log

## Phase two — 30 September 2026

- Added `phase2.py`, `review_tools.py`, executed `CTR_Phase2.ipynb`, and `CASE_STUDY.md`.
- Added independent calibration, uncertainty estimates, development-only stability checks, and error analysis.
- Updated the README to lead with current evidence while preserving its phase-one content.
- Added focused tests. Preserved existing files, phase-one results, notebooks, and Git history.
- A representative temporal benchmark was investigated through Criteo’s official dataset pages. The downloadable alternatives are substantially larger, require different schemas, and do not establish the missing original campaign’s prevalence or timestamps. No bulk archive was downloaded. Population CTR and future-campaign validation require documented impression logs; calibration alone cannot reconstruct unknown sampling.

Data provenance and download checks are documented in `data/`. File paths and before/after SHA-256 hashes
are recorded in `AUDIT/phase2-file-changes.json`. Commit and push receipts are retained in the local audit log.
