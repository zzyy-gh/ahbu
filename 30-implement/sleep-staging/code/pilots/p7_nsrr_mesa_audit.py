"""
Spec: 20-plan/sleep-staging/pilots-README.md#P-7

P-7 — NSRR token validation + MESA AHI distribution sanity.

Question: (a) Is NSRR_TOKEN valid against an authenticated MESA endpoint?
(b) Does the MESA covariates file load and contain a per-subject AHI
column? (c) Is the empirical severe-OSA stratum (AHI >= 30) >= 10 % of
the cohort (i.e. >= ~205 of 2,056), so that the smallest stratum after
the 90/10 split is >= 185 subjects (the protocol-lock §3 §scope-(a)-power-story
conditional kill threshold)?

Success criteria:
  (a) Token validation returns HTTP 200 from a token-required endpoint.
  (b) MESA covariates CSV loads and exposes an AHI column.
  (c) Severe-OSA fraction >= 10 %.

Token policy: NSRR_TOKEN lives in `.env` as `os.environ['NSRR_TOKEN']`.
NEVER print the token value. Only authentication-result booleans are
recorded.

Per pilots-README §P-7, if the token is missing the pilot fails honestly
with reason "NSRR_TOKEN env var not set — token-gated probe blocked";
this is a real outcome and is not papered over.
"""

import argparse
import io
import json
import os
import re
import sys
import time
from pathlib import Path


# Token-validation endpoint. The pilot spec mentioned `/api/v1/me.json`
# but that path returns 404 on the live API as of 2026-05-03. The working
# token-validation endpoint is `/api/v1/account/profile.json`, which
# returns `{"authenticated": true, "username": "..."}` when the token
# is valid (and `{"authenticated": false}` anonymous). Verified by
# data-plumber probe on 2026-05-03.
NSRR_TOKEN_VALIDATION_URL = "https://sleepdata.org/api/v1/account/profile.json"

# MESA covariates: NSRR distributes a covariates CSV inside the MESA
# Sleep dataset. The discoverable URL pattern is the dataset-files
# endpoint at https://sleepdata.org/datasets/mesa/files. The covariates
# CSV is `mesa-sleep-dataset-0.X.0.csv` under `datasets/`. We try a list
# of plausible locations (latest first) and fall back to a directory
# listing via the API.
MESA_COVARIATES_CANDIDATE_URLS = (
    # Verified live by data-plumber 2026-05-03 via NSRR API listing
    # (api/v1/datasets/mesa/files.json). Current version is 0.8.0.
    "https://sleepdata.org/datasets/mesa/files/m/browser/datasets/mesa-sleep-dataset-0.8.0.csv",
    "https://sleepdata.org/datasets/mesa/files/datasets/mesa-sleep-dataset-0.8.0.csv",
    "https://sleepdata.org/datasets/mesa/files/datasets/mesa-sleep-dataset-0.7.0.csv",
    "https://sleepdata.org/datasets/mesa/files/datasets/mesa-sleep-dataset-0.6.0.csv",
    "https://sleepdata.org/datasets/mesa/files/datasets/mesa-sleep-dataset-0.5.0.csv",
)

# MESA AHI column candidates. NSRR's MESA covariates file historically
# exposes AHI at desat thresholds 3 % and 4 % under multiple names; we
# search for any of these in priority order.
AHI_COLUMN_CANDIDATES = (
    "ahi_a0h3",       # all-event AHI at 3 % desat (most common)
    "ahi_a0h3a",
    "ahi_a0h4",       # all-event AHI at 4 % desat
    "ahi_a0h4a",
    "ahi",
    "ahi_overall",
    "rdi",
    "rdi3p",
    "rdi4p",
)


def _scrub(text: str, token: str) -> str:
    """Belt-and-braces: strip the token (or its prefix) from any string
    that might be logged. The pilot pipes this through every error path
    that touches the network so we never write the token to a result file
    even if requests/urllib3 echoes the URL on failure."""
    if not text or not token:
        return text
    out = text.replace(token, "<TOKEN_REDACTED>")
    # also redact the auth_token=... query-param shape just in case
    out = re.sub(r"auth_token=[^&\s\"\']+", "auth_token=<REDACTED>", out)
    return out


