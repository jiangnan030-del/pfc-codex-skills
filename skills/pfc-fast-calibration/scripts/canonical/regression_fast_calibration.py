#!/usr/bin/env python3
"""Fast-calibration regression helpers for improved PFC LPBM.

The equations are source-specific predictors. Use them for reproduction or
initial guesses, then validate with PFC simulations.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from typing import Dict


@dataclass
class MicroParams:
    Ebar_star: float = 85.0
    E_ratio: float = 0.3
    kbar_star: float = 3.0
    sigma_c_bar: float = 135.0
    coh_ratio: float = 2.0
    mu: float = 0.7
    phi_bar: float = 30.0
    beta_bar_moment: float = 0.5
    Rf: float = 0.7
    beta_weibull: float = 3.0
    R_sigma: float = 0.1
    R_E: float = 0.1
    R_k: float = 2.0


def predict_macro(p: MicroParams, nonlinear_phi: bool = True) -> Dict[str, float]:
    e = 0.031 * p.Ebar_star - 0.886 * p.kbar_star - 6.728 * p.Rf + 16.546
    nu = -0.0002 * p.Ebar_star + 0.029 * p.kbar_star + 0.158 * p.Rf - 0.0001
    ucs = (
        -0.087 * p.Ebar_star
        + 70.061 * p.E_ratio
        + 0.646 * p.sigma_c_bar
        + 15.55 * p.coh_ratio
        + 24.043 * p.mu
        - 0.446 * p.phi_bar
        - 84.036 * p.beta_bar_moment
        - 76.097 * p.Rf
        + 135.056 * p.R_sigma
        + 28.910
    )
    if nonlinear_phi:
        phi = (
            0.019 * p.Ebar_star
            + 1.454 * p.coh_ratio
            + 0.974 * math.log(-0.840 + 1.692 * p.mu)
            - 14.064 * p.beta_bar_moment
            + 0.970 * math.log(1.942 - 2.767 * p.Rf)
            + 64.236
        )
    else:
        phi = (
            0.019 * p.Ebar_star
            + 1.454 * p.coh_ratio
            + 7.531 * p.mu
            - 14.064 * p.beta_bar_moment
            - 11.511 * p.Rf
            + 60.247
        )
    c = (
        -0.016 * p.Ebar_star
        + 0.081 * p.sigma_c_bar
        + 1.573 * p.coh_ratio
        - 0.065 * p.phi_bar
        - 5.364 * p.beta_bar_moment
        - 7.011 * p.Rf
        + 14.867 * p.R_sigma
        + 7.653
    )
    cd_ratio = (
        -0.419 * p.E_ratio
        - 0.003 * p.sigma_c_bar
        - 0.065 * p.coh_ratio
        + 0.003 * p.phi_bar
        + 0.260 * p.beta_bar_moment
        + 0.325 * p.Rf
        + 0.281 * p.R_E
        + 0.572
    )
    ucs_uts = 0.126 * p.phi_bar - 9.056 * p.beta_bar_moment + 9.484 * p.Rf - 16.026 * p.R_sigma + 3.352
    return {
        "E_GPa": e,
        "nu": nu,
        "UCS_MPa": ucs,
        "phi_deg": phi,
        "c_MPa": c,
        "sigma_cd_over_UCS": cd_ratio,
        "UCS_over_UTS": ucs_uts,
    }


def source_example() -> Dict[str, object]:
    params = MicroParams()
    return {"micro_params": asdict(params), "predicted_macro": predict_macro(params)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict macro values from source fast-calibration regressions.")
    parser.add_argument("--show-source-example", action="store_true")
    parser.add_argument("--params-json", help="JSON object with MicroParams fields to override defaults.")
    parser.add_argument("--target-E", type=float, default=None, help="Recorded for reporting; algebraic inversion is intentionally not automatic.")
    parser.add_argument("--target-nu", type=float, default=None)
    parser.add_argument("--target-UCS", type=float, default=None)
    parser.add_argument("--target-ratio", type=float, default=None)
    args = parser.parse_args()

    params = MicroParams()
    if args.params_json:
        values = json.loads(args.params_json)
        for key, value in values.items():
            if not hasattr(params, key):
                raise SystemExit(f"Unknown parameter: {key}")
            setattr(params, key, float(value))

    payload = {"micro_params": asdict(params), "predicted_macro": predict_macro(params)}
    targets = {"E_GPa": args.target_E, "nu": args.target_nu, "UCS_MPa": args.target_UCS, "UCS_over_UTS": args.target_ratio}
    payload["targets"] = {k: v for k, v in targets.items() if v is not None}
    if args.show_source_example:
        payload = source_example()
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
