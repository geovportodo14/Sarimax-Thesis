"""
forecasting/pipeline/recommender.py
=====================================
Budget-aware recommendation layer.

Runs AFTER SARIMAX forecasting. Takes the predicted hourly energy values,
converts to cost, compares against the household daily budget, and generates
plain-language action messages.

Completely decoupled from the SARIMAX model.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

import pandas as pd

log = logging.getLogger("sarimax_pipeline.recommender")

# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------
BUDGET_WARNING_PCT = 0.90  # warn when predicted cost ≥ 90 % of budget
HIGH_USAGE_RANK    = 1     # top-N appliances flagged as high usage


@dataclass
class BudgetRecommendation:
    forecast_date:       str
    daily_budget_php:    float
    predicted_cost_php:  float
    budget_remaining:    float
    budget_utilization:  float          # 0.0 – 1.0+
    status:              str            # "within_budget" | "warning" | "over_budget"
    messages:            List[str] = field(default_factory=list)
    appliance_breakdown: Dict[str, float] = field(default_factory=dict)   # appliance → PHP

    @property
    def over_budget(self) -> bool:
        return self.predicted_cost_php > self.daily_budget_php


def generate_recommendations(
    appliance_forecasts: Dict[str, "ApplianceForecast"],    # type: ignore[name-defined]
    tariff: float,
    daily_budget: float,
    forecast_date: str,
) -> BudgetRecommendation:
    """
    Parameters
    ----------
    appliance_forecasts : dict mapping appliance name → ApplianceForecast
    tariff              : PHP per kWh
    daily_budget        : household daily budget in PHP
    forecast_date       : YYYY-MM-DD string

    Returns
    -------
    BudgetRecommendation with status, utilization, and plain-language messages.
    """
    # ── Compute costs per appliance ───────────────────────────────────────────
    breakdown: Dict[str, float] = {}
    for name, fc in appliance_forecasts.items():
        cost = round(fc.total_kwh * tariff, 4)
        breakdown[name] = cost

    total_cost     = sum(breakdown.values())
    remaining      = daily_budget - total_cost
    utilization    = total_cost / daily_budget if daily_budget > 0 else 0.0

    # ── Status ───────────────────────────────────────────────────────────────
    if utilization > 1.0:
        status = "over_budget"
    elif utilization >= BUDGET_WARNING_PCT:
        status = "warning"
    else:
        status = "within_budget"

    messages: List[str] = []

    # ── Base message ──────────────────────────────────────────────────────────
    if status == "within_budget":
        messages.append(
            f"✅ Expected to stay within budget. "
            f"Predicted cost ₱{total_cost:.2f} vs. budget ₱{daily_budget:.2f}."
        )
    elif status == "warning":
        messages.append(
            f"⚠️ Approaching daily budget limit. "
            f"Predicted cost ₱{total_cost:.2f} (≥90 % of ₱{daily_budget:.2f})."
        )
    else:
        overage = abs(remaining)
        messages.append(
            f"🚨 Expected to EXCEED daily budget by ₱{overage:.2f}. "
            f"Predicted cost ₱{total_cost:.2f}, budget ₱{daily_budget:.2f}."
        )

    # ── Identify highest-usage appliance ──────────────────────────────────────
    if breakdown:
        top_appliance = max(breakdown, key=breakdown.get)  # type: ignore[arg-type]
        top_cost = breakdown[top_appliance]
        pct = (top_cost / total_cost * 100) if total_cost > 0 else 0
        messages.append(
            f"📊 Highest usage: {top_appliance.replace('_', ' ').title()} "
            f"(₱{top_cost:.2f}, {pct:.0f}% of predicted daily spend)."
        )

    # ── Aircon-specific peak-hour advisory ───────────────────────────────────
    if "aircon" in appliance_forecasts and status in ("warning", "over_budget"):
        aircon_fc = appliance_forecasts["aircon"]
        hourly    = pd.Series(
            aircon_fc.predicted_energy,
            index=pd.to_datetime(aircon_fc.timestamps),
        )
        # Identify top-4 peak hours for aircon
        peak_hours = hourly.nlargest(4).index.strftime("%H:00").tolist()
        messages.append(
            f"💡 Consider reducing aircon runtime during peak hours: "
            f"{', '.join(peak_hours)}. This could save ₱"
            f"{(hourly.nlargest(4).sum() * tariff):.2f}."
        )

    # ── Generic reduction tip ─────────────────────────────────────────────────
    if status in ("warning", "over_budget"):
        messages.append(
            "💡 Tips: limit high-draw appliances during 13:00–17:00 peak rate hours; "
            "set aircon to 25°C instead of 22°C; unplug standby devices overnight."
        )

    log.info(
        "[Recommender] date=%s | cost=₱%.2f | budget=₱%.2f | status=%s",
        forecast_date, total_cost, daily_budget, status,
    )

    return BudgetRecommendation(
        forecast_date       = forecast_date,
        daily_budget_php    = round(daily_budget, 4),
        predicted_cost_php  = round(total_cost, 4),
        budget_remaining    = round(remaining, 4),
        budget_utilization  = round(utilization, 4),
        status              = status,
        messages            = messages,
        appliance_breakdown = breakdown,
    )
