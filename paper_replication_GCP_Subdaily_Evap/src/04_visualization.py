# -*- coding: utf-8 -*-
"""
04_visualization.py

生成与论文类似的图形：
- 平均日变化曲线
- E_est vs E_obs 散点/hexbin
- 无量纲互补曲线

Generate plots similar to those in the paper:
- Mean diurnal cycle
- E_est vs E_obs scatter / hexbin
- Dimensionless complementary curve
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from utils import log


def plot_diurnal_cycle(
    df: pd.DataFrame,
    site_name: str,
    figures_dir: Path,
):
    """
    绘制平均日变化曲线：
    - 观测蒸发 E_obs
    - 带稳定度修正的估算 E_est_stab
    - 中性假设下的估算 E_est_neutral

    Plot mean diurnal cycle of:
    - Observed evaporation (E_obs)
    - Estimated with stability correction (E_est_stab)
    - Estimated assuming neutral conditions (E_est_neutral)
    """
    df = df.copy()
    df["hour"] = df.index.hour

    diurnal = df.groupby("hour")[["E_obs", "E_est_stab", "E_est_neutral"]].mean()

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(diurnal.index, diurnal["E_obs"], label="E_obs")
    ax.plot(diurnal.index, diurnal["E_est_stab"], label="E_est_stab (stability)")
    ax.plot(
        diurnal.index,
        diurnal["E_est_neutral"],
        label="E_est_neutral (neutral)",
    )
    ax.set_xlabel("Hour of day / 小时")
    ax.set_ylabel("Latent heat flux (W m$^{-2}$) / 潜热通量")
    ax.set_title(f"Mean diurnal cycle at {site_name}")
    ax.legend()
    ax.grid(True, alpha=0.3)

    out_path = figures_dir / f"{site_name}_diurnal_cycle.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    log(f"Diurnal cycle figure saved to {out_path}")


def plot_scatter_est_vs_obs(
    df: pd.DataFrame,
    site_name: str,
    figures_dir: Path,
):
    """
    绘制估算 E 与观测 E 的散点/hexbin 图。
    Plot hexbin scatter of estimated vs observed evaporation.
    """
    E_obs = df["E_obs"].values
    E_est_stab = df["E_est_stab"].values

    fig, ax = plt.subplots(figsize=(5, 5))
    hb = ax.hexbin(E_obs, E_est_stab, gridsize=40, mincnt=1)
    ax.plot(
        [E_obs.min(), E_obs.max()],
        [E_obs.min(), E_obs.max()],
        "k--",
        linewidth=1.0,
        label="1:1 line",
    )
    ax.set_xlabel("Observed E (W m$^{-2}$)")
    ax.set_ylabel("Estimated E (W m$^{-2}$)")
    ax.set_title(f"E_est vs E_obs at {site_name}")
    cb = fig.colorbar(hb, ax=ax)
    cb.set_label("Counts")
    ax.legend()
    ax.grid(True, alpha=0.3)

    out_path = figures_dir / f"{site_name}_scatter_Eest_vs_Eobs.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    log(f"Scatter figure saved to {out_path}")


def plot_dimensionless_cr(
    df: pd.DataFrame,
    site_name: str,
    figures_dir: Path,
):
    """
    绘制无量纲互补曲线：
    y = E / Epa, x = βc Ee / Epa 与理论曲线 y = 2x^2 - x^3 比较。

    Plot dimensionless complementary relationship:
    y = E / Epa vs x = βc Ee / Epa, compared with y = 2x^2 - x^3.
    """
    ROOT = Path(__file__).resolve().parents[1]
    summary_path = ROOT / "results" / "tables" / f"{site_name}_summary.json"
    if not summary_path.exists():
        log(f"Summary file {summary_path} not found. Skip dimensionless plot.")
        return

    import json

    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)
    beta_c = summary["with_stability"]["beta_c"]

    Ee = df["Ee_stab"].values
    Epa = df["Epa_stab"].values
    E = df["E_est_stab"].values

    Epa_safe = np.where(Epa <= 1e-6, 1e-6, Epa)
    x = beta_c * Ee / Epa_safe
    x = np.clip(x, 0.0, 1.0)
    y = E / Epa_safe

    fig, ax = plt.subplots(figsize=(5, 4))
    hb = ax.hexbin(x, y, gridsize=40, mincnt=1)
    cb = fig.colorbar(hb, ax=ax)
    cb.set_label("Counts")

    x_theo = np.linspace(0.0, 1.0, 200)
    y_theo = 2.0 * x_theo ** 2 - x_theo ** 3
    ax.plot(x_theo, y_theo, "r-", linewidth=2.0, label="GCP: y = 2x^2 - x^3")

    ax.set_xlabel(r"$\beta_c E_e / E_{pa}$")
    ax.set_ylabel(r"$E / E_{pa}$")
    ax.set_title(f"Dimensionless CR at {site_name}")
    ax.legend()
    ax.grid(True, alpha=0.3)

    out_path = figures_dir / f"{site_name}_dimensionless_CR.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    log(f"Dimensionless CR figure saved to {out_path}")


if __name__ == "__main__":
    ROOT = Path(__file__).resolve().parents[1]
    tables_dir = ROOT / "results" / "tables"
    figures_dir = ROOT / "results" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    for site_name, csv_name in [
        ("Tumbarumba", "Tumbarumba_timeseries.csv"),
        ("DalyRiverPasture", "DalyRiverPasture_timeseries.csv"),
    ]:
        csv_path = tables_dir / csv_name
        if not csv_path.exists():
            log(f"Timeseries file {csv_path} not found, skip {site_name}.")
            continue
        df = pd.read_csv(csv_path, index_col=0, parse_dates=True)

        plot_diurnal_cycle(df, site_name, figures_dir)
        plot_scatter_est_vs_obs(df, site_name, figures_dir)
        plot_dimensionless_cr(df, site_name, figures_dir)

    log("All figures generated.")
