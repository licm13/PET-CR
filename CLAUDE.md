# CLAUDE.md - AI Assistant Guide for PET-CR Repository

**Last Updated**: 2025-11-21
**Repository**: PET-CR (Complementary Relationship Evapotranspiration Library)
**Version**: 0.3.0
**Primary Language**: Python 3.9+

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Repository Structure](#repository-structure)
3. [Codebase Architecture](#codebase-architecture)
4. [Development Conventions](#development-conventions)
5. [Key Workflows](#key-workflows)
6. [Common Tasks](#common-tasks)
7. [Important Patterns](#important-patterns)
8. [Testing Guidelines](#testing-guidelines)
9. [Documentation Standards](#documentation-standards)
10. [Common Pitfalls](#common-pitfalls)
11. [Reference Materials](#reference-materials)

---

## Project Overview

### Purpose

PET-CR is a comprehensive Python library for estimating actual evapotranspiration (ET) using Complementary Relationship (CR) theory. It integrates **three distinct but complementary approaches**:

1. **Traditional CR Models** - For users with pre-calculated Penman (Ep) and Priestley-Taylor (Ew) ET
2. **Land-Atmosphere Framework** - Based on Zhou & Yu (2025), for energy flux analysis and climate attribution
3. **BGCR-Budyko Model** - For monthly ET estimation with spatial heterogeneity

### Scientific Context

- **Primary Citation**: Zhou & Yu (2025) "Land-atmosphere interactions exacerbate concurrent soil moisture drought and atmospheric aridity" (Nature Climate Change, accepted)
- **Application Areas**: Hydrology, climate science, land-atmosphere interactions, drought analysis
- **Target Users**: Researchers, climate scientists, hydrologists

### Key Features

- ✅ Bilingual documentation (English/Chinese)
- ✅ Strict SI units throughout
- ✅ Literature-referenced implementations
- ✅ Comprehensive examples with visualization
- ✅ Attribution analysis for climate change studies
- ✅ Spatial heterogeneity handling

---

## Repository Structure

```
PET-CR/
├── petcr/                          # Main package (PRIMARY)
│   ├── __init__.py                 # Package API and exports
│   ├── constants.py                # Physical constants (CENTRALIZED)
│   ├── models.py                   # Traditional CR models
│   ├── physics.py                  # Physical calculations (Penman, PT)
│   ├── land_atmosphere.py          # Land-atmosphere PET estimation
│   ├── bgcr_model.py              # BGCR-Budyko monthly model
│   ├── attribution.py             # Budyko framework attribution
│   └── utils.py                   # Data generation and loading
│
├── Zhou_NCC_Code/                  # Original land-atmosphere code (LEGACY)
│   ├── src/                       # Source modules
│   ├── examples/                  # Original examples
│   └── data/                      # Input/output data
│
├── bgcr-budyko/                   # Original BGCR implementation (LEGACY)
│   ├── bgcr_budyko/              # BGCR package
│   │   ├── models/               # BGCR and Penman models
│   │   ├── params/               # Parameter schemes
│   │   ├── io/                   # I/O helpers
│   │   └── utils/                # Math utilities
│   ├── examples/                  # BGCR examples
│   └── tests/                     # BGCR tests
│
├── examples/                       # Main example scripts (START HERE)
│   ├── example_sigmoid.py         # Basic CR model usage
│   ├── example_land_atmosphere.py # Land-atmosphere framework
│   ├── example_attribution_analysis.py  # Attribution analysis
│   ├── compare_models.py          # Compare CR models
│   ├── compare_all_three_methods.py  # Compare all 3 methods
│   ├── advanced_analysis.py       # 30-year trend & extreme events
│   ├── spatial_bgcr_example.py    # Spatial BGCR application
│   ├── calibration_and_uncertainty.py  # Uncertainty analysis
│   ├── real_data_workflow.py      # Real data processing
│   └── figures/                   # Generated figures
│
├── tests/                         # Unit tests
│   └── test_basic.py              # Basic functionality tests
│
├── docs/                          # Documentation
│   └── presentations/             # Teaching materials
│
├── data/                          # Data directory
│   └── output/                    # Output data
│
├── README.md                       # Main documentation (BILINGUAL)
├── REFACTORING_AND_ANALYSIS_REPORT.md  # Recent refactoring details
├── UNIT_CONVERSION_AUDIT_REPORT.md     # Unit consistency audit
├── VERIFICATION_REPORT.md         # Verification results
├── IMPLEMENTATION_SUMMARY.md      # Implementation summary
├── requirements.txt               # Python dependencies
├── setup.py                       # Package installation
└── .gitignore                     # Git ignore patterns
```

### Key Directory Purposes

- **`petcr/`**: The main package - **ALWAYS work here** for new features
- **`Zhou_NCC_Code/`**: Legacy code, retained for reference - **DO NOT MODIFY**
- **`bgcr-budyko/`**: Legacy BGCR code, retained for reference - **DO NOT MODIFY**
- **`examples/`**: **START HERE** to understand usage patterns
- **`tests/`**: Unit tests - **ADD TESTS** for new features

---

## Codebase Architecture

### Module Responsibilities

#### `petcr/constants.py` - Physical Constants Hub

**CRITICAL**: This is the **single source of truth** for all physical constants.

```python
# Key constants defined here:
CP_AIR = 1005.0                    # Specific heat of air [J/(kg·K)]
EPSILON_MOLWEIGHT = 0.62198        # Ratio of water vapor to dry air molecular weight
LAMBDA_DEFAULT = 2.45e6            # Latent heat of vaporization [J/kg]
GAMMA_DEFAULT = 0.067              # Psychrometric constant [kPa/K]
STEFAN_BOLTZMANN = 5.67e-8         # Stefan-Boltzmann constant [W/(m²·K⁴)]
```

**Convention**: NEVER use hardcoded magic numbers. ALWAYS import from `constants`.

#### `petcr/models.py` - Traditional CR Models

Implements 5 classical CR models:
- `sigmoid_cr()` - Han & Tian (2018)
- `polynomial_cr()` - Brutsaert (2015)
- `rescaled_power_cr()` - Szilagyi et al. (2017)
- `bouchet_cr()` - Bouchet (1963)
- `aa_cr()` - Advection-Aridity model

**Key Pattern**: All models accept `ep` (Penman ET) and `ew` (Priestley-Taylor ET) in **W/m²**.

#### `petcr/physics.py` - Physical Calculations

Provides fundamental physics calculations:
- `penman_potential_et()` - Penman equation
- `priestley_taylor_et()` - Priestley-Taylor equation
- `vapor_pressure_deficit()` - VPD calculation
- Psychrometric functions

**Unit Convention**: Temperature in Kelvin [K], Pressure in Pascal [Pa], Energy in W/m²

#### `petcr/land_atmosphere.py` - Land-Atmosphere Framework

Implements Zhou & Yu (2025) framework:
- `calculate_pet_land()` - PETe and PETa for land surfaces
- `calculate_pet_ocean()` - PET for ocean/wet surfaces
- `calculate_wet_bowen_ratio()` - Wet Bowen ratio with constraints
- `batch_calculate_pet()` - Batch processing for time series

**Key Concepts**:
- **PETe** (Energy-based PET): Maximum ET constrained by available energy
- **PETa** (Aerodynamics-based PET): Maximum ET constrained by atmospheric demand

#### `petcr/bgcr_model.py` - BGCR-Budyko Model

Monthly-scale ET estimation:
- `calculate_bgcr_et()` - High-level interface
- `bgcr_monthly()` - Core monthly model
- `calculate_penman_components()` - Erad and Eaero from Penman
- `calculate_budyko_w_from_SI()` - BGCR-1 parameterization
- `calculate_budyko_w_from_SI_albedo()` - BGCR-2 parameterization

**Key Feature**: Handles spatial heterogeneity through distributed Budyko parameter.

#### `petcr/attribution.py` - Attribution Analysis

Climate change attribution using Budyko framework:
- `attribution_analysis()` - Separate climate and land surface effects
- `calibrate_budyko_parameter()` - Calibrate Budyko n parameter
- `projection_1pctCO2()` - Analyze 1pctCO2 experiments

**Use Case**: Quantify contributions of climate change vs land surface changes to ET trends.

#### `petcr/utils.py` - Utility Functions

Data generation and loading:
- `generate_sample_data()` - Generate sample meteorological data
- `generate_timeseries_data()` - Generate time series for attribution
- `load_fluxnet_data()` - Load FLUXNET eddy covariance data
- `load_cmip6_data()` - Load CMIP6 climate model data
- `setup_chinese_font()` - Configure Chinese font for plots

---

## Development Conventions

### 1. Units - **STRICTLY SI UNITS**

**CRITICAL**: The codebase underwent major refactoring (see `REFACTORING_AND_ANALYSIS_REPORT.md`) to ensure unit consistency.

| Variable | Unit | Symbol |
|----------|------|--------|
| Temperature | Kelvin | K |
| Pressure | Pascal | Pa |
| Energy Flux | Watt per square meter | W/m² |
| ET Rate (short-term) | W/m² or mm/day | - |
| Precipitation | mm or mm/month | - |
| Specific Humidity | kg/kg | - |
| Wind Speed | m/s | - |
| Vapor Pressure | kPa (exception) | - |

**Common Conversions**:
```python
# Temperature: °C to K
temp_k = temp_c + 273.15

# Pressure: kPa to Pa
pressure_pa = pressure_kpa * 1000.0

# ET: W/m² to mm/day
et_mm_day = et_w_m2 * 86400 / lambda_vap  # lambda_vap in J/kg
```

### 2. Naming Conventions

**Variables**:
- Use descriptive names: `latent_heat`, not `lh`
- Follow snake_case: `calculate_pet_land`, not `CalculatePetLand`
- Use standard abbreviations:
  - `ep`: Penman potential ET
  - `ew`: Priestley-Taylor ET
  - `ea`: Actual ET
  - `pete`: Energy-based PET
  - `peta`: Aerodynamics-based PET
  - `vpd`: Vapor pressure deficit
  - `rn`: Net radiation
  - `sh`: Sensible heat flux
  - `lh`: Latent heat flux

**Functions**:
- Action verbs: `calculate_`, `estimate_`, `calibrate_`
- Return dictionaries for multiple outputs

**Example**:
```python
def calculate_pet_land(latent_heat, sensible_heat, ...):
    """Calculate PETe and PETa for land surfaces."""
    # ... calculations ...
    return {
        'pete': pete,
        'peta': peta,
        'beta_w': beta_w,
        'et': et
    }
```

### 3. Documentation Standards

**BILINGUAL**: All major functions and modules have English/Chinese documentation.

**Docstring Format**:
```python
def function_name(param1, param2):
    """
    English description.
    中文描述。

    Parameters
    ----------
    param1 : type
        English description [unit]
        中文描述 [单位]
    param2 : type
        English description [unit]
        中文描述 [单位]

    Returns
    -------
    dict
        Dictionary with keys:
        - 'key1': description [unit] / 描述 [单位]
        - 'key2': description [unit] / 描述 [单位]

    Examples
    --------
    >>> result = function_name(100, 50)
    >>> print(result['key1'])

    References
    ----------
    Author (Year). Title. Journal.
    """
```

### 4. Code Quality Standards

Based on recent refactoring work:

1. **NO Magic Numbers**: Use `constants.py` for all physical constants
2. **Input Validation**: Check for NaN, negative values, valid ranges
3. **Numerical Stability**: Use safe division functions (e.g., `_safe_div`)
4. **Physical Constraints**: Apply `np.clip()` or `np.minimum()` to constrain outputs
5. **Type Hints**: Gradually being added, use where appropriate
6. **Error Messages**: Clear, bilingual when possible

**Example**:
```python
from . import constants

def calculate_psychrometric_constant(air_pressure):
    """Calculate psychrometric constant γ."""
    # Input validation
    if air_pressure <= 0:
        raise ValueError("Air pressure must be positive")

    # Use constants, not magic numbers
    cp = constants.CP_AIR
    epsilon = constants.EPSILON_MOLWEIGHT
    lambda_v = constants.LAMBDA_DEFAULT

    # Calculate with clear formula
    gamma = cp * air_pressure / (epsilon * lambda_v)

    return gamma
```

### 5. Import Organization

**Standard Order**:
```python
# 1. Standard library
import numpy as np
import pandas as pd
from typing import Dict, Optional

# 2. Third-party packages
import matplotlib.pyplot as plt
import seaborn as sns

# 3. Local imports (relative)
from . import constants
from .physics import penman_potential_et
from .utils import generate_sample_data
```

**Avoid**: `from module import *`
**Prefer**: Explicit imports from `__init__.py`

---

## Key Workflows

### Workflow 1: Adding a New CR Model

1. **Add implementation to `petcr/models.py`**:
   ```python
   def new_cr_model(ep, ew, param):
       """New CR model implementation."""
       # Input validation
       # Implementation
       # Physical constraints
       return ea
   ```

2. **Export in `petcr/__init__.py`**:
   ```python
   from .models import new_cr_model
   __all__ = [..., 'new_cr_model']
   ```

3. **Add example to `examples/`**:
   ```python
   # examples/example_new_model.py
   import petcr
   ea = petcr.new_cr_model(ep=400, ew=350, param=0.5)
   ```

4. **Add test to `tests/`**:
   ```python
   def test_new_cr_model():
       ea = petcr.new_cr_model(ep=400, ew=350, param=0.5)
       assert ea > 0
       assert ea <= min(400, 350)
   ```

5. **Update README.md**: Add to model table

### Workflow 2: Fixing Unit Issues

**CRITICAL**: Based on `UNIT_CONVERSION_AUDIT_REPORT.md`:

1. **Identify**: Check if hardcoded constant exists
2. **Add to constants.py** if not present
3. **Replace**: Change magic number to `constants.CONSTANT_NAME`
4. **Verify**: Run affected tests
5. **Document**: Note in commit message

**Example from recent fix**:
```python
# BEFORE (line 165 of land_atmosphere.py)
vapor_pressure = mixing_ratio / (mixing_ratio + 0.622) * pressure

# AFTER
from . import constants
vapor_pressure = mixing_ratio / (mixing_ratio + constants.EPSILON_MOLWEIGHT) * pressure
```

### Workflow 3: Creating Examples

Examples are the primary way users learn the library.

**Example Structure**:
```python
"""
Example: Descriptive Title
English description.
中文描述。
"""
import numpy as np
import matplotlib.pyplot as plt
import petcr

# 1. Generate or load data
data = petcr.generate_sample_data(...)

# 2. Perform calculations
results = petcr.some_function(...)

# 3. Analyze results
print(f"Result: {results['key']:.2f} units")

# 4. Visualize
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
# ... plotting code ...
plt.tight_layout()
plt.savefig('examples/figures/example_name.png', dpi=300, bbox_inches='tight')
plt.show()
```

**Naming**: `example_<feature>.py` or `compare_<models>.py`
**Location**: `examples/`
**Output**: Save figures to `examples/figures/`

---

## Common Tasks

### Task 1: Run Examples

```bash
# Navigate to repository root
cd /path/to/PET-CR

# Install package in development mode (if not done)
pip install -e .

# Run examples
python examples/example_sigmoid.py
python examples/example_land_atmosphere.py
python examples/advanced_analysis.py
```

### Task 2: Run Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_basic.py

# Run with coverage
pytest tests/ --cov=petcr --cov-report=html
```

### Task 3: Generate Documentation

```bash
# Build Sphinx docs (if configured)
cd docs/
make html

# View in browser
open _build/html/index.html
```

### Task 4: Add New Physical Constant

```python
# 1. Add to petcr/constants.py
NEW_CONSTANT = 1.234  # Description [unit]

# 2. Document in constants.py docstring

# 3. Use in modules
from . import constants
value = some_calculation * constants.NEW_CONSTANT
```

### Task 5: Debug Unit Mismatches

1. **Check inputs**: Print input values and units
2. **Trace calculations**: Add print statements for intermediate values
3. **Verify constants**: Ensure using correct constant from `constants.py`
4. **Check references**: Compare with original paper equations
5. **Consult audit report**: See `UNIT_CONVERSION_AUDIT_REPORT.md` for known issues

---

## Important Patterns

### Pattern 1: Safe Division

To avoid division by zero:

```python
def _safe_div(numerator, denominator, fill_value=0.0):
    """Safely divide arrays, handling division by zero."""
    result = np.divide(
        numerator,
        denominator,
        out=np.full_like(numerator, fill_value, dtype=float),
        where=(denominator != 0)
    )
    return result
```

Usage: `result = _safe_div(a, b, fill_value=np.nan)`

### Pattern 2: Physical Constraints

Always constrain outputs to physically valid ranges:

```python
# Example: Actual ET cannot exceed wet ET or Penman ET
ea = calculate_cr_model(ep, ew)
ea = np.clip(ea, 0, min(ep, ew))  # Constrain to [0, min(ep, ew)]

# Example: Bowen ratio constraints
beta_w = calculate_bowen_ratio(...)
beta_w = np.clip(beta_w, BETA_W_MIN, BETA_W_MAX)
```

### Pattern 3: Batch Processing

For time series or spatial data:

```python
def batch_process(data_array):
    """Process multiple time steps or grid cells."""
    results = []
    for i in range(len(data_array)):
        result = process_single(data_array[i])
        results.append(result)
    return np.array(results)
```

Or use vectorization:
```python
# Vectorized version (preferred for performance)
results = np.vectorize(process_single)(data_array)
```

### Pattern 4: Multi-Climate Scenario Analysis

See `examples/advanced_analysis.py` for the pattern:

```python
# Define climate scenarios
scenarios = {
    'humid': {'temp': 25, 'rh': 80},
    'arid': {'temp': 30, 'rh': 30},
    # ...
}

# Process each scenario
results = {}
for name, params in scenarios.items():
    results[name] = calculate_et(params)

# Compare results
for name, result in results.items():
    print(f"{name}: EA = {result['ea']:.2f} W/m²")
```

### Pattern 5: Attribution Analysis

Standard workflow for climate attribution:

```python
# 1. Generate or load long-term data (30+ years)
data = petcr.generate_timeseries_data(n_years=140, include_trend=True)

# 2. Perform attribution analysis
results = petcr.attribution_analysis(
    et_timeseries=data['et'],
    pete_timeseries=data['pete'],
    pr_timeseries=data['pr'],
    window_size=30  # 30-year moving window
)

# 3. Separate contributions
climate_contribution = results['et_climate']
landsurf_contribution = results['et_landsurf']
total_change = results['et_total']

# 4. Analyze trends
print(f"Climate contribution: {climate_contribution[-1]:.3f} mm/day")
print(f"Land surface contribution: {landsurf_contribution[-1]:.3f} mm/day")
```

---

## Testing Guidelines

### Test Structure

Located in `tests/` directory:

```python
import pytest
import numpy as np
import petcr

def test_function_basic():
    """Test basic functionality."""
    result = petcr.function(input1, input2)
    assert result > 0
    assert isinstance(result, float)

def test_function_edge_cases():
    """Test edge cases."""
    # Zero input
    result = petcr.function(0, 0)
    assert result == 0

    # Negative input (should raise error)
    with pytest.raises(ValueError):
        petcr.function(-1, 10)

def test_function_arrays():
    """Test array inputs."""
    inputs = np.array([1, 2, 3, 4, 5])
    results = petcr.function(inputs, inputs)
    assert len(results) == len(inputs)
    assert np.all(results >= 0)
```

### Running Tests

```bash
# All tests
pytest tests/

# Specific test
pytest tests/test_basic.py::test_function_basic

# With verbose output
pytest tests/ -v

# With coverage
pytest tests/ --cov=petcr --cov-report=term-missing
```

### Coverage Goals

- **Core modules** (`models.py`, `physics.py`, `land_atmosphere.py`): >80% coverage
- **Utility modules** (`utils.py`): >60% coverage
- **All new functions**: Must have at least basic tests

---

## Documentation Standards

### 1. README.md

**BILINGUAL**: English and Chinese sections

**Structure**:
- Overview
- Key Features
- Installation
- Quick Start (all 3 methods)
- Available Models
- Examples
- Project Structure
- Citation
- Scientific Background

**Updates**: When adding new features, update both English and Chinese sections.

### 2. Docstrings

**Format**: NumPy style

**Required Sections**:
- Description (bilingual)
- Parameters (with units)
- Returns (with units)
- Examples
- References (where applicable)

### 3. Examples as Documentation

Examples serve as **living documentation**. Each example should:
- Be runnable without modification
- Include comments explaining key steps
- Generate visualizations where appropriate
- Print key results with units
- Be referenced in README.md

### 4. Inline Comments

**When to comment**:
- Complex algorithms (reference equation numbers)
- Unit conversions
- Physical constraints and their rationale
- Workarounds for edge cases

**When NOT to comment**:
- Obvious operations (`x = x + 1  # increment x`)
- Self-documenting code with clear variable names

### 5. Commit Messages

**Format**:
```
<type>: <subject>

<body (optional)>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

**Example**:
```
fix: Replace hardcoded epsilon with constants.EPSILON_MOLWEIGHT

Updated land_atmosphere.py line 165 to use centralized constant
instead of hardcoded 0.622. This improves precision and maintainability.

Refs: UNIT_CONVERSION_AUDIT_REPORT.md issue M3
```

---

## Common Pitfalls

### Pitfall 1: Unit Confusion

**Problem**: Mixing °C and K, kPa and Pa

**Solution**:
- ALWAYS use K for temperature in calculations
- Use `constants.py` for conversions
- Add unit checks in input validation

```python
# Bad
def calculate_something(temp_c):
    result = temp_c * some_constant  # Wrong if expecting K

# Good
def calculate_something(temp_k):
    if temp_k < 0:
        raise ValueError("Temperature must be in Kelvin (K)")
    result = temp_k * some_constant
```

### Pitfall 2: Modifying Legacy Code

**Problem**: Tempted to modify `Zhou_NCC_Code/` or `bgcr-budyko/`

**Solution**: These directories are **LEGACY REFERENCES**. All active development happens in `petcr/`. If you need functionality from legacy code:
1. Extract the function
2. Refactor and add to appropriate `petcr/` module
3. Add tests
4. Update documentation

### Pitfall 3: Ignoring Physical Constraints

**Problem**: Calculated values that violate physical laws (negative ET, EA > EP)

**Solution**: Apply constraints immediately after calculation:

```python
# Calculate
ea = some_cr_model(ep, ew)

# Constrain - actual ET cannot exceed potential ET
ea = np.minimum(ea, ep)
ea = np.maximum(ea, 0)  # Cannot be negative

# Or use clip
ea = np.clip(ea, 0, min(ep, ew))
```

### Pitfall 4: Not Handling NaN/Inf

**Problem**: Missing data or division by zero propagates NaN through calculations

**Solution**:
```python
# Check inputs
if np.any(np.isnan(input_data)):
    raise ValueError("Input contains NaN values")

# Use safe division
result = _safe_div(numerator, denominator, fill_value=np.nan)

# Or handle explicitly
with np.errstate(divide='ignore', invalid='ignore'):
    result = numerator / denominator
    result[~np.isfinite(result)] = fill_value
```

### Pitfall 5: Hardcoding File Paths

**Problem**: Examples with absolute paths won't run on other systems

**Solution**: Use relative paths and pathlib:

```python
from pathlib import Path

# Get repository root
repo_root = Path(__file__).parent.parent
data_dir = repo_root / 'data' / 'input'
output_dir = repo_root / 'examples' / 'figures'

# Create output directory if needed
output_dir.mkdir(parents=True, exist_ok=True)

# Use in operations
output_file = output_dir / 'result.png'
plt.savefig(output_file)
```

### Pitfall 6: Forgetting Bilingual Documentation

**Problem**: Adding English-only documentation

**Solution**: When adding or modifying docstrings:
1. Write English first
2. Add Chinese translation immediately after
3. Ensure both are accurate and complete
4. If uncertain about translation, mark with `# TODO: Verify Chinese translation`

### Pitfall 7: Breaking Changes Without Notice

**Problem**: Changing function signatures or return types breaks existing user code

**Solution**:
1. **Deprecation path**: Keep old function, add new one
2. **Semantic versioning**: Major version bump for breaking changes
3. **Migration guide**: Document in changelog/migration guide
4. **Warning messages**: Use `warnings.warn()` for deprecated features

```python
import warnings

def old_function(x):
    warnings.warn(
        "old_function is deprecated, use new_function instead",
        DeprecationWarning,
        stacklevel=2
    )
    return new_function(x)
```

---

## Reference Materials

### Key Documents

1. **README.md** - Primary user documentation (bilingual)
2. **REFACTORING_AND_ANALYSIS_REPORT.md** - Recent code quality improvements
3. **UNIT_CONVERSION_AUDIT_REPORT.md** - Unit consistency audit and fixes
4. **VERIFICATION_REPORT.md** - Verification of implementations
5. **IMPLEMENTATION_SUMMARY.md** - Implementation details

### Scientific References

1. **Zhou & Yu (2025)** - Nature Climate Change (accepted)
   - Land-atmosphere framework
   - PETe/PETa concepts
   - Attribution methodology

2. **Han & Tian (2018)** - Sigmoid CR model

3. **Brutsaert (2015)** - Polynomial CR model

4. **Szilagyi et al. (2017)** - Rescaled power CR model

5. **Bouchet (1963)** - Original CR hypothesis

6. **Yang et al. (2006)** - BGCR-Budyko model

### External Resources

- **FLUXNET**: Eddy covariance flux data
- **CMIP6**: Climate model output
- **FAO-56**: Reference evapotranspiration guidelines

### Dependencies

```
numpy>=1.20.0        # Numerical computing
pandas>=1.3.0        # Data structures
scipy>=1.7.0         # Scientific computing
matplotlib>=3.4.0    # Plotting
seaborn>=0.11.0      # Statistical visualization
netCDF4>=1.5.7       # NetCDF file handling
xarray>=0.19.0       # Labeled arrays
pytest>=6.2.0        # Testing framework
pytest-cov>=2.12.0   # Coverage reporting
```

### Development Tools

- **Python**: 3.9+
- **Git**: Version control
- **pytest**: Testing framework
- **Sphinx** (optional): Documentation generation
- **black** (optional): Code formatting
- **flake8** (optional): Linting

---

## Quick Reference Card

### Import Cheatsheet

```python
import petcr

# Traditional CR models
ea = petcr.sigmoid_cr(ep, ew, beta)
ea = petcr.bouchet_cr(ep, ew)

# Land-atmosphere framework
results = petcr.calculate_pet_land(lh, sh, q, p, ta, ts)
pete = results['pete']
peta = results['peta']

# BGCR-Budyko model
results = petcr.calculate_bgcr_et(rn, temp, u, ea, es, precip, si, albedo)
et = results['et']

# Attribution analysis
results = petcr.attribution_analysis(et, pete, pr, window_size=30)

# Utilities
data = petcr.generate_sample_data(...)
petcr.setup_chinese_font()
```

### Common Unit Conversions

```python
# Temperature
temp_k = temp_c + 273.15

# Pressure
pressure_pa = pressure_kpa * 1000

# ET: W/m² to mm/day
lambda_v = 2.45e6  # J/kg
et_mm_day = et_w_m2 * 86400 / lambda_v

# ET: mm/day to W/m²
et_w_m2 = et_mm_day * lambda_v / 86400
```

### File Locations

- **Constants**: `petcr/constants.py`
- **CR Models**: `petcr/models.py`
- **Examples**: `examples/`
- **Tests**: `tests/`
- **Figures**: `examples/figures/`

### Quick Commands

```bash
# Install
pip install -e .

# Test
pytest tests/ -v

# Run example
python examples/example_sigmoid.py

# Check for issues (if flake8 installed)
flake8 petcr/ --max-line-length=100
```

---

## Version History

- **v0.3.0** (Current): Integrated BGCR-Budyko model (Method 3)
- **v0.2.0**: Added land-atmosphere framework and attribution analysis
- **v0.1.0**: Initial release with traditional CR models

---

## Contributing Guidelines

### For AI Assistants

When working on this codebase:

1. ✅ **READ** `README.md` first for context
2. ✅ **EXPLORE** `examples/` to understand usage patterns
3. ✅ **CHECK** `constants.py` before adding physical constants
4. ✅ **VERIFY** units are correct and consistent
5. ✅ **TEST** new functionality with `pytest`
6. ✅ **DOCUMENT** in bilingual format (English/Chinese)
7. ✅ **CONSTRAIN** outputs to physically valid ranges
8. ❌ **DO NOT** modify `Zhou_NCC_Code/` or `bgcr-budyko/` directories
9. ❌ **DO NOT** use magic numbers - use `constants.py`
10. ❌ **DO NOT** break backward compatibility without versioning

### Questions to Ask Before Coding

1. Does this feature belong in `petcr/` or should it be an example?
2. Are there existing functions I can reuse?
3. What physical constraints apply to the outputs?
4. What units should inputs and outputs use?
5. Can this be vectorized for array inputs?
6. How will this be tested?
7. Does this need bilingual documentation?

---

## Contact and Support

- **Issues**: Report via GitHub issues
- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory
- **Primary Author**: Sha Zhou (shazhou21@bnu.edu.cn)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-21
**Maintainer**: AI Assistant (Claude)

---

**This document is a living guide. Update it as the codebase evolves.**
