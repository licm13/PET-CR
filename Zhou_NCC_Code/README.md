# Land-Atmosphere Feedback in Evapotranspiration Projections

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Code repository for the paper: **"Neglecting land–atmosphere feedbacks overestimates climate-driven increases in evapotranspiration"** published in *Nature Climate Change*.

[中文文档](README_CN.md)

## Overview

This repository provides Python implementations of the theoretical framework developed to disentangle land-atmosphere interactions in evapotranspiration (ET) projections. The code distinguishes between two key potential evapotranspiration (PET) estimators:

- **PETe** (Energy-based PET): Maximum ET constrained by net radiation
- **PETa** (Aerodynamics-based PET): Maximum ET determined by aerodynamic conditions

## Key Findings

- Previous estimates of climate-driven ET increases have been overestimated by **25-39%**
- Land surface changes' negative contribution has been exaggerated by **77-121%**
- PETe remains largely insensitive to land-atmosphere feedbacks, making it suitable for isolating climate change impacts

## Installation

### Requirements

```bash
pip install -r requirements.txt
```

Required packages:
- numpy >= 1.20.0
- pandas >= 1.3.0
- scipy >= 1.7.0
- matplotlib >= 3.4.0
- netCDF4 >= 1.5.7 (optional, for reading CMIP6 data)

### Quick Start

```python
from src.pet_estimation import calculate_pet_land
from src.data_generator import generate_sample_data

# Generate sample data
data = generate_sample_data(n_samples=100)

# Calculate PETe and PETa
results = calculate_pet_land(
    latent_heat=data['hfls'],
    sensible_heat=data['hfss'],
    specific_humidity=data['huss'],
    air_pressure=data['ps'],
    air_temperature=data['tas'],
    skin_temperature=data['ts']
)

print(f"PETe: {results['pete']} mm/day")
print(f"PETa: {results['peta']} mm/day")
```

## Project Structure

```
et_landatmosphere_feedback/
├── README.md                   # English documentation
├── README_CN.md               # Chinese documentation
├── requirements.txt           # Python dependencies
├── LICENSE                    # MIT License
├── src/
│   ├── __init__.py
│   ├── pet_estimation.py     # PET calculation functions
│   ├── wet_dry_conditions.py # PET under wet/driest conditions
│   ├── et_attribution.py     # ET projection and attribution
│   ├── budyko_framework.py   # Budyko framework implementation
│   └── data_generator.py     # Sample data generation
├── data/
│   ├── input/                # Input data directory (empty)
│   └── output/               # Output results directory
├── examples/
│   ├── example_basic.py      # Basic usage example
│   ├── example_attribution.py # Attribution analysis example
│   └── example_visualization.py # Visualization example
├── tests/
│   ├── test_pet_estimation.py
│   ├── test_attribution.py
│   └── test_budyko.py
└── docs/
    ├── methodology.md        # Detailed methodology
    └── data_format.md        # Input data format specification
```

## Usage

### 1. Basic PET Calculation (Land Surface)

```python
from src.pet_estimation import calculate_pet_land

# Your input data (can be from Fluxnet2015 or CMIP6 models)
results = calculate_pet_land(
    latent_heat=100.0,      # W/m²
    sensible_heat=50.0,     # W/m²
    specific_humidity=0.01, # kg/kg
    air_pressure=101325.0,  # Pa
    air_temperature=298.15, # K
    skin_temperature=300.15 # K
)
```

### 2. PET Under Wet and Driest Conditions (Ocean Surface)

```python
from src.wet_dry_conditions import calculate_pet_ocean

results = calculate_pet_ocean(
    latent_heat=150.0,
    sensible_heat=30.0,
    specific_humidity=0.015,
    air_pressure=101325.0,
    air_temperature=298.15,
    skin_temperature=299.15
)

print(f"PETe (wet): {results['pete_wet']} mm/day")
print(f"PETa (wet): {results['peta_wet']} mm/day")
print(f"PETe (driest): {results['pete_driest']} mm/day")
print(f"PETa (driest): {results['peta_driest']} mm/day")
```

### 3. ET Attribution Analysis

```python
from src.et_attribution import attribution_analysis

# Historical and future climate data
results = attribution_analysis(
    et_timeseries=et_data,
    pete_timeseries=pete_data,
    pr_timeseries=pr_data,
    window_size=30  # 30-year moving average
)

print(f"Climate change contribution: {results['et_climate']} mm/day")
print(f"Land surface change contribution: {results['et_landsurf']} mm/day")
```

## Data Format

### Input Data Requirements

The code expects meteorological variables in the following units:

