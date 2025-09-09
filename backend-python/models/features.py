from __future__ import annotations
from dataclasses import dataclass
from typing import List
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, FunctionTransformer


# -----------------------------
# Column layout specification
# -----------------------------

@dataclass
class FeatureSpec:
    cat_cols: List[str]
    num_cols: List[str]

# Categorical columns (will be one-hot encoded)
CAT_COLS = ["accident_zone", "vehicle_type"]

# Numeric columns (passed through + used to build derived features)
# Note: These match your new CSV exactly.
NUM_COLS = [
    "year",
    "odometer",
    "grade_of_rust",
    "severity_of_accident",
    "is_flooded",
    "ease_of_acces",
]

BASE_FEATURES = FeatureSpec(cat_cols=CAT_COLS, num_cols=NUM_COLS)


# -----------------------------------------
# Derived features to aid model learning
# -----------------------------------------

def _add_derived(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create extra signals that typically improve accuracy for this domain:
      - vehicle_age: older cars are usually harder (corroded fasteners, etc.)
      - log_odometer: mileage is skewed; log compresses the long tail
      - damage flags: explicit binary indicators from accident_zone
    We keep original columns too; tree models can use both.
    """
    out = df.copy()

    # Cap age into a reasonable band to avoid extreme leverage
    out["vehicle_age"] = np.clip(2025 - out["year"].astype(int), 0, 40)

    # Log transform odometer (add 1 to avoid log(0))
    out["log_odometer"] = np.log1p(out["odometer"].astype(float))

    # Simple accident-zone flags (even though we also one-hot encode, these can help)
    az = out["accident_zone"].astype(str).str.lower()
    out["front_damage"] = (az == "front").astype(int)
    out["rear_damage"]  = (az == "rear").astype(int)
    out["side_damage"]  = (az == "side").astype(int)

    return out

# Names of the derived numeric columns we just created
DERIVED_NUMERIC = ["vehicle_age", "log_odometer", "front_damage", "rear_damage", "side_damage"]


# ---------------------------------------------------
# Preprocessor (fit once in training; reuse in infer)
# ---------------------------------------------------

def make_preprocessor(feature_spec: FeatureSpec = BASE_FEATURES) -> ColumnTransformer:

    add = FunctionTransformer(_add_derived, validate=False)

    cat_encoder = OneHotEncoder(
        handle_unknown="ignore",   # safe at inference if a new label appears
        sparse_output=False        # dense ndarray output (XGBoost is fine with this)
    )

    cats = feature_spec.cat_cols
    nums = feature_spec.num_cols + DERIVED_NUMERIC

    pre = ColumnTransformer(
        transformers=[
            ("cats", cat_encoder, cats),
            ("nums", "passthrough", nums),
        ],
        remainder="drop",
    )

    # Attach the derived-step transformer for a simple two-call pipeline:
    #   df_aug = pre.add_derived.fit_transform(df_train)
    #   pre.fit(df_aug)  # then use pre.transform(...) later
    pre.add_derived = add  # duck-typed convenience
    pre.feature_names_out_ = None  # optional placeholder for downstream code

    return pre


def prepare_X(pre: ColumnTransformer, df: pd.DataFrame) -> np.ndarray:
    
    df_aug = pre.add_derived.transform(df)
    X = pre.transform(df_aug)
    return X
