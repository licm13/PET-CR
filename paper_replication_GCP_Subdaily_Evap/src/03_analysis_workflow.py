# -*- coding: utf-8 -*-
"""
03_analysis_workflow.py

集成数据加载、βc 标定与结果汇总的主工作流脚本。

Main analysis workflow:
- Load processed data for each site
- Calibrate beta_c with and without stability corrections
- Save metrics and intermediate results
"""

from pathlib import Path
import json

import pandas as pd

from utils import log, compute_metrics
from model_definition import GCPWithStability


def load_processed_site(path: Path) -> pd.DataFrame:
    """
    加载预处理好的站点数据。
    Load processed site data.
    """
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    return df


def run_site_analysis(
    site_name: str,
    df: pd.DataFrame,
    config: dict,
    results_dir: Path,
):
    """
    对单个站点运行 GCP 标定与蒸发估算。
    Run GCP calibration and evaporation estimation for a single site.

    Args:
        site_name (str): 站点名称 / site name.
        df (pd.DataFrame): 预处理数据 / preprocessed data.
        config (dict): 包含 z, d0, z0m, z0v 等参数的字典。
        results_dir (Path): 结果输出目录 / output directory.
    """
    log(f"Running analysis for site {site_name} ...")

    model = GCPWithStability(
        z=config["z"],
        d0=config["d0"],
        z0m=config["z0m"],
        z0v=config["z0v"],
        p_kpa=config.get("p_kpa", 101.3),
    )

    Qne = df["Qne"].values
    Ta_C = df["Ta_C"].values
    D1 = df["D1"].values
    u2 = df["u2"].values
    E_obs = df["E_obs"].values

    # 1) 带稳定度修正的 βc 标定
    calib_stab = model.calibrate_beta_c(
        Qne=Qne,
        Ta_C=Ta_C,
        D1_kpa=D1,
        u2=u2,
        E_obs=E_obs,
        beta_bounds=(0.7, 1.5),
        with_stability=True,
    )

    res_stab = model.estimate_time_series(
        Qne=Qne,
        Ta_C=Ta_C,
        D1_kpa=D1,
        u2=u2,
        beta_c=calib_stab["beta_c"],
        with_stability=True,
        max_iter=20,
    )

    # 2) 不考虑稳定度修正（中性）
    calib_neutral = model.calibrate_beta_c(
        Qne=Qne,
        Ta_C=Ta_C,
        D1_kpa=D1,
        u2=u2,
        E_obs=E_obs,
        beta_bounds=(0.7, 1.5),
        with_stability=False,
    )

    res_neutral = model.estimate_time_series(
        Qne=Qne,
        Ta_C=Ta_C,
        D1_kpa=D1,
        u2=u2,
        beta_c=calib_neutral["beta_c"],
        with_stability=False,
        max_iter=20,
    )

    # 保存时间序列结果
    # Save time series results
    out_df = pd.DataFrame(
        index=df.index,
        data={
            "E_obs": E_obs,
            "E_est_stab": res_stab["E"],
            "Epa_stab": res_stab["Epa"],
            "Ee_stab": res_stab["Ee"],
            "E_est_neutral": res_neutral["E"],
            "Epa_neutral": res_neutral["Epa"],
            "Ee_neutral": res_neutral["Ee"],
        },
    )
    out_csv = results_dir / f"{site_name}_timeseries.csv"
    out_df.to_csv(out_csv)

    # 汇总指标
    metrics_neutral = compute_metrics(res_neutral["E"], E_obs)

    summary = {
        "site": site_name,
        "config": config,
        "with_stability": calib_stab,
        "neutral": calib_neutral,
        "neutral_metrics": metrics_neutral,
    }
    out_json = results_dir / f"{site_name}_summary.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    log(f"Analysis for site {site_name} completed.")
    log(f"  Time series saved to: {out_csv}")
    log(f"  Summary saved to: {out_json}")


if __name__ == "__main__":
    ROOT = Path(__file__).resolve().parents[1]
    processed_dir = ROOT / "data" / "processed"
    results_dir = ROOT / "results" / "tables"
    results_dir.mkdir(parents=True, exist_ok=True)

    # 站点配置：根据论文表 1 设置 z / z0m, 粗糙度等（可调整）
    # Site configuration: approximate z, d0, z0m, z0v (can be adjusted)

    site_configs = {
        "Tumbarumba": {
            "z": 70.0,
            "d0": 26.7,
            "z0m": 0.7,
            "z0v": 0.07,
        },
        "DalyRiverPasture": {
            "z": 15.0,
            "d0": 0.2,
            "z0m": 15.0 / 270.0,
            "z0v": (15.0 / 270.0) / 10.0,
        },
    }

    tum_df = load_processed_site(processed_dir / "tumbarumba_subdaily.csv")
    run_site_analysis(
        site_name="Tumbarumba",
        df=tum_df,
        config=site_configs["Tumbarumba"],
        results_dir=results_dir,
    )

    daly_df = load_processed_site(processed_dir / "daly_river_pasture_subdaily.csv")
    run_site_analysis(
        site_name="DalyRiverPasture",
        df=daly_df,
        config=site_configs["DalyRiverPasture"],
        results_dir=results_dir,
    )

    log("All site analyses completed.")