| Variable | Symbol | Unit | Description |
|----------|--------|------|-------------|
| Latent Heat Flux | `hfls` | W/m² | Surface upward latent heat flux |
| Sensible Heat Flux | `hfss` | W/m² | Surface upward sensible heat flux |
| Specific Humidity | `huss` | kg/kg | Near-surface specific humidity |
| Air Pressure | `ps` | Pa | Surface air pressure |
| Air Temperature | `tas` | K | Near-surface air temperature |
| Skin Temperature | `ts` | K | Surface skin temperature |
| Precipitation | `pr` | mm/day | Precipitation (for attribution) |

### Data Sources

#### 1. Fluxnet2015 Dataset
- **Source**: https://fluxnet.org/data/fluxnet2015-dataset/
- **Coverage**: 146 sites, 990 site-years (1997-2014)
- **Variables**: Energy fluxes, meteorological conditions

#### 2. CMIP6 Model Simulations
- **Source**: https://esgf-node.llnl.gov/search/cmip6/
- **Experiments**: 
  - Historical (1980-2014)
  - SSP5-8.5 (2015-2100)
  - 1pctCO2 and 1pctCO2-rad (idealized experiments)
- **Models**: 32 CMIP6 models (see paper Supplementary Table 2)

### Loading Real Data

```python
# Example: Load Fluxnet data
from src.data_loader import load_fluxnet_data

data = load_fluxnet_data('data/input/fluxnet_site.csv')

# Example: Load CMIP6 data
from src.data_loader import load_cmip6_data

cmip6_data = load_cmip6_data(
    model='ACCESS-CM2',
    experiment='historical',
    variable='hfls',
    path='data/input/cmip6/'
)
```

## Methodology

### Theoretical Framework

The relationship between ET and the two PET estimators is given by:

```
ET = (1 + βw) × PETe - βw × PETa
```

Where:
- `βw` is the wet Bowen ratio (ratio of sensible to latent heat under saturated conditions)
- `PETe` represents atmospheric energy control on ET
- `PETa` represents aerodynamic conditions

### Key Equations

**1. Energy-based PET (PETe):**
```
PETe = Rn / (1 + βw)
```

**2. Aerodynamics-based PET (PETa):**
```
PETa = H / βw
```

**3. Wet Bowen Ratio (βw):**
```
βw = γ × (Ts - Ta) / (e*s - ea)
```

Where:
- `Rn` = Net radiation (W/m²)
- `H` = Sensible heat flux (W/m²)
- `γ` = Psychrometric constant (kPa/°C)
- `Ts` = Surface temperature (K)
- `Ta` = Air temperature (K)
- `e*s` = Saturation vapor pressure at surface temperature (kPa)
- `ea` = Actual vapor pressure (kPa)

### Budyko Framework

The Budyko framework relates ET ratio to dryness index:

```
ET/P = [(PETe/P)^(-n) + 1]^(-1/n)
```

Where:
- `P` = Precipitation (mm/day)
- `n` = Parameter accounting for land surface characteristics

## Examples

See the `examples/` directory for detailed usage examples:

1. **example_basic.py**: Basic PET calculation
2. **example_attribution.py**: ET attribution analysis
3. **example_visualization.py**: Visualization of results

Run examples:
```bash
python examples/example_basic.py
python examples/example_attribution.py
python examples/example_visualization.py
```

## Testing

Run the test suite:

```bash
pytest tests/
```

Run tests with coverage:

```bash
pytest --cov=src tests/
```

## Citation

If you use this code in your research, please cite:

```bibtex
@article{zhou2025neglecting,
  title={Neglecting land–atmosphere feedbacks overestimates climate-driven increases in evapotranspiration},
  author={Zhou, Sha and Yu, Bofu},
  journal={Nature Climate Change},
  year={2025},
  doi={10.1038/s41558-025-02428-5}
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

- **Corresponding Author**: Sha Zhou (shazhou21@bnu.edu.cn)
- **Institution**: Beijing Normal University

## Acknowledgments

- Fluxnet2015 dataset contributors
- CMIP6 modeling groups
- National Natural Science Foundation of China (grants 42471108 and 42521001)
- National Key Research and Development Program of China (grant 2022YFF0801303)

## References

1. Zhou, S., & Yu, B. (2024). Physical basis of the potential evapotranspiration and its estimation over land. *Journal of Hydrology*, 641, 131825.

2. Zhou, S., Yu, B., Huang, Y., & Wang, G. (2015). The complementary relationship and generation of the Budyko functions. *Geophysical Research Letters*, 42(6), 1781-1790.

3. Budyko, M. I. (1974). *Climate and Life*. Academic Press.

---

**Note**: This repository provides the computational framework. Real observational data (Fluxnet2015) and model simulations (CMIP6) need to be downloaded separately from their respective sources due to size and licensing constraints.
