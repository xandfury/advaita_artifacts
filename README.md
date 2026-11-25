# Coverage Illusion: Measuring Android TLS Instrumentation Gaps — Artifact

If you use the datasets, please cite the paper:

```bibtex
@inproceedings{advaita2026,
  author    = {Abhinav Saxena and Joel Reardon},
  title     = {Coverage Illusion: Measuring {Android} {TLS} Instrumentation Gaps},
  booktitle = {Proceedings of the 2026 ACM SIGSAC Conference on Computer and
               Communications Security (CCS '26)},
  pages     = {3744--3758},
  year      = {2026},
  month     = nov,
  address   = {The Hague, Netherlands},
  publisher = {Association for Computing Machinery},
  location  = {The Hague, Netherlands},
  series    = {CCS '26},
  doi       = {10.1145/3830454.3846690},
  isbn      = {979-8-4007-2871-6}
}

```

## Overview

Advaita is an eBPF-based TLS instrumentation system for Android. The core
finding of the paper is that Advaita detects statistically significantly more
data recipients and PII transmissions than three widely used instrumentation
techniques (mitmproxy, Frida/objection, and AOSP source modification). The gap
arises from the fragmentation of the Android TLS stack: apps that bundle custom
TLS libraries (Meta's Fizz, ByteDance's BoringSSL fork, Chromium's Cronet,
Flutter's BoringSSL, Snapchat's static BoringSSL) evade all proxy-based and
hooking-based approaches. Advaita combines eBPF uprobes and kprobes to achieve
TLS visibility across all architectural layers, including these custom TLS stacks.

This artifact contains:

- the **redacted datasets** collected in the measurement study (Parquet),
- the **analysis pipeline** (Python/Jupyter) that reproduces every statistical
  result, table and figure in the paper from those datasets,
- the **redacted plaintext traffic captures** (`.pkt`) referenced in Section 7, and
- pre-rendered HTML exports of every notebook for reviewers who prefer not to
  execute them.

Advaita itself (the kernel module and injection tooling) is **not** part of
this artifact and is not required to reproduce any result below.

## Directory structure

```txt
.
├── README.md                     # This file
├── APPS.md                       # The 50 apps in the study (package name, version, category)
├── Dockerfile                    # Reproducible environment (optional; see "Getting started")
├── pyproject.toml                # Python dependencies
├── uv.lock                       # Locked dependency versions
│
├── notebooks/                    # Analysis notebooks, run in order
│   ├── 01_http_requests.ipynb    # Section 6.1  HTTP request detection, Cochran's Q, McNemar, protocol stratification
│   ├── 02_pii_observed.ipynb     # Section 6.2  PII detection, Friedman/Nemenyi, PII-category stratification, Figure 2
│   ├── 03_observable_gaps.ipynb  # Section 6.3  Gap analysis and custom TLS library classification, Figure 3
│   ├── 04_case_studies.ipynb     # Section 7    Co-transmission with Advertising ID, background transmissions
│   └── 05_pinning_detection.ipynb
│
├── data/                         # Redacted datasets (Parquet)
│   ├── http_requests.parquet     # One row per HTTP request, all four techniques
│   ├── pii_observed.parquet      # PII observations, foreground sessions
│   ├── pii_observed_all.parquet  # PII observations, all sessions (background analysis)
│   ├── pii_top_25.parquet        # Subset of DRs used for Figure 2
│   ├── observable_gaps.parquet   # Advaita-only traffic with TLS-library labels
│   └── pinning.parquet           # Certificate pinning results from mitmproxy error logs
│
├── packets/                      # 50 redacted plaintext traffic captures (.pkt), one per data recipient
│
├── analysis_utils/               # Shared code used by the notebooks
│   ├── stats.py                  # Cochran's Q, Friedman/Nemenyi, McNemar, chi-squared, stratified tests
│   └── shared_setup.py           # Plotting helpers, constants, mark_print
│
├── images/                       # Figures as they appear in the paper
│   ├── gaps.pdf                  # Figure 3
│   └── pii_dr_paper.pdf          # Figure 2
│
└── rendered/                     # Pre-rendered HTML of every notebook (no execution needed)
    ├── 01_http_requests.html
    ├── 02_pii_observed.html
    ├── 03_observable_gaps.html
    ├── 04_case_studies.html
    └── 05_pinning_detection.html
```

## Claims and where they are reproduced

| #  | Claim (paper section) | Notebook | Output |
|----|---|---|---|
| C1 | Advaita detects significantly more data recipients than Mitm, Frida and Aosp-Sci; Cochran's Q, Friedman, and all six pairwise McNemar tests are significant (Section 6.1) | `01_http_requests.ipynb` | Tables 3, 4 |
| C2 | Advaita's detection rate does not vary with HTTP protocol version, while the other three techniques degrade on HTTP/2 and HTTP/3 (Section 6.1) | `01_http_requests.ipynb` | Table 5 |
| C3 | Advaita detects significantly more PII-transmitting data recipients; five of six pairwise differences are significant; the other techniques under-detect Account and Location data (Section 6.2) | `02_pii_observed.ipynb` | Figure 2, Table 6, Section 6.2 statistics |
| C4 | Unobserved traffic results from several interacting factors, not certificate pinning alone (Section 6.3) | `03_observable_gaps.ipynb` | Figure 3, Section 6.3 counts |
| C5 | PII co-transmission with the Advertising ID; Advaita-exclusive DR–PII pairs; persistent device identifiers (Section 7.1) | `04_case_studies.ipynb` | Table 7 |
| C6 | Background transmissions (Section 7.2) | `04_case_studies.ipynb` | Section 7.2 counts |
| C7 | Certificate pinning detection and classification (Appendix D) | `05_pinning_detection.ipynb` | --- |

