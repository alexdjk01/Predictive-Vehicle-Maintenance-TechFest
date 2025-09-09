from __future__ import annotations
from typing import Dict, Tuple, Optional, Iterable, List


BASE_PRICES_EUR: Dict[str, float] = {
    "battery": 40.0, "alternator": 70.0, "starter": 55.0, "radiator": 45.0,
    "headlight": 35.0, "bumper": 30.0, "door_front": 80.0, "door_rear": 70.0,
    "seat_front": 60.0, "mirror_side": 30.0,
}

VT_MULTIPLIER: Dict[str, Dict[str, float]] = {
    "combustion": {"battery": 1.0, "alternator": 1.0, "starter": 1.0},
    "hybrid":     {"battery": 1.8, "alternator": 1.0, "starter": 1.0},
    "ev":         {"battery": 6.0, "alternator": 0.0, "starter": 0.0},
}

MASS_KG: Dict[str, float] = {
    "battery": 12.0, "alternator": 6.0, "starter": 5.0, "radiator": 7.0,
    "headlight": 1.2, "bumper": 5.5, "door_front": 28.0, "door_rear": 26.0,
    "seat_front": 18.0, "mirror_side": 0.9,
}

SCRAP_EUR_PER_KG_DEFAULT: float = 0.6
CONSUMABLES_REUSE: Dict[str, float] = {"battery": 1.0, "headlight": 0.5, "mirror_side": 0.2}
CONSUMABLES_RECYCLE: Dict[str, float] = {"battery": 0.5}  # else fallback to reuse consumables
REUSE_BLOCKLIST = set()  # e.g. {"airbag_module"}

EMISSION_FACTOR_DEFAULT: float = 0.35  # kgCO2e per kg (placeholder)
EMISSION_FACTOR_PER_PART: Dict[str, float] = {}  # per-part overrides (optional)


def _condition_multiplier(severity_0_5: int, rust_0_5: int, flood: int) -> float:
    m = 1.0
    m *= max(0.5, 1 - 0.08 * int(severity_0_5))  # crash damage
    m *= max(0.6, 1 - 0.07 * int(rust_0_5))      # corrosion
    if int(flood):
        m *= 0.7                                  # electrical risk
    return float(max(0.2, m))


def _age_multiplier(year: int, ref_year: int = 2025) -> float:
    age = max(0, int(ref_year) - int(year))
    return float(max(0.6, 1 - 0.02 * age))


def price_for(component: str, year: int, severity_0_5: int, rust_0_5: int,
              flood: int, vehicle_type: str) -> float:
    """Risk-adjusted resale price estimate for reuse branch."""
    base = float(BASE_PRICES_EUR.get(component, 0.0))
    if base <= 0.0:
        return 0.0

    vt_mult = VT_MULTIPLIER.get(str(vehicle_type).lower(), {}).get(component, 1.0)
    if vt_mult == 0.0:  # e.g., alternator/starter on EV
        return 0.0

    m = _age_multiplier(year) * _condition_multiplier(severity_0_5, rust_0_5, flood)
    return float(round(base * vt_mult * m, 2))


def co2_saved_kg(component: str) -> float:
    mass = float(MASS_KG.get(component, 0.0))
    ef = float(EMISSION_FACTOR_PER_PART.get(component, EMISSION_FACTOR_DEFAULT))
    return mass * ef


def _scrap_value_eur(component: str) -> float:
    return float(MASS_KG.get(component, 0.0)) * SCRAP_EUR_PER_KG_DEFAULT


def _profit_reuse_eur(component: str, success_prob: float, pred_time_min: float,
                      labor_rate: float, job: Dict) -> Optional[float]:
    """Expected profit for reuse; None if reuse disallowed."""
    if component in REUSE_BLOCKLIST:
        return None
    resale = price_for(
        component=component,
        year=int(job["year"]),
        severity_0_5=int(job["severity_of_accident"]),
        rust_0_5=int(job["grade_of_rust"]),
        flood=int(job["is_flooded"]),
        vehicle_type=str(job["vehicle_type"]),
    )
    cons = float(CONSUMABLES_REUSE.get(component, 0.0))
    labor = labor_rate * float(pred_time_min)
    return success_prob * (resale - cons) - labor


