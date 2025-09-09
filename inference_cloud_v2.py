from __future__ import annotations
from pathlib import Path
import io
import json
import joblib
import pandas as pd
import os
from typing import Dict, List

from azure.storage.blob import ContainerClient
from dotenv import load_dotenv

from knapsack import select_under_budget
from pricing import build_candidate_item, render_output, compute_mandatory_steps

# -------- Azure setup --------
load_dotenv()
_SAS  = os.getenv("AZURE_STORAGE_SAS")
_URL  = os.getenv("AZURE_ACCOUNT_URL")
_CONT = os.getenv("AZURE_CONTAINER_NAME")

def _get_cc() -> ContainerClient:
    if not (_SAS and _URL and _CONT):
        raise RuntimeError("Missing AZURE_STORAGE_SAS / AZURE_ACCOUNT_URL / AZURE_CONTAINER_NAME.")
    return ContainerClient(account_url=_URL, container_name=_CONT, credential=_SAS)

def _norm_prefix(prefix: str | None) -> str:
    if not prefix:
        return ""
    p = str(prefix).lstrip("/")
    return (p + "/") if p and not p.endswith("/") else p

def _download_joblib(cc: ContainerClient, blob_name: str):
    data = cc.download_blob(blob_name).readall()
    with io.BytesIO(data) as buf:
        return joblib.load(buf)

def _discover_components(cc: ContainerClient, prefix: str) -> List[str]:
    comps = set()
    for b in cc.list_blobs(name_starts_with=prefix):
        if b.name.endswith("_time.pkl"):
            comps.add(Path(b.name).stem.removesuffix("_time"))
    return sorted(comps)

# -------- Azure-backed artifact loading --------
def _load_artifacts(artifacts_dir: str, components: List[str]) -> Dict[str, dict]:
    """
    Azure implementation: downloads <prefix>/<comp>_{preprocessor,time,success_calibrated}.pkl
    """
    cc = _get_cc()
    prefix = _norm_prefix(artifacts_dir)

    bundles = {}
    for comp in components:
        pre_blob  = f"{prefix}{comp}_preprocessor.pkl"
        time_blob = f"{prefix}{comp}_time.pkl"
        succ_blob = f"{prefix}{comp}_success_calibrated.pkl"

        bundles[comp] = {
            "pre":  _download_joblib(cc, pre_blob),
            "time": _download_joblib(cc, time_blob),
            "succ": _download_joblib(cc, succ_blob),
        }
    return bundles

def inference(job: dict, artifacts_dir: str) -> dict:
    # 1) Build input frame; inject neutral access if app doesn't provide it
    df = pd.DataFrame([job])
    if "ease_of_acces(0-2)" not in df.columns:
        df["ease_of_acces(0-2)"] = 1  # neutral default

    # 2) Discover components in Azure and load artifacts
    cc = _get_cc()
    prefix = _norm_prefix(artifacts_dir)  # "" means blobs are at container root
    components = _discover_components(cc, prefix)

    if not components:
        return render_output(mandatory_first=[], chosen=[], skipped={"_system": f"no artifacts found under '{prefix or '/'}'"})

    bundles = _load_artifacts(prefix, components)

    time_budget = int(job.get("time_budget_min", 90))
    labor_rate  = float(0.5)

    # 3) Predict per-component, build items
    items, skipped = [], {}
    for comp in components:
        b = bundles[comp]
        X = b["pre"].transform(b["pre"].add_derived.transform(df))
        t = float(b["time"].predict(X)[0])
        p = float(b["succ"].predict_proba(X)[0, 1])

        item, reason = build_candidate_item(job, comp, t, p, labor_rate, time_budget)
        if item is None:
            skipped[comp] = reason
        else:
            items.append(item)

    # 4) Optimize under time budget
    chosen = select_under_budget(items, capacity=time_budget) if items else []

    # 5) Deterministic mandatory steps
    selected_components = [it["component"] for it in chosen]
    mandatory = compute_mandatory_steps(job, selected_components)

    # 6) Shape final output
    return render_output(mandatory, chosen, skipped)


# job = {
#     "year": 2019,
#     "odometer": 80000,
#     "grade_of_rust(0-5)": 0,
#     "accident_zone": "none",
#     "severity_of_accident(0-5)": 0,
#     "is_flooded": 0,
#     "vehicle_type": "combustion",
#     "time_budget_min": 90,
# }
#
# print(json.dumps(inference(job, artifacts_dir=""), indent=2))