## Requirements

- Python 3.12 or newer (the lock file was generated with 3.14)
- [`uv`](https://docs.astral.sh/uv/) **or** Docker
- ~2 GB free disk space
- Any OS; tested on Ubuntu 22.04 and macOS 14. No GPU, no network access after
  installing dependencies.

Each notebook completes in under five minutes on a laptop.

## Getting started

### Option A: `uv` (fastest)

```bash
uv sync
uv run jupyter lab notebooks/
```

Open `01_http_requests.ipynb` and run all cells. It should print
"165,813 HTTP streams to 2,098 unique hosts" in the first output cell and end
with Table 5.

### Option B: Docker (fully pinned environment)

```bash
docker build -t advaita-artifact .
docker run --rm -p 8888:8888 advaita-artifact
```

Open the URL printed in the terminal. The container has the repository mounted
at `/artifact` with all dependencies installed.

### Running everything non-interactively

```bash
for nb in notebooks/*.ipynb; do
  uv run jupyter nbconvert --to html --execute "$nb" --output-dir=rendered/
done
```

This re-executes every notebook and overwrites `rendered/`. Diff against the
shipped versions to confirm identical numbers.

## Data description

All datasets are Apache Parquet.

| File | Rows | Unit | Columns |
|---|---|---|---|
| `http_requests.parquet` | 166,528 | one HTTP request | `uuid`, `timestamp`, `host`, `path`, `app`, `company`, `method`, `http_stream_type`, `vantage_type` |
| `pii_observed.parquet` | 77,242 | one PII observation, foreground sessions | `app`, `host`, `ip`, `port`, `pii_type`, `time`, `dir`, `uuid`, `decoders`, `pii_label`, `http_stream_type`, `vantage_type`, `app_test`, `clientrandom`, `tls_lib`, `company` |
| `pii_observed_all.parquet` | 93,167 | one PII observation, all sessions (adds background transmissions) | same as `pii_observed.parquet` |
| `pii_top_25.parquet` | — | subset of `pii_observed.parquet` | same as `pii_observed.parquet`; the DRs shown in Figure 2 |
| `observable_gaps.parquet` | 21,883 | one Advaita-only TLS stream | `uuid`, `clientrandom`, `app_test`, `connection_id`, `stream_id`, `direction`, `source`, `timestamp_us`, `host`, `host_src`, `ip`, `port`, `frame_number`, `appname`, `uid`, `pid`, `comm`, `is_quic`, `protocol`, `http_stream_type`, `tls_lib`, `total_bytes`, `company` |
| `pinning.parquet` | 578 | one mitmproxy TLS error | `host`, `vantage_type`, `ip`, `app_test`, `mitm_lines`, `uid`, `pid`, `app`, `comm`, `logcat_evidence`, `company`, `pinning_type_label` |

Column conventions: `vantage_type` is one of `Advaita`, `Mitm`, `Frida`,
`Aosp-Sci`. `company` is the data recipient after host-to-company mapping.
`app` / `appname` is the package name (see `APPS.md`). `app_test` identifies the
capture session. `uuid` is a per-request capture identifier, not a device
identifier. `ip` is the server-side address. `pii_type` is the PII category
(see Table 1 in the paper); `pii_label` is the capture tool's annotation name
for the match. `tls_lib` is the TLS library that produced the stream.
`clientrandom` is the `TLS ClientHello` random, used to join streams to keys.

### Redaction

The datasets and captures have been redacted so that no device, account or
location identifier from the test device remains:

- In `http_requests.parquet`, every URL parameter value in `path` is replaced
  by `[REDACTED]`; path segments carrying identifiers (UUIDs, long hex, Base64
  blobs, coordinates, `/users/<id>/`-style segments) are redacted as well. All
  other columns are unmodified.
- In `packets/*.pkt`, every identifier value is replaced by `[REDACTED]`.

Redaction does not affect any reported number: the analysis keys on `company`,
`pii_type`, `http_stream_type` and `vantage_type`, none of which are redacted.
Residual identifier-shaped strings in `path` are content hashes and CDN asset
names, inspected individually before release.

## Statistical tests

`analysis_utils/stats.py` provides the functions used across notebooks:

- `perform_cochran` — Cochran's Q on binary detection, with Kendall's W.
- `perform_friedman` — Friedman test on per-subject counts, with Nemenyi post-hoc.
- `perform_mcnemar_pairwise` — pairwise McNemar tests; p-values are
  Bonferroni-adjusted and compared against α = 0.05.
- `perform_within_category` — Cochran's Q within each stratum (HTTP version or
  PII group). p-values are uncorrected.
- `perform_between_category` — chi-squared test of independence per technique
  across strata; reports the minimum expected cell count.
