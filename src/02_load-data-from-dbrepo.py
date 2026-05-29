"""Load the frost-day modelling data from DBRepo.

The experiment should call ``load_frost_day_data()`` instead of reading a local
CSV file. The script reads DBRepo connection settings from ``.env`` and returns
the usual ``X`` and ``y`` objects for model training.

The DBRepo view contains the physical weather columns. Month, day-of-year, and
the frost-day label are small derived columns, so they are added here after the
API call. ``temp_min_c`` is used to create the label, but is not used as a model
feature because that would leak the answer into the input data.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from requests.auth import HTTPBasicAuth


def load_env_file() -> None:
    """Load .env from either the current folder or the repository root."""
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parents[1] / ".env",
    ]
    for env_path in candidates:
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())
        return


load_env_file()

DEFAULT_FEATURE_COLUMNS = [
    "obs_month",
    "obs_day_of_year",
    "temp_mean_c",
    "temp_max_c",
    "precipitation_mm",
    "sunshine_h",
    "humidity_pct",
    "visibility_m",
]
TARGET_COLUMN = "is_frost_day"


class DBRepoError(RuntimeError):
    """Raised when DBRepo cannot provide usable model data."""


def _auth_from_env() -> HTTPBasicAuth | None:
    username = os.getenv("DBREPO_USERNAME")
    password = os.getenv("DBREPO_PASSWORD", "").strip()
    if username and password:
        return HTTPBasicAuth(username, password)
    return None


def _feature_view_endpoint(page: int, size: int) -> str:
    base_url = os.getenv("DBREPO_ENDPOINT", "").rstrip("/")
    database_id = os.getenv("DATABASE_ID")
    view_id = os.getenv("DBREPO_FEATURE_VIEW_ID")

    if not base_url or not database_id or not view_id:
        raise DBRepoError(
            "Set DBREPO_ENDPOINT, DATABASE_ID, and DBREPO_FEATURE_VIEW_ID in .env"
        )
    return f"{base_url}/api/v1/database/{database_id}/view/{view_id}/data?page={page}&size={size}"


def _observation_table_endpoint(page: int, size: int) -> str:
    base_url = os.getenv("DBREPO_ENDPOINT", "").rstrip("/")
    database_id = os.getenv("DATABASE_ID")
    table_id = os.getenv("OBS_TABLE_ID")

    if not base_url or not database_id or not table_id:
        raise DBRepoError(
            "Set DBREPO_ENDPOINT, DATABASE_ID, and OBS_TABLE_ID in .env"
        )
    return f"{base_url}/api/v1/database/{database_id}/table/{table_id}/data?page={page}&size={size}"



def _request_json(url: str) -> Any:
    try:
        response = requests.get(
            url,
            auth=_auth_from_env(),
            headers={"Accept": "application/json"},
            timeout=60,
        )
        response.raise_for_status()
    except requests.ConnectionError as exc:
        raise DBRepoError(f"Could not connect to DBRepo at {url}") from exc
    except requests.Timeout as exc:
        raise DBRepoError(f"DBRepo request timed out at {url}") from exc
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        body = exc.response.text[:500] if exc.response is not None else ""
        raise DBRepoError(f"DBRepo returned HTTP {status} for {url}: {body}") from exc

    try:
        return response.json()
    except ValueError as exc:
        raise DBRepoError(f"DBRepo response from {url} was not valid JSON") from exc


def _rows_from_payload(payload: Any) -> list[Any]:
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        raise DBRepoError("DBRepo response must be a JSON object or list.")
    for key in ("data", "rows", "results", "items"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
    raise DBRepoError("DBRepo response did not contain tabular rows.")


def _page_count_from_payload(payload: Any) -> int | None:
    if not isinstance(payload, dict):
        return None
    for key in ("total_pages", "totalPages", "pages"):
        value = payload.get(key)
        if isinstance(value, int):
            return value
    page_info = payload.get("page")
    if isinstance(page_info, dict):
        for key in ("total_pages", "totalPages", "pages"):
            value = page_info.get(key)
            if isinstance(value, int):
                return value
    return None


def _request_all_rows(endpoint_builder, page_size: int = 10000) -> list[Any]:
    rows: list[Any] = []
    page = 0
    total_pages: int | None = None

    while total_pages is None or page < total_pages:
        payload = _request_json(endpoint_builder(page=page, size=page_size))
        page_rows = _rows_from_payload(payload)
        rows.extend(page_rows)

        total_pages = _page_count_from_payload(payload)
        if total_pages is None and len(page_rows) < page_size:
            break
        page += 1

    return rows


def _frame_from_rows(rows: list[Any]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    if isinstance(rows[0], dict):
        return pd.DataFrame(rows)
    raise DBRepoError("DBRepo returned row arrays without column names.")


def _derive_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Add date features, the frost label, and keep complete rows."""
    frame = frame.copy()
    frame["obs_date"] = pd.to_datetime(frame["obs_date"])
    frame["obs_month"] = frame["obs_date"].dt.month
    frame["obs_day_of_year"] = frame["obs_date"].dt.day_of_year
    frame["temp_min_c"] = pd.to_numeric(frame["temp_min_c"], errors="coerce")
    frame[TARGET_COLUMN] = (frame["temp_min_c"] < 0).astype(int)
    required = DEFAULT_FEATURE_COLUMNS + ["temp_min_c", TARGET_COLUMN]
    frame = frame.dropna(subset=required)
    return frame


