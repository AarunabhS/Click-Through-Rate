"""Restore the documented public input, verifying both upstream and converted hashes."""
from __future__ import annotations
import hashlib
import io
import re
import urllib.request
import zipfile
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch():
    target = ROOT / "data" / TARGET
    if target.exists():
        if sha256(target.read_bytes()) != TARGET_SHA256:
            raise ValueError("Existing input differs from the documented sample. It was left untouched; use --data with analysis.py for custom inputs.")
        print(f"Verified existing input: {target.relative_to(ROOT)}")
        return
    request = urllib.request.Request(URL, headers={"User-Agent": "portfolio-reproducibility/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        content = response.read()
    if sha256(content) != SOURCE_SHA256:
        raise ValueError("Upstream checksum mismatch; no input file was written. Review the publisher's version before updating the expected hash.")
    converted = convert(content)
    if sha256(converted) != TARGET_SHA256:
        raise ValueError("Converted checksum differs; no input file was written. Use the tested requirements.txt versions.")
    target.parent.mkdir(parents=True, exist_ok=True)
    # Never replace an existing file, even if it appeared during the download.
    with target.open("xb") as stream:
        stream.write(converted)
    print(f"Downloaded and verified: {target.relative_to(ROOT)}")


TARGET = 'clicks.csv'
URL = 'https://openml.org/data/v1/download/184157/Click_prediction_small.arff'
SOURCE_SHA256 = '76c9f98a9a11e32b05974704228811cd6ed35f535d3b0173c4e602b3f1366c20'
TARGET_SHA256 = 'a31e7ed1237d1d78ae0556e986b583360effdf2c8b5d67a009410be82ec73043'

def convert(content):
    header, text = content.decode("utf-8").split("@data", 1)
    names = [line.split()[1] for line in header.splitlines() if line.lower().startswith("@attribute")]
    string_columns = [name for name in names if name not in ["click", "impression", "depth", "position"]]
    frame = pd.read_csv(io.StringIO(text), header=None, names=names, dtype={name: "string" for name in string_columns})
    return frame.to_csv(index=False).encode("utf-8")

if __name__ == "__main__":
    try:
        fetch()
    except (ValueError, OSError) as error:
        raise SystemExit(f"Download error: {error}")