def _profit_recycle_eur(component: str, pred_time_min: float, labor_rate: float) -> float:
    scrap = _scrap_value_eur(component)
    cons = float(CONSUMABLES_RECYCLE.get(component, CONSUMABLES_REUSE.get(component, 0.0)))
    labor = labor_rate * float(pred_time_min)
    return scrap - cons - labor


def compute_mandatory_steps(job: Dict, selected_components: Iterable[str]) -> List[str]:
    """
    Deterministic safety/prep steps derived from vehicle context and planned parts.
    Order: electrical → SRS → fluids → other.
    """
    steps: List[str] = []

    # 1) Electrical safety first (always)
    steps.append("isolate_12v_battery")

    # 2) High-voltage safety for EV/Hybrid
    vt = str(job.get("vehicle_type", "")).lower()
    if vt in {"ev", "hybrid"}:
        steps.append("pull_hv_service_disconnect")
        steps.append("wait_10min_for_hv_capacitors")

    # 3) Flood handling
    if int(job.get("is_flooded", 0)) == 1:
        steps.append("flood_electrical_assessment")

    # 4) SRS safety on heavy crashes
    if int(job.get("severity_of_accident(0-5)", 0)) >= 3:
        steps.append("safe_srs_airbag_system")

    # 5) Fluids if relevant parts are planned
    comps = set(selected_components or [])
    if "radiator" in comps:
        steps.append("depressurize_cooling_circuit")
        steps.append("drain_coolant")

    # De-dup while preserving order
    seen = set()
    ordered = []
    for s in steps:
        if s not in seen:
            ordered.append(s); seen.add(s)
    return ordered


def build_candidate_item(job: Dict, component: str, pred_time_min: float, success_prob: float,
                         labor_rate: float, time_budget_min: int) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Create the per-component item with:
      reuse_profit_eur, recycle_profit_eur, co2_saved_kg, decision,
      and the 'profit' used by knapsack.

    Returns (item, None) if valid; otherwise (None, reason) to report in 'skipped'.
    """
    t = float(pred_time_min)
    p = float(success_prob)

    reuse = _profit_reuse_eur(component, p, t, labor_rate, job)    # may be None
    recycle = _profit_recycle_eur(component, t, labor_rate)        # always a float

    choose_recycle = (reuse is None) or (recycle > reuse)
    chosen = recycle if choose_recycle else float(reuse)
    decision = "recycle" if choose_recycle else "reuse"

    if t > time_budget_min:
        return None, f"task time ({t:.2f} min) > {time_budget_min}-min budget"
    if chosen <= 0:
        return None, "negative expected profit"

    return ({
        "component": component,
        "t": t,
        "p": p,
        "reuse_profit": None if reuse is None else float(reuse),
        "recycle_profit": float(recycle),
        "profit": float(chosen),     # used by knapsack
        "decision": decision,
        "co2_saved": float(co2_saved_kg(component)),
    }, None)

def render_output(mandatory_first: list, chosen: list, skipped: Dict[str, str]) -> Dict:
    """Format the final JSON payload with per-item fields and totals."""
    # deterministic order: highest profit density first
    for it in chosen:
        it["density"] = it["profit"] / max(1e-6, it["t"])
    chosen.sort(key=lambda x: (-x["density"], x["t"]))

    selected_order = [{
        "component": it["component"],
        "pred_time_min": round(it["t"], 2),
        "success_prob": round(it["p"], 2),
        "reuse_profit_eur": None if it["reuse_profit"] is None else round(it["reuse_profit"], 2),
        "recycle_profit_eur": round(it["recycle_profit"], 2),
        "co2_saved_kg": round(it["co2_saved"], 2),
        "decision": it["decision"],
    } for it in chosen]

    totals = {
        "time_min": round(sum(it["t"] for it in chosen), 2),
        "expected_profit_eur": round(sum(it["profit"] for it in chosen), 2),
        "reuse_profit_eur": round(sum((it["reuse_profit"] or 0.0) for it in chosen), 2),
        "recycle_profit_eur": round(sum(it["recycle_profit"] for it in chosen), 2),
        "co2_saved_kg": round(sum(it["co2_saved"] for it in chosen), 2),
    }

    return {
        "mandatory_first": list(mandatory_first),
        "selected_order": selected_order,
        "skipped": dict(skipped),
        "totals": totals,
    }