def load_frost_day_frame() -> pd.DataFrame:
    """Return the ML-ready frame loaded exclusively from DBRepo view endpoint."""
    rows = _request_all_rows(_feature_view_endpoint)
    frame = _frame_from_rows(rows)

    if "temp_min_c" not in frame.columns:
        raise DBRepoError(
            f"DBRepo view is missing expected columns. Got: {list(frame.columns)}"
        )

    frame = _derive_features(frame)
    return frame


def load_observation_table_frame() -> pd.DataFrame:
    """Load the DBRepo base observation table and derive the same ML columns."""
    rows = _request_all_rows(_observation_table_endpoint)
    frame = _frame_from_rows(rows)

    if "temp_min_c" not in frame.columns:
        raise DBRepoError(
            f"DBRepo observation table is missing expected columns. Got: {list(frame.columns)}"
        )

    return _derive_features(frame)


def load_frost_day_data() -> tuple[pd.DataFrame, pd.Series]:
    """Return model features X and labels y loaded exclusively from DBRepo.

    temp_min_c is excluded from X to prevent label leakage.
    """
    frame = load_frost_day_frame()
    X = frame[DEFAULT_FEATURE_COLUMNS].apply(pd.to_numeric, errors="raise")
    y = frame[TARGET_COLUMN].astype(int)
    return X, y


def _compare_frames(left: pd.DataFrame, right: pd.DataFrame) -> dict[str, Any]:
    import numpy as np

    cols = DEFAULT_FEATURE_COLUMNS + [TARGET_COLUMN]
    missing_left = [col for col in cols if col not in left.columns]
    missing_right = [col for col in cols if col not in right.columns]
    if missing_left or missing_right:
        raise DBRepoError(
            f"Missing columns for verification. left={missing_left}, right={missing_right}"
        )

    sort_cols = ["obs_date"] + cols if "obs_date" in left.columns else cols
    left_subset = left[sort_cols].sort_values(sort_cols).reset_index(drop=True)
    right_subset = right[sort_cols].sort_values(sort_cols).reset_index(drop=True)

    row_match = len(left_subset) == len(right_subset)
    numeric_match = False
    label_match = False

    if row_match:
        numeric_match = bool(np.allclose(
            left_subset[DEFAULT_FEATURE_COLUMNS].to_numpy(dtype=float),
            right_subset[DEFAULT_FEATURE_COLUMNS].to_numpy(dtype=float),
            atol=1e-6,
            equal_nan=True,
        ))
        label_match = bool(
            (left_subset[TARGET_COLUMN].values == right_subset[TARGET_COLUMN].values).all()
        )

    return {
        "left_rows": len(left_subset),
        "right_rows": len(right_subset),
        "row_match": row_match,
        "numeric_match": numeric_match,
        "label_match": label_match,
        "identical": row_match and numeric_match and label_match,
    }


def verify_against_local(local_csv_path: str) -> dict[str, Any]:
    """Compare DBRepo-loaded data with the earlier local CSV version."""
    local_df = _derive_features(pd.read_csv(local_csv_path))
    api_frame = load_frost_day_frame()
    result = _compare_frames(local_df, api_frame)
    result["local_rows"] = result.pop("left_rows")
    result["api_rows"] = result.pop("right_rows")

    print("=== DBRepo vs local CSV verification ===")
    for k, v in result.items():
        print(f"  {k}: {v}")
    if result["identical"]:
        print("  RESULT: DBRepo data is identical to local CSV.")
    else:
        print("  RESULT: MISMATCH detected.")
    return result


def verify_against_dbrepo_table() -> dict[str, Any]:
    """Compare the feature view API with the uploaded DBRepo source table."""
    source_frame = load_observation_table_frame()
    api_frame = load_frost_day_frame()
    result = _compare_frames(source_frame, api_frame)
    result["source_table_rows"] = result.pop("left_rows")
    result["feature_view_rows"] = result.pop("right_rows")

    print("=== DBRepo feature view vs DBRepo uploaded table verification ===")
    for k, v in result.items():
        print(f"  {k}: {v}")
    if result["identical"]:
        print("  RESULT: Feature view data matches the uploaded DBRepo table after applying the same transformations.")
    else:
        print("  RESULT: MISMATCH detected.")
    return result


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--dbrepo-table-check":
        verify_against_dbrepo_table()
    elif len(sys.argv) > 1:
        verify_against_local(sys.argv[1])
    else:
        X, y = load_frost_day_data()
        print(f"Loaded {len(X)} rows from DBRepo.")
        print(f"Features : {list(X.columns)}")
        print(f"Frost days: {y.sum()} / {len(y)}")
        print(X.head())
