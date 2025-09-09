from __future__ import annotations
from pathlib import Path
import pandas as pd
import joblib
import json

from pvmt.ml.utils.knapsack import select_under_budget
from pvmt.ml.utils.pricing import build_candidate_item, render_output, compute_mandatory_steps

import sys
import pvmt.ml.features as _features   # if your file is src/pvmt/ml/features.py
sys.modules["features"] = _features

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"


def _load_artifacts(artifacts_dir: str, components: list[str]):
    base = Path(artifacts_dir)
    return {
        comp: {
            "pre":  joblib.load(base / f"{comp}_preprocessor.pkl"),
            "time": joblib.load(base / f"{comp}_time.pkl"),
            "succ": joblib.load(base / f"{comp}_success_calibrated.pkl"),
        }
        for comp in components
    }

def inference(job: dict, artifacts_dir: str | Path = ARTIFACTS_DIR) -> dict:
    """
    Run per-component time/success predictions, select under time budget,
    add mandatory steps, and shape the final response.
    """
    # 1) Build input frame; inject neutral access if app doesn't provide it
    df = pd.DataFrame([job])
    # inject neutral access if app doesn't provide it (name expected by preprocessor)
    if "ease_of_acces" not in df.columns:
        df["ease_of_acces"] = job.get("ease_of_acces", 1)

    # 2) Discover components and load artifacts
    base = Path(artifacts_dir).resolve()
    components = sorted(p.stem.replace("_time", "") for p in base.glob("*_time.pkl"))
    if not components:
        return render_output(mandatory_first=[], chosen=[], skipped={"_system": "no artifacts found"})

    bundles = _load_artifacts(str(base), components)

    time_budget = int(job.get("time_budget_min", 90))
    labor_rate  = float(0.5)

    # 3) Predict per-component, build candidate items
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

    # 5) Compute deterministic mandatory steps based on job + chosen components
    selected_components = [it["component"] for it in chosen]
    mandatory = compute_mandatory_steps(job, selected_components)

    # 6) Shape final output
    return render_output(mandatory, chosen, skipped)

# Debug Code


# job = {
#     "year": 2019,
#     "odometer": 80000,
#     "grade_of_rust(0-5)": 0,
#     "accident_zone": "none",
#     "severity_of_accident(0-5)": 0,
#     "is_flooded": 0,
#     "vehicle_type": "combustion",
#     "time_budget_min": 90,
#     "grade_of_rust": 0,
#     "ease_of_acces": 0,
#     "severity_of_accident" :0
# }
#
# print(json.dumps(inference(job, artifacts_dir="artifacts"), indent=2))