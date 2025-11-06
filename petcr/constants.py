"""
物理常数模块 / Physical Constants Module
========================================

本模块集中定义 PET-CR 库中使用的所有物理常数和转换因子，确保一致性和可维护性。
This module centralizes all physical constants and conversion factors used in
the PET-CR library to ensure consistency and maintainability.

所有常数使用 SI 单位，并提供明确的来源引用。
All constants use SI units with clear source references.

参考文献 / References
---------------------
.. [1] Allen, R.G., Pereira, L.S., Raes, D., & Smith, M. (1998).
       Crop evapotranspiration-Guidelines for computing crop water requirements.
       FAO Irrigation and drainage paper 56, FAO, Rome, 300(9), D05109.
.. [2] WMO (2018). Guide to Instruments and Methods of Observation.
       WMO-No. 8, Volume I.
.. [3] CODATA (2018). Committee on Data for Science and Technology.
"""

# ============================================================================
# 时间常数 / Time Constants
# ============================================================================
SECONDS_PER_DAY = 86400  # s
"""秒每天 / Seconds per day"""

DAYS_PER_YEAR = 365.25  # days (average including leap years)
"""平均年长度（包含闰年）/ Average days per year including leap years"""

DAYS_PER_MONTH_AVG = 30.4375  # days (365.25 / 12)
"""平均月长度 / Average days per month (365.25 / 12)

Note 注意
---------
This is only an average. Use actual month lengths for precise calculations.
这只是平均值。对于精确计算，请使用实际月长度。
"""

# ============================================================================
# 热力学常数 / Thermodynamic Constants
# ============================================================================
CP_AIR = 1013.0  # J/(kg·K)
"""空气定压比热 / Specific heat of air at constant pressure [J/(kg·K)]

Source / 来源: FAO-56 (Allen et al., 1998)
Valid range / 有效范围: -20°C to 50°C
"""

LV_WATER = 2.45e6  # J/kg
"""水的汽化潜热（在约20°C）/ Latent heat of vaporization of water (at ~20°C) [J/kg]

Source / 来源: FAO-56 (Allen et al., 1998)
Note 注意: For temperature-dependent calculations, use
calculate_latent_heat_vaporization() function.
对于温度依赖计算，使用 calculate_latent_heat_vaporization() 函数。
"""

# ============================================================================
# 气体常数 / Gas Constants
# ============================================================================
R_SPECIFIC_DRY_AIR = 287.05  # J/(kg·K)
"""干空气比气体常数 / Specific gas constant for dry air [J/(kg·K)]

Source / 来源: CODATA 2018
Formula / 公式: R_specific = R_universal / M_air
where R_universal = 8.314462618 J/(mol·K) and M_air = 0.0289647 kg/mol
"""

EPSILON_MOLWEIGHT = 0.62198  # dimensionless
"""水汽与干空气的分子量比 / Ratio of molecular weight of water vapor to dry air

Source / 来源: M_water / M_air = 18.01528 / 28.96546 = 0.621979...
Commonly rounded to 0.622 in meteorology.
气象学中通常舍入为 0.622。
"""

# ============================================================================
# 密度常数 / Density Constants
# ============================================================================
RHO_AIR_SL = 1.225  # kg/m³
"""海平面标准条件下的空气密度 / Air density at sea level, standard conditions [kg/m³]

Standard conditions / 标准条件: 15°C, 101325 Pa
Note 注意: For elevation-dependent calculations, compute density from
ideal gas law: ρ = P / (R_specific × T)
对于海拔依赖计算，使用理想气体定律计算密度：ρ = P / (R_specific × T)
"""

RHO_WATER = 1000.0  # kg/m³
"""水的密度 / Density of water [kg/m³]

Standard conditions / 标准条件: 4°C, 101325 Pa
"""

# ============================================================================
# Tetens 方程常数 / Tetens Equation Constants
# ============================================================================
TETENS_A = 17.27  # dimensionless
"""Tetens方程系数A / Tetens equation coefficient A

Source / 来源: FAO-56, Equation 11
"""

TETENS_B = 237.3  # °C
"""Tetens方程系数B / Tetens equation coefficient B [°C]

Source / 来源: FAO-56, Equation 11
"""

TETENS_E0_PA = 611.0  # Pa
"""Tetens方程基准饱和水汽压（0°C）/ Reference saturation vapor pressure at 0°C [Pa]

Source / 来源: FAO-56
"""

TETENS_E0_KPA = 0.611  # kPa
"""Tetens方程基准饱和水汽压（0°C）/ Reference saturation vapor pressure at 0°C [kPa]

Source / 来源: FAO-56
"""

# ============================================================================
# 经验系数 / Empirical Coefficients
# ============================================================================
PRIESTLEY_TAYLOR_ALPHA = 1.26  # dimensionless
"""Priestley-Taylor系数 / Priestley-Taylor coefficient

Source / 来源: Priestley & Taylor (1972)
Applicable to / 适用于: Well-watered surfaces under minimal advection
充分灌溉且平流效应最小的地表
"""

PENMAN_WIND_COEFF = 208.0  # s/m
"""Penman风速函数系数（简化形式）/ Penman wind function coefficient (simplified) [s/m]

Formula / 公式: r_a = 208 / u_2
where u_2 is wind speed at 2m height / 其中 u_2 是2米高度风速
Source / 来源: FAO-56, simplified form for reference grass
"""

# ============================================================================
# 单位转换因子 / Unit Conversion Factors
# ============================================================================
W_TO_MJ_PER_DAY = 0.0864  # (W/m²) to (MJ/m²/day)
"""能量通量单位转换：W/m² 转 MJ/m²/day / Energy flux conversion: W/m² to MJ/m²/day

Calculation / 计算: 1 W/m² × 86400 s/day = 86400 J/m²/day = 0.0864 MJ/m²/day
"""

