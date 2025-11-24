# -*- coding: utf-8 -*-
"""
01_data_preprocessing.py

从 OZFlux 或类似通量数据文件中读取原始数据，并进行预处理：
- 解析时间列
- 选择子日时间步 (30/60 min)
- 计算可用能量 Qne = Rn - G
- 计算水汽压亏缺 D1 (kPa)
- 输出统一格式的 CSV 文件以供后续 GCP 模型使用

Read and preprocess raw flux / meteorological data from OZFlux-like files:
- Parse timestamp column
- Select sub-daily timestep (30/60 min)
- Compute available energy Qne = Rn - G
- Compute vapor pressure deficit D1 (kPa)
- Save standardized CSV for further GCP modeling
"""

from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

from utils import log


def saturation_vapor_pressure_kpa(ta_c: np.ndarray) -> np.ndarray:
    """
    计算饱和水汽压 (kPa)，Tetens 公式。
    Compute saturation vapor pressure (kPa) using Tetens formula.

    Args:
        ta_c (np.ndarray): 气温 (℃) / air temperature in degC.

    Returns:
        np.ndarray: 饱和水汽压 (kPa) / saturation vapor pressure in kPa.
    """
    return 0.6108 * np.exp(17.27 * ta_c / (ta_c + 237.3))


def compute_vpd_kpa(ta_c: np.ndarray, rh_pct: np.ndarray) -> np.ndarray:
    """
    由温度和相对湿度计算水汽压亏缺 (kPa)。
    Compute vapor pressure deficit (kPa) from air temperature and relative humidity.

    Args:
        ta_c (np.ndarray): 气温 (℃) / air temperature in degC.
        rh_pct (np.ndarray): 相对湿度 (%) / relative humidity in %.

    Returns:
        np.ndarray: VPD (kPa)
    """
    es = saturation_vapor_pressure_kpa(ta_c)
    ea = es * (rh_pct / 100.0)
    vpd = es - ea
    return vpd


def load_and_preprocess_site(
    raw_path: Path,
    site_name: str,
    time_col: str = "timestamp",
    var_map: Optional[Dict[str, str]] = None,
    freq: str = "30min",
) -> pd.DataFrame:
    """
    加载单个站点的原始数据并进行预处理。
    Load and preprocess raw data for a single site.

    Args:
        raw_path (Path): 原始数据文件路径 / path to raw data file (CSV).
        site_name (str): 站点名称 / site name (for logging).
        time_col (str): 时间列名称 / name of timestamp column.
        var_map (dict): 原始列名 -> 标准列名 的映射。
                        Mapping from raw column names to standardized ones.
                        需要包含至少: 'Rn', 'G', 'Ta', 'RH', 'WS', 'LE'.
        freq (str): 目标时间分辨率（如 '30min' 或 '60min'）。
                    Target timestep, e.g., '30min' or '60min'.

    Returns:
        pd.DataFrame: 预处理后包含 [Qne, Ta, u2, D1, E_obs] 的数据框。
                      Preprocessed DataFrame with at least [Qne, Ta, u2, D1, E_obs].
    """
    log(f"Loading raw data for site {site_name} from {raw_path} ...")



    df = pd.read_csv(raw_path)
    if time_col not in df.columns:
        raise ValueError(f"Timestamp column '{time_col}' not found in {raw_path}.")

    # 解析时间列并设为索引
    # Parse timestamp and set as index
    df[time_col] = pd.to_datetime(df[time_col])
    df = df.set_index(time_col).sort_index()

    # 列名映射到统一变量 (可以根据实际 OZFlux 字段修改)
    # Map column names to standardized ones (modify according to actual OZFlux fields)
    default_map = {
        "Rn": "Rn",      # Net radiation (W/m2)
        "G": "G",        # Soil heat flux (W/m2)
        "Ta": "Ta",      # Air temperature (degC)
        "RH": "RH",      # Relative humidity (%)
        "WS": "WS",      # Wind speed (m/s)
        "LE": "LE",      # Latent heat flux (W/m2), used as E_obs
    }
    if var_map is not None:
        default_map.update(var_map)

    df_std = pd.DataFrame(index=df.index)
    for std_name, raw_name in default_map.items():
        if raw_name not in df.columns:
            raise ValueError(
                f"Raw column '{raw_name}' for standardized '{std_name}' "
                f"not found in file {raw_path}.",
            )
        df_std[std_name] = df[raw_name]

    # 统一时间步（如从 30 分钟到 60 分钟）——这里采用平均
    # Resample to target timestep (e.g., from 30min to 60min) by mean
    df_res = df_std.resample(freq).mean()

    # 计算可用能量 Qne = Rn - G
    # Compute available energy Qne = Rn - G
    df_res["Qne"] = df_res["Rn"] - df_res["G"]

    # 计算 VPD / D1 (kPa)
    # Compute VPD / D1 (kPa)
    df_res["D1"] = compute_vpd_kpa(df_res["Ta"].values, df_res["RH"].values)

    # 标准化列名给后续模型使用
    # Standardized column names for the model
    df_res = df_res.rename(
        columns={
            "Ta": "Ta_C",
            "WS": "u2",
            "LE": "E_obs",
        },
    )

    # 删除存在 NaN 的时间步
    # Drop rows with missing values in key variables
    df_res = df_res[["Qne", "Ta_C", "u2", "D1", "E_obs"]].dropna()

    log(
        f"Site {site_name}: preprocessed {len(df_res)} records "
        f"at timestep {freq}.",
    )
    return df_res


if __name__ == "__main__":
    # 定义根目录
    # Define project root
    ROOT = Path(__file__).resolve().parents[1]
    raw_dir = ROOT / "data" / "raw"
    processed_dir = ROOT / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Tumbarumba 示例
    tum_raw = raw_dir / "tumbarumba_raw.csv"
    daly_raw = raw_dir / "daly_river_pasture_raw.csv"

    # 这里假设两个站点的时间列名和基本变量名一致，
    # 若不一致，可分别传入不同的 var_map。
    # Here we assume both sites share similar column names; otherwise pass different var_map.

    tum_df = load_and_preprocess_site(
        tum_raw,
        site_name="Tumbarumba",
        time_col="timestamp",
        var_map=None,
        freq="60min",
    )
    tum_df.to_csv(processed_dir / "tumbarumba_subdaily.csv", index=True)

    daly_df = load_and_preprocess_site(
        daly_raw,
        site_name="DalyRiverPasture",
        time_col="timestamp",
        var_map=None,
        freq="30min",
    )
    daly_df.to_csv(processed_dir / "daly_river_pasture_subdaily.csv", index=True)

    log("Data preprocessing completed for both sites.")
