# Data source and schema

Source: [Tencent / KDD Cup 2012, distributed through OpenML dataset 1220 (version 5)](https://www.openml.org/d/1220).

Licence: **Public, as declared by OpenML dataset metadata; upstream terms are not separately specified there**. Dataset rights are separate from project code.

39,948 ad-context records distributed by OpenML as Click_prediction_small. There are 33,220 no-click and 6,728 click labels before deduplication; the publisher explicitly downsampled negatives to roughly a 5:1 ratio. This is a replacement benchmark, not the original receipt-ad MySQL dataset. A label denotes at least one click in an aggregated ad context, not the click count divided by impressions. The raw CSV is kept local and restored with `fetch_data.py`; only metrics and derived results are published, since the OpenML licence field is the generic 'Public'.

## Schema

CSV columns: `click, impression, url_hash, ad_id, advertiser_id, depth, position, query_id, keyword_id, title_id, description_id, user_id`.

Target: `click` — 0=no click; 1=at least one click.
Extra columns are excluded by the explicit feature list in `analysis.py`.
Missing or non-binary labels are rejected, never inferred as negatives.
Numeric missing features are imputed from training data; completely missing numeric columns are rejected.

## Reproduce and verify

`python fetch_data.py` verifies the local file or downloads from the exact source above if it is missing.
Both the upstream bytes and the converted CSV are checked against the SHA-256 hashes in
[provenance.json](provenance.json). Existing differing files are left untouched.
CSV conversions are deterministic with the tested requirements.

See the [results report](../results/REPORT.md) for the actual cohort, partition sizes, and limitations.