PA_TO_KPA = 0.001  # Pa to kPa
"""压强单位转换：Pa 转 kPa / Pressure conversion: Pa to kPa"""

KPA_TO_PA = 1000.0  # kPa to Pa
"""压强单位转换：kPa 转 Pa / Pressure conversion: kPa to Pa"""

KELVIN_TO_CELSIUS_OFFSET = 273.15  # K to °C offset
"""温度单位偏移：开尔文转摄氏度 / Temperature offset: Kelvin to Celsius

Formula / 公式: T(°C) = T(K) - 273.15
"""

MM_PER_DAY_TO_W_PER_M2 = 28.35  # (mm/day) to (W/m²) at 20°C
"""蒸散发单位转换：mm/day 转 W/m² / ET conversion: mm/day to W/m² (at 20°C)

Calculation / 计算: 1 mm/day = 1000 kg/m³ × 0.001 m × 2.45e6 J/kg / 86400 s
≈ 28.35 W/m²
Note / 注意: Temperature-dependent due to latent heat variation
由于潜热变化，此值依赖于温度
"""

# ============================================================================
# 数值计算常数 / Numerical Constants
# ============================================================================
EPSILON_SAFE_DIV = 1e-12
"""通用安全除法小量 / General small value for safe division

Used to avoid division by zero in numerical calculations.
用于避免数值计算中的除零错误。
"""

EPSILON_PRECIP = 1e-10  # mm
"""降水阈值 / Precipitation threshold [mm]

Values below this are considered effectively zero (0.01 mm/year).
低于此值被视为有效零值（0.01 mm/年）。
"""

EPSILON_EVAP = 1e-6  # mm/day
"""蒸发阈值 / Evaporation threshold [mm/day]

Values below this are considered effectively zero (0.001 mm/day).
低于此值被视为有效零值（0.001 mm/天）。
"""

# ============================================================================
# 物理约束 / Physical Constraints
# ============================================================================
TEMPERATURE_MIN_CELSIUS = -100.0  # °C
"""合理温度下限 / Minimum reasonable temperature [°C]

For detecting unit errors (user might pass Celsius as Kelvin).
用于检测单位错误（用户可能将摄氏度当作开尔文传入）。
"""

TEMPERATURE_MAX_CELSIUS = 70.0  # °C
"""合理温度上限 / Maximum reasonable temperature [°C]

For detecting unit errors or extreme values.
用于检测单位错误或极端值。
"""

TEMPERATURE_MIN_KELVIN = 173.15  # K (= -100°C)
"""合理温度下限（开尔文）/ Minimum reasonable temperature [K]"""

TEMPERATURE_MAX_KELVIN = 343.15  # K (= 70°C)
"""合理温度上限（开尔文）/ Maximum reasonable temperature [K]"""

RELATIVE_HUMIDITY_MIN = 0.0  # %
"""相对湿度下限 / Minimum relative humidity [%]"""

RELATIVE_HUMIDITY_MAX = 100.0  # %
"""相对湿度上限 / Maximum relative humidity [%]"""

WIND_SPEED_MIN = 0.0  # m/s
"""风速下限 / Minimum wind speed [m/s]"""

WIND_SPEED_MAX = 100.0  # m/s
"""风速上限（用于检测异常值）/ Maximum wind speed for outlier detection [m/s]"""

PRESSURE_MIN = 50000.0  # Pa (~5500m elevation)
"""合理气压下限 / Minimum reasonable pressure [Pa]

Corresponds to ~5500m elevation / 对应约5500米海拔
"""

PRESSURE_MAX = 110000.0  # Pa (extreme low elevation)
"""合理气压上限 / Maximum reasonable pressure [Pa]

Corresponds to extreme low elevations / 对应极低海拔
"""

# ============================================================================
# 模块导出 / Module Exports
# ============================================================================
__all__ = [
    # Time constants / 时间常数
    'SECONDS_PER_DAY',
    'DAYS_PER_YEAR',
    'DAYS_PER_MONTH_AVG',
    
    # Thermodynamic constants / 热力学常数
    'CP_AIR',
    'LV_WATER',
    
    # Gas constants / 气体常数
    'R_SPECIFIC_DRY_AIR',
    'EPSILON_MOLWEIGHT',
    
    # Density constants / 密度常数
    'RHO_AIR_SL',
    'RHO_WATER',
    
    # Tetens equation constants / Tetens方程常数
    'TETENS_A',
    'TETENS_B',
    'TETENS_E0_PA',
    'TETENS_E0_KPA',
    
    # Empirical coefficients / 经验系数
    'PRIESTLEY_TAYLOR_ALPHA',
    'PENMAN_WIND_COEFF',
    
    # Unit conversion factors / 单位转换因子
    'W_TO_MJ_PER_DAY',
    'PA_TO_KPA',
    'KPA_TO_PA',
    'KELVIN_TO_CELSIUS_OFFSET',
    'MM_PER_DAY_TO_W_PER_M2',
    
    # Numerical constants / 数值计算常数
    'EPSILON_SAFE_DIV',
    'EPSILON_PRECIP',
    'EPSILON_EVAP',
    
    # Physical constraints / 物理约束
    'TEMPERATURE_MIN_CELSIUS',
    'TEMPERATURE_MAX_CELSIUS',
    'TEMPERATURE_MIN_KELVIN',
    'TEMPERATURE_MAX_KELVIN',
    'RELATIVE_HUMIDITY_MIN',
    'RELATIVE_HUMIDITY_MAX',
    'WIND_SPEED_MIN',
    'WIND_SPEED_MAX',
    'PRESSURE_MIN',
    'PRESSURE_MAX',
]
