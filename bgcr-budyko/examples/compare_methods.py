"""
Example: compare BGCR PET implementations (single point or grid).
Saves results to examples/output/pet_compare.csv and creates a quick plot.

Usage:
    python bgcr-budyko/examples/compare_methods.py --input bgcr-budyko/examples/data/sample_meteo.csv
"""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Imports based on README references
from bgcr_budyko.models.bgcr import bgcr_monthly
from bgcr_budyko.params.w_schemes import w_from_SI, w_from_SI_albedo

OUT_DIR = Path("bgcr-budyko/examples/output")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def load_sample(path):
    """Load sample CSV expecting columns: time,P,Epa,Erad,SI,ALB (SI, ALB optional)."""
    df = pd.read_csv(path, parse_dates=["time"])
    df.set_index("time", inplace=True)
    required = {"P", "Epa", "Erad"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df

def compare_methods(df):
    """Run bgcr_monthly with scalar w and two w schemes (SI, SI+ALB)."""
    P = df["P"].values
    Epa = df["Epa"].values
    Erad = df["Erad"].values

    # 1) baseline: fixed w
    E_fixed, out_fixed = bgcr_monthly(P, Epa, Erad, w=1.6)

    # 2) single-variable w from SI (if SI present)
    if "SI" in df.columns:
        SI = df["SI"].values
        w_si = w_from_SI(SI)
        E_si, out_si = bgcr_monthly(P, Epa, Erad, w=w_si)
    else:
        w_si = None
        E_si = None

    # 3) SI + Albedo
    if {"SI", "ALB"} <= set(df.columns):
        SI = df["SI"].values
        ALB = df["ALB"].values
        w_si_alb = w_from_SI_albedo(SI, ALB)
        E_si_alb, out_si_alb = bgcr_monthly(P, Epa, Erad, w=w_si_alb)
    else:
        w_si_alb = None
        E_si_alb = None

    # Build DataFrame of results
    index = df.index
    results = pd.DataFrame(index=index)
    results["E_fixed"] = E_fixed
    if E_si is not None:
        results["E_si"] = E_si
    if E_si_alb is not None:
        results["E_si_alb"] = E_si_alb

    return results

def main(infile):
    df = load_sample(infile)
    res = compare_methods(df)
    out_csv = OUT_DIR / "pet_compare.csv"
    res.to_csv(out_csv)
    print(f"Wrote results to {out_csv}")

    # Quick plotting
    ax = res.plot(figsize=(10, 4), title="BGCR PET methods comparison")
    ax.set_ylabel("PET (same units as Epa)")
    fig = ax.get_figure()
    fig.savefig(OUT_DIR / "pet_compare.png", dpi=150)
    print(f"Wrote plot to {OUT_DIR/'pet_compare.png'}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", "-i", default="bgcr-budyko/examples/data/sample_meteo.csv")
    args = p.parse_args()
    main(args.input)