def _validate_token(token: str, timeout_sec: float = 30.0) -> dict:
    """HTTP GET the token-validation endpoint. Returns dict with
    `http_status`, `authenticated` (bool|None), `username_present`.
    Never logs the token. Uses the Authorization header (not URL query)
    so the token doesn't end up in error strings if the request fails."""
    try:
        import requests  # type: ignore[import-not-found]
    except ImportError:
        return {
            "http_status": None,
            "authenticated": None,
            "error": "`requests` not installed; pip install requests",
        }

    # NSRR's API only honours auth via the `auth_token` query param;
    # `Authorization: Token token=...` is silently ignored (returns
    # `authenticated:false`). _scrub() below removes the token from any
    # error string before it's logged.
    try:
        resp = requests.get(
            NSRR_TOKEN_VALIDATION_URL,
            params={"auth_token": token},
            timeout=timeout_sec,
        )
    except Exception as e:  # noqa: BLE001
        return {
            "http_status": None,
            "authenticated": None,
            "error": _scrub(f"network error: {e}", token),
        }

    out: dict = {
        "http_status": resp.status_code,
        "endpoint": NSRR_TOKEN_VALIDATION_URL,
    }
    if resp.status_code != 200:
        out["authenticated"] = False
        out["error"] = f"HTTP {resp.status_code} from token-validation endpoint"
        return out

    try:
        body = resp.json()
    except Exception as e:  # noqa: BLE001
        out["authenticated"] = None
        out["error"] = f"could not parse JSON response: {e}"
        return out

    out["authenticated"] = bool(body.get("authenticated", False)) or "username" in body
    out["username_present"] = "username" in body and bool(body["username"])
    return out


def _download_mesa_covariates(token: str, timeout_sec: float = 120.0) -> dict:
    """Try the candidate covariates URLs in order; return the first that
    loads as a non-empty CSV. Returns dict with `csv_text`, `source_url`,
    or `error`."""
    try:
        import requests  # type: ignore[import-not-found]
    except ImportError:
        return {"error": "`requests` not installed; pip install requests"}

    last_err: str | None = None
    for url in MESA_COVARIATES_CANDIDATE_URLS:
        try:
            resp = requests.get(
                url,
                params={"auth_token": token},
                timeout=timeout_sec,
                allow_redirects=True,
            )
        except Exception as e:  # noqa: BLE001
            last_err = _scrub(f"{url}: network error: {e}", token)
            continue
        if resp.status_code != 200:
            last_err = f"{url}: HTTP {resp.status_code}"
            continue
        # Some endpoints serve HTML (DAR not approved → server quietly
        # redirects to the dataset's file-browser HTML page rather than
        # returning the CSV). Verified empirically 2026-05-03 by
        # data-plumber: a 596 KB harmonized-CSV and the 7.6 MB main CSV
        # both return HTML for a token-only account, while same-folder
        # data-dictionary CSVs and PDFs return as expected. Treat HTML
        # response → DAR-not-approved.
        text = resp.text
        if not text or text.lstrip().startswith("<") or "text/html" in (resp.headers.get("Content-Type") or ""):
            last_err = (
                f"{url}: server returned HTML, not CSV. Most likely cause: "
                "MESA Data Access Request (DAR) not yet approved for this "
                "account. Token validates (read-only metadata access works) "
                "but bulk covariate downloads require an approved DAR signed "
                "via https://sleepdata.org/datasets/mesa. This is risk-register "
                "R-1 materializing: token tier insufficient for downloads."
            )
            continue
        # Light sanity: must have header row with comma + at least 50 lines
        if "," not in text.split("\n", 1)[0] or len(text.splitlines()) < 50:
            last_err = f"{url}: response too small / not a covariates table"
            continue
        return {"csv_text": text, "source_url": url}

    return {
        "error": last_err
        or "no candidate URL returned a covariates CSV",
        "candidates_tried": list(MESA_COVARIATES_CANDIDATE_URLS),
        "remediation": (
            "Find the current covariates URL at "
            "https://sleepdata.org/datasets/mesa/files (browse to "
            "datasets/ and copy the latest mesa-sleep-dataset-*.csv link). "
            "Pass via --covariates-url."
        ),
    }


