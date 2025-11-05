# -*- coding: utf-8 -*-
"""
Synthetic heterogeneous sub-basin demo (EN/中文)
================================================
- Generate 8 sub-basins with different (elevation/aridity/seasonality/albedo)
- Build monthly time series 1982-2022 for P, Epa, Erad (toy)
- Compare three parameterization strategies:
    1) Uniform w
    2) w(SI)
    3) w(SI, ALB)

注意：此示例为“结构复刻”，用于检查公式与流程；
真实复现需替换为论文所述数据（TPMFD/ERA5等）。
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from bgcr_budyko.models.bgcr import bgcr_monthly
from bgcr_budyko.params.w_schemes import w_from_SI, w_from_SI_albedo
from bgcr_budyko.io.io_helpers import seasonal_index

# Matplotlib font for Chinese (best effort; may vary by environment)
plt.rcParams['font.sans-serif'] = ['Arial']  # 若无中文字体，可安装 SimHei 或 Noto Sans CJK
plt.rcParams['axes.unicode_minus'] = False

np.random.seed(42)

years = np.arange(1982, 2023)
nY = len(years)
months = np.tile(np.arange(1,13), nY)
time_index = pd.date_range('1982-01-01', periods=nY*12, freq='MS')

nbas = 8
labels = [f"Basin{i+1}" for i in range(nbas)]

# Create synthetic heterogeneity for each basin (scalar per basin)
elev = np.linspace(800, 5200, nbas)             # elevation proxy
arid = np.linspace(0.5, 1.6, nbas)              # AI proxy
albedo = np.clip(0.15 + (elev-800)/5000*0.35, 0.12, 0.6)  # higher elev -> higher albedo
season_amp = np.linspace(0.2, 1.2, nbas)        # stronger seasonality eastwards
wind = np.linspace(1.0, 4.0, nbas)

def monthly_shape(x):
    return np.repeat(x[None, None, ...], nY, axis=0).repeat(12, axis=1)

# Build monthly series (years, 12, basins)
baseP = 50.0 + 100.0*np.sin(2*np.pi*(months/12.0 - 0.2))  # seasonal baseline
P = np.zeros((nY,12,nbas))
Epa = np.zeros_like(P)
Erad = np.zeros_like(P)

for b in range(nbas):
    # precipitation: wetter in low elev / humid basins, add noise
    scale = 1.4 - 0.6*(arid[b]-0.5)  # arid up -> less P
    P[:,:,b] = (baseP*scale).reshape(nY,12) * (1 + season_amp[b]*0.3*np.sin(2*np.pi*(np.arange(12)/12.0)))
    P[:,:,b] += np.random.randn(nY,12)*5.0
    P[:,:,b] = np.clip(P[:,:,b], 0.1, None)
    # Erad: larger for high elevation (clear sky), plus summer peak
    Erad[:,:,b] = (3.0 + 0.002*(elev[b])) * (1 + 0.5*np.sin(2*np.pi*((np.arange(12)+1)/12.0 - 0.25)))
    # Epa: add small aerodynamic term via wind & VPD proxy
    vpd = 0.8 + 0.3*np.sin(2*np.pi*((np.arange(12)+1)/12.0 - 0.2))
    Epa[:,:,b] = Erad[:,:,b] + 0.05*wind[b]*vpd

# Compute SI per basin (years,12,basins) -> (basins,)
SI = np.zeros(nbas)
for b in range(nbas):
    SI[b] = seasonal_index(P[:,:,b][None, ...])  # reuse function; expects (years,12,...)

# Strategy 1: uniform w calibrated-ish (mid value)
w_uni = 1.6
# Strategy 2: SI only
w_si = w_from_SI(SI)
# Strategy 3: SI + Albedo
w_dual = w_from_SI_albedo(SI, albedo)

# Run BGCR for each strategy
def run_strategy(w_param):
    E = np.zeros_like(P)
    for b in range(nbas):
        if np.isscalar(w_param):
            w_use = w_param
        elif np.ndim(w_param)==1:
            w_use = w_param[b]
        else:
            w_use = w_param[..., b]
        e, _ = bgcr_monthly(P[:,:,b], Epa[:,:,b], Erad[:,:,b], w=w_use)
        E[:,:,b] = e
    return E

E_uni = run_strategy(w_uni)
E_si  = run_strategy(w_si)
E_dual= run_strategy(w_dual)

# Aggregate annual for plotting
def annual_sum(arr):
    return arr.reshape(nY,12,-1).sum(axis=1)

annE_uni = annual_sum(E_uni)
annE_si  = annual_sum(E_si)
annE_dual= annual_sum(E_dual)
annP     = annual_sum(P)

# Plot comparison for one humid basin (low elev) and one dry, high-elev basin
fig, axes = plt.subplots(2,1, figsize=(9,6), dpi=120, sharex=True)
pick_lo = 0
pick_hi = -1
axes[0].plot(years, annE_uni[:,pick_lo], label='Uniform w')
axes[0].plot(years, annE_si[:,pick_lo],  label='w(SI)')
axes[0].plot(years, annE_dual[:,pick_lo],label='w(SI,ALB)')
axes[0].set_ylabel('Annual E (synthetic) / 年蒸发(合成)')
axes[0].set_title(f'{labels[pick_lo]} (低海拔/湿润示例)')
axes[0].legend()

axes[1].plot(years, annE_uni[:,pick_hi], label='Uniform w')
axes[1].plot(years, annE_si[:,pick_hi],  label='w(SI)')
axes[1].plot(years, annE_dual[:,pick_hi],label='w(SI,ALB)')
axes[1].set_ylabel('Annual E (synthetic) / 年蒸发(合成)')
axes[1].set_title(f'{labels[pick_hi]} (高海拔/干旱示例)')
axes[1].set_xlabel('Year / 年份')
axes[1].legend()

plt.tight_layout()
plt.savefig('../figures/demo_annual_E_compare.png', bbox_inches='tight')
print('Saved figures/demo_annual_E_compare.png')

# Spatial-style scatter: show SI vs w for both schemes
plt.figure(figsize=(6,4), dpi=120)
plt.scatter(SI, np.full_like(SI, w_uni), label='Uniform w')
plt.scatter(SI, w_si, label='w(SI)')
plt.scatter(SI, w_dual, label='w(SI,ALB)')
plt.xlabel('SI (seasonality index)')
plt.ylabel('w')
plt.title('Budyko w parameterization / Budyko参数区域化')
plt.legend()
plt.tight_layout()
plt.savefig('../figures/w_parameterization.png', bbox_inches='tight')
print('Saved figures/w_parameterization.png')