def _compute_ahi_distribution(csv_text: str) -> dict:
    """Parse the covariates CSV and compute the AHI-band distribution.
    Returns dict with band counts, total, severe fraction, and the AHI
    column name actually used."""
    try:
        import pandas as pd
    except ImportError:
        return {"error": "pandas not installed; pip install pandas"}

    try:
        df = pd.read_csv(io.StringIO(csv_text))
    except Exception as e:  # noqa: BLE001
        return {"error": f"failed to parse CSV: {e}"}

    # Normalize column names to lowercase for case-insensitive lookup.
    cols_lower = {c.lower(): c for c in df.columns}
    ahi_col_used: str | None = None
    for cand in AHI_COLUMN_CANDIDATES:
        if cand.lower() in cols_lower:
            ahi_col_used = cols_lower[cand.lower()]
            break

    if ahi_col_used is None:
        # Last-resort: any column starting with 'ahi' or 'rdi'.
        for c in df.columns:
            cl = c.lower()
            if cl.startswith("ahi") or cl.startswith("rdi"):
                ahi_col_used = c
                break

    if ahi_col_used is None:
        return {
            "error": "no AHI/RDI column found in covariates CSV",
            "available_columns_sample": list(df.columns[:30]),
        }

    ahi_series = df[ahi_col_used].dropna()
    n_total = int(len(df))
    n_with_ahi = int(len(ahi_series))

    none_n = int((ahi_series < 5).sum())
    mild_n = int(((ahi_series >= 5) & (ahi_series < 15)).sum())
    moderate_n = int(((ahi_series >= 15) & (ahi_series < 30)).sum())
    severe_n = int((ahi_series >= 30).sum())

    severe_fraction = severe_n / n_with_ahi if n_with_ahi > 0 else 0.0

    # 90/10 split arithmetic from protocol-lock §3 §scope-(a)-power-story.
    severe_in_90pct_test = int(round(severe_n * 0.9))

    return {
        "ahi_column_used": ahi_col_used,
        "n_subjects_total": n_total,
        "n_subjects_with_ahi": n_with_ahi,
        "ahi_band_counts": {
            "none": none_n,
            "mild": mild_n,
            "moderate": moderate_n,
            "severe": severe_n,
        },
        "ahi_band_fractions": {
            "none": round(none_n / n_with_ahi, 4) if n_with_ahi else None,
            "mild": round(mild_n / n_with_ahi, 4) if n_with_ahi else None,
            "moderate": round(moderate_n / n_with_ahi, 4) if n_with_ahi else None,
            "severe": round(severe_fraction, 4),
        },
        "severe_fraction": round(severe_fraction, 4),
        "severe_in_90pct_test_estimate": severe_in_90pct_test,
    }


def probe(
    severe_fraction_threshold: float,
    severe_test_n_threshold: int,
    covariates_url_override: str | None,
    covariates_path_override: Path | None,
) -> dict:
    token = os.environ.get("NSRR_TOKEN")
    if not token:
        return {
            "status": "fail",
            "reason": "NSRR_TOKEN env var not set — token-gated probe blocked",
            "remediation": (
                "Set NSRR_TOKEN in `.env` (gitignored) by copying it from "
                "https://sleepdata.org/profile after login. Reload the shell "
                "(or `source .env`) before re-running."
            ),
        }

    # 1. Token validation.
    token_result = _validate_token(token)
    if not token_result.get("authenticated"):
        return {
            "status": "fail",
            "reason": "token validation failed",
            "token_validation": token_result,
            "remediation": (
                "Re-login to sleepdata.org and renew the token. Trigger "
                "R-1a mitigation (risk-register.md). Do NOT log the token."
            ),
        }

    # 2. Load MESA covariates. Prefer local file if provided.
    csv_text: str | None = None
    source: str | None = None
    download_error: dict | None = None

    if covariates_path_override is not None:
        if not covariates_path_override.exists():
            return {
                "status": "fail",
                "reason": f"--covariates-file path does not exist: {covariates_path_override}",
                "token_validation": token_result,
            }
        try:
            csv_text = covariates_path_override.read_text(encoding="utf-8", errors="replace")
            source = f"local:{covariates_path_override}"
        except Exception as e:  # noqa: BLE001
            return {
                "status": "fail",
                "reason": f"failed to read local covariates file: {e}",
                "token_validation": token_result,
            }
    else:
        urls = (
            (covariates_url_override,)
            if covariates_url_override
            else MESA_COVARIATES_CANDIDATE_URLS
        )
        # Reuse downloader, but if override given, restrict to that single URL.
        if covariates_url_override:
            try:
                import requests  # type: ignore[import-not-found]

                resp = requests.get(
                    covariates_url_override,
                    params={"auth_token": token},
                    timeout=120,
                    allow_redirects=True,
                )
                if resp.status_code == 200 and resp.text and not resp.text.lstrip().startswith("<"):
                    csv_text = resp.text
                    source = covariates_url_override
                else:
                    download_error = {
                        "error": f"override URL HTTP {resp.status_code} or non-CSV body",
                        "url": covariates_url_override,
                    }
            except Exception as e:  # noqa: BLE001
                download_error = {"error": _scrub(f"override URL network error: {e}", token)}
        else:
            dl = _download_mesa_covariates(token)
            if "csv_text" in dl:
                csv_text = dl["csv_text"]
                source = dl["source_url"]
            else:
                download_error = dl

    if csv_text is None:
        return {
            "status": "fail",
            "reason": "could not load MESA covariates CSV",
            "token_validation": token_result,
            "download_attempt": download_error,
        }

    # 3. Compute AHI distribution.
    ahi_dist = _compute_ahi_distribution(csv_text)
    if "error" in ahi_dist:
        return {
            "status": "fail",
            "reason": f"AHI distribution computation failed: {ahi_dist['error']}",
            "token_validation": token_result,
            "covariates_source": source,
            "ahi_distribution_partial": ahi_dist,
        }

    # 4. Decide pass/fail on the severe-OSA-fraction power criterion.
    severe_fraction = ahi_dist["severe_fraction"]
    severe_test_n = ahi_dist["severe_in_90pct_test_estimate"]
    fraction_ok = severe_fraction >= severe_fraction_threshold
    test_n_ok = severe_test_n >= severe_test_n_threshold

    # Both checks must pass: the headline fraction threshold (>= 10 %) and
    # the absolute-N test-partition threshold (>= 185 subjects after 90/10
    # split, the protocol-lock §3 conditional-kill bound).
    status = "pass" if (fraction_ok and test_n_ok) else "fail"
    reason = None
    if not fraction_ok:
        reason = (
            f"severe-OSA fraction {severe_fraction:.3f} < "
            f"{severe_fraction_threshold:.2f} — triggers protocol-lock §3 "
            "scope-(a) conditional kill; HEADLINE-A must be re-locked "
            "before any test access."
        )
    elif not test_n_ok:
        reason = (
            f"severe-OSA stratum after 90/10 split = ~{severe_test_n} subjects "
            f"< {severe_test_n_threshold} threshold; underpowered per "
            "protocol-lock §3 conditional kill."
        )

    return {
        "status": status,
        "reason": reason,
        "token_validation": token_result,
        "covariates_source": source,
        "ahi_distribution": ahi_dist,
        "severe_fraction_threshold": severe_fraction_threshold,
        "severe_test_n_threshold": severe_test_n_threshold,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="P-7 NSRR token validation + MESA AHI distribution sanity"
    )
    ap.add_argument(
        "--severe-fraction-threshold",
        type=float,
        default=0.10,
        help="Minimum severe-OSA fraction in the full cohort (default 10 %%).",
    )
    ap.add_argument(
        "--severe-test-n-threshold",
        type=int,
        default=185,
        help=(
            "Minimum severe-OSA stratum size after the 90/10 split "
            "(default 185, per protocol-lock §3 conditional kill)."
        ),
    )
    ap.add_argument(
        "--covariates-url",
        type=str,
        default=None,
        help=(
            "Override the auto-discovered MESA covariates URL (e.g. if NSRR "
            "renames the dataset version). Pass the direct CSV URL."
        ),
    )
    ap.add_argument(
        "--covariates-file",
        type=Path,
        default=None,
        help=(
            "Path to a locally cached MESA covariates CSV. Skips download. "
            "Token validation still runs."
        ),
    )
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    result = probe(
        severe_fraction_threshold=args.severe_fraction_threshold,
        severe_test_n_threshold=args.severe_test_n_threshold,
        covariates_url_override=args.covariates_url,
        covariates_path_override=args.covariates_file,
    )
    result["pilot"] = "P-7"
    result["spec"] = "20-plan/sleep-staging/pilots-README.md#P-7"

    # Belt-and-braces token scrub of the JSON output (defence-in-depth in
    # case any nested error string from requests/urllib3 echoed the URL).
    token_now = os.environ.get("NSRR_TOKEN")
    if token_now:
        scrubbed = _scrub(json.dumps(result), token_now)
        result = json.loads(scrubbed)

    runs_dir = Path(__file__).resolve().parents[2] / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.out or (runs_dir / f"pilot_p7_nsrr_mesa_audit_{int(time.time())}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))

    # Side-artifact: token-validation log per pilots-README §P-7 step 2.
    # Logs only the boolean, not the token.
    tv = result.get("token_validation", {}) or {}
    token_log_path = runs_dir / "nsrr_token_validation.txt"
    token_log_lines = [
        f"timestamp: {int(time.time())}",
        f"endpoint: {tv.get('endpoint', NSRR_TOKEN_VALIDATION_URL)}",
        f"http_status: {tv.get('http_status')}",
        f"authenticated: {tv.get('authenticated')}",
        f"username_present: {tv.get('username_present')}",
    ]
    token_log_path.write_text("\n".join(token_log_lines) + "\n")

    print(json.dumps(result, indent=2))
    print(f"\nWrote {out_path}")
    print(f"Wrote {token_log_path}")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
