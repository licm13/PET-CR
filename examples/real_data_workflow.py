"""
真实数据工作流示例 / Real Data Workflow Example

这个示例展示如何将PET-CR库应用于真实气象站数据的完整工作流：
1. 数据加载和预处理
2. 数据质量控制
3. 批量计算蒸散发
4. 结果验证和导出
5. 误差分析

This example demonstrates a complete workflow for applying PET-CR to real
meteorological station data:
1. Data loading and preprocessing
2. Data quality control
3. Batch ET calculation
4. Results validation and export
5. Error analysis

数据格式示例 / Example data format:
    date,temperature,relative_humidity,net_radiation,wind_speed,pressure
    2023-01-01,15.5,65.3,280.5,2.1,101325
    2023-01-02,16.2,62.8,295.3,1.8,101280
    ...
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings

try:
    from petcr import (
        sigmoid_cr, polynomial_cr, rescaled_power_cr, bouchet_cr, aa_cr,
        penman_potential_et, priestley_taylor_et,
        vapor_pressure_deficit
    )
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from petcr import (
        sigmoid_cr, polynomial_cr, rescaled_power_cr, bouchet_cr, aa_cr,
        penman_potential_et, priestley_taylor_et,
        vapor_pressure_deficit
    )


class MeteoDataProcessor:
    """
    气象数据处理器
    Meteorological data processor

    这个类封装了从原始气象数据到蒸散发估算的完整流程
    This class encapsulates the complete workflow from raw meteorological
    data to ET estimation
    """

    def __init__(self, ground_heat_flux: float = 50.0):
        """
        初始化数据处理器
        Initialize data processor

        Parameters
        ----------
        ground_heat_flux : float
            土壤热通量 [W/m²]，默认50 W/m²
            Ground heat flux [W/m²], default 50 W/m²
        """
        self.ground_heat_flux = ground_heat_flux
        self.data = {}
        self.quality_flags = {}
        self.results = {}

    def load_data(self, temperature: np.ndarray,
                  relative_humidity: np.ndarray,
                  net_radiation: np.ndarray,
                  wind_speed: np.ndarray,
                  pressure: Optional[np.ndarray] = None,
                  dates: Optional[List] = None) -> None:
        """
        加载气象数据
        Load meteorological data

        Parameters
        ----------
        temperature : array_like
            气温 [°C] / Air temperature [°C]
        relative_humidity : array_like
            相对湿度 [%] / Relative humidity [%]
        net_radiation : array_like
            净辐射 [W/m²] / Net radiation [W/m²]
        wind_speed : array_like
            风速 [m/s] / Wind speed [m/s]
        pressure : array_like, optional
            大气压强 [Pa]，如未提供则使用标准大气压
            Atmospheric pressure [Pa], uses standard pressure if not provided
        dates : list, optional
            日期列表 / List of dates
        """
        n_records = len(temperature)

        self.data = {
            'temperature': np.asarray(temperature),
            'relative_humidity': np.asarray(relative_humidity),
            'net_radiation': np.asarray(net_radiation),
            'wind_speed': np.asarray(wind_speed),
            'pressure': np.asarray(pressure) if pressure is not None else np.full(n_records, 101325.0),
        }

        if dates is not None:
            self.data['dates'] = dates
        else:
            # 生成默认日期序列 / Generate default date sequence
            start_date = datetime(2023, 1, 1)
            self.data['dates'] = [start_date + timedelta(days=i) for i in range(n_records)]

        print(f"已加载 {n_records} 条气象数据记录")
        print(f"Loaded {n_records} meteorological data records")

    def quality_control(self, verbose: bool = True) -> Dict[str, int]:
        """
        数据质量控制
        Data quality control

        检查数据的物理合理性和完整性
        Check physical reasonableness and completeness of data

        Parameters
        ----------
        verbose : bool
            是否打印详细信息 / Whether to print detailed information

        Returns
        -------
        dict
            质量控制统计 / Quality control statistics
        """
        if verbose:
            print("\n" + "=" * 80)
            print("数据质量控制 / Data Quality Control")
            print("=" * 80)

        n_records = len(self.data['temperature'])
        qc_stats = {
            'total_records': n_records,
            'flagged_records': 0,
            'issues': {}
        }

        # 初始化质量标志 (True表示数据良好) / Initialize quality flags
        self.quality_flags = {
            'temperature': np.ones(n_records, dtype=bool),
            'relative_humidity': np.ones(n_records, dtype=bool),
            'net_radiation': np.ones(n_records, dtype=bool),
            'wind_speed': np.ones(n_records, dtype=bool),
            'overall': np.ones(n_records, dtype=bool),
        }

        # 1. 检查气温范围 (-50°C to 60°C) / Check temperature range
        temp_flags = (self.data['temperature'] >= -50) & (self.data['temperature'] <= 60)
        temp_issues = np.sum(~temp_flags)
        self.quality_flags['temperature'] = temp_flags
        qc_stats['issues']['temperature'] = temp_issues

        if verbose and temp_issues > 0:
            print(f"⚠ 警告: {temp_issues} 条记录的气温超出合理范围 [-50, 60]°C")
            print(f"⚠ Warning: {temp_issues} records with temperature out of range [-50, 60]°C")

        # 2. 检查相对湿度范围 (0-100%) / Check relative humidity range
        rh_flags = (self.data['relative_humidity'] >= 0) & (self.data['relative_humidity'] <= 100)
        rh_issues = np.sum(~rh_flags)
        self.quality_flags['relative_humidity'] = rh_flags
        qc_stats['issues']['relative_humidity'] = rh_issues

        if verbose and rh_issues > 0:
            print(f"⚠ 警告: {rh_issues} 条记录的相对湿度超出范围 [0, 100]%")
            print(f"⚠ Warning: {rh_issues} records with RH out of range [0, 100]%")

        # 3. 检查净辐射范围 (-200 to 1500 W/m²) / Check net radiation range
        rad_flags = (self.data['net_radiation'] >= -200) & (self.data['net_radiation'] <= 1500)
        rad_issues = np.sum(~rad_flags)
        self.quality_flags['net_radiation'] = rad_flags
        qc_stats['issues']['net_radiation'] = rad_issues

        if verbose and rad_issues > 0:
            print(f"⚠ 警告: {rad_issues} 条记录的净辐射超出范围 [-200, 1500] W/m²")
            print(f"⚠ Warning: {rad_issues} records with net radiation out of range")

        # 4. 检查风速范围 (0-50 m/s) / Check wind speed range
        ws_flags = (self.data['wind_speed'] >= 0) & (self.data['wind_speed'] <= 50)
        ws_issues = np.sum(~ws_flags)
        self.quality_flags['wind_speed'] = ws_flags
        qc_stats['issues']['wind_speed'] = ws_issues

        if verbose and ws_issues > 0:
            print(f"⚠ 警告: {ws_issues} 条记录的风速超出范围 [0, 50] m/s")
            print(f"⚠ Warning: {ws_issues} records with wind speed out of range")

        # 5. 计算总体质量标志 / Calculate overall quality flag
        self.quality_flags['overall'] = (
            temp_flags & rh_flags & rad_flags & ws_flags
        )

        total_issues = np.sum(~self.quality_flags['overall'])
        qc_stats['flagged_records'] = total_issues

        if verbose:
            print("\n质量控制总结 / Quality Control Summary:")
            print("-" * 80)
            print(f"总记录数 / Total records: {n_records}")
            print(f"良好记录 / Good records: {n_records - total_issues} ({(n_records-total_issues)/n_records*100:.1f}%)")
            print(f"标记记录 / Flagged records: {total_issues} ({total_issues/n_records*100:.1f}%)")

        return qc_stats

    def calculate_et(self, models: Optional[List[str]] = None,
                    use_only_good_data: bool = True) -> Dict[str, np.ndarray]:
        """
        批量计算蒸散发
        Batch calculate evapotranspiration

        Parameters
        ----------
        models : list of str, optional
            要使用的模型列表，默认使用所有模型
            List of models to use, defaults to all models
        use_only_good_data : bool
            是否只使用质量良好的数据 / Whether to use only good quality data

        Returns
        -------
        dict
            包含所有蒸散发计算结果的字典 / Dictionary with all ET calculation results
        """
        print("\n" + "=" * 80)
        print("计算蒸散发 / Calculating Evapotranspiration")
        print("=" * 80)

        # 如果没有运行质量控制，先运行 / Run QC if not already done
        if not self.quality_flags:
            self.quality_control(verbose=False)

        # 准备数据 / Prepare data
        if use_only_good_data:
            # 只使用质量良好的数据 / Use only good quality data
            good_indices = self.quality_flags['overall']
            n_good = np.sum(good_indices)
            print(f"使用 {n_good} 条质量良好的记录进行计算")
            print(f"Using {n_good} good quality records for calculation")

            # 提取良好数据 / Extract good data
            temp = self.data['temperature'][good_indices]
            rh = self.data['relative_humidity'][good_indices]
            rad = self.data['net_radiation'][good_indices]
            ws = self.data['wind_speed'][good_indices]
            pres = self.data['pressure'][good_indices]
        else:
            temp = self.data['temperature']
            rh = self.data['relative_humidity']
            rad = self.data['net_radiation']
            ws = self.data['wind_speed']
            pres = self.data['pressure']
            print(f"使用全部 {len(temp)} 条记录进行计算")
            print(f"Using all {len(temp)} records for calculation")

        # 计算Ep (Penman) / Calculate Ep
        print("  计算Penman潜在蒸散发... / Calculating Penman potential ET...")
        ep = penman_potential_et(
            net_radiation=rad,
            ground_heat_flux=self.ground_heat_flux,
            temperature=temp,
            relative_humidity=rh,
            wind_speed=ws,
            pressure=pres
        )

        # 计算Ew (Priestley-Taylor) / Calculate Ew
        print("  计算Priestley-Taylor湿环境蒸散发... / Calculating P-T wet-environment ET...")
        ew = priestley_taylor_et(
            net_radiation=rad,
            ground_heat_flux=self.ground_heat_flux,
            temperature=temp,
            pressure=pres,
            alpha=1.26
        )

        # 存储基础结果 / Store base results
        self.results = {
            'Ep': ep,
            'Ew': ew,
            'quality_mask': good_indices if use_only_good_data else np.ones(len(temp), dtype=bool),
        }

        # 定义可用的模型 / Define available models
        available_models = {
            'Sigmoid': lambda: sigmoid_cr(ep, ew, beta=0.5),
            'Polynomial': lambda: polynomial_cr(ep, ew, b=2.0),
            'Rescaled_Power': lambda: rescaled_power_cr(ep, ew, n=0.5),
            'Bouchet': lambda: bouchet_cr(ep, ew),
            'AA': lambda: aa_cr(ep, ew),
        }

        # 如果未指定模型，使用所有模型 / Use all models if not specified
        if models is None:
            models = list(available_models.keys())

        # 计算每个模型的Ea / Calculate Ea for each model
        print("  应用CR模型... / Applying CR models...")
        for model_name in models:
            if model_name in available_models:
                print(f"    - {model_name}")
                self.results[model_name] = available_models[model_name]()
            else:
                warnings.warn(f"未知模型: {model_name} / Unknown model: {model_name}")

        print(f"\n完成! 计算了 {len(models)} 个模型的结果")
        print(f"Done! Calculated results for {len(models)} models")

        return self.results

    def validate_results(self) -> Dict:
        """
        验证计算结果的物理合理性
        Validate physical reasonableness of calculation results

        Returns
        -------
        dict
            验证统计 / Validation statistics
        """
        print("\n" + "=" * 80)
        print("结果验证 / Results Validation")
        print("=" * 80)

        if not self.results:
            print("错误: 尚未计算结果 / Error: No results calculated yet")
            return {}

        validation_stats = {}

        # 检查物理约束: 0 ≤ Ea ≤ Ew
        # Check physical constraint: 0 ≤ Ea ≤ Ew
        for model_name, ea in self.results.items():
            if model_name in ['Ep', 'Ew', 'quality_mask']:
                continue

            ew = self.results['Ew']

            # 检查非负性 / Check non-negativity
            negative_count = np.sum(ea < 0)

            # 检查是否超过Ew / Check if exceeding Ew
            exceed_count = np.sum(ea > ew * 1.01)  # 允许1%的数值误差

            # 计算Ea/Ew比值统计 / Calculate Ea/Ew ratio statistics
            ratio = ea / ew
            ratio_stats = {
                'mean': np.mean(ratio),
                'std': np.std(ratio),
                'min': np.min(ratio),
                'max': np.max(ratio),
            }

            validation_stats[model_name] = {
                'negative_count': negative_count,
                'exceed_ew_count': exceed_count,
                'ea_ew_ratio': ratio_stats,
            }

            print(f"\n{model_name}模型:")
            print(f"  负值数量 / Negative values: {negative_count}")
            print(f"  超过Ew的数量 / Exceeding Ew: {exceed_count}")
            print(f"  Ea/Ew比值 / Ea/Ew ratio: "
                  f"均值={ratio_stats['mean']:.3f}, "
                  f"范围=[{ratio_stats['min']:.3f}, {ratio_stats['max']:.3f}]")

        return validation_stats

    def export_results(self, filename: str = 'et_results.csv',
                      include_dates: bool = True) -> None:
        """
        导出计算结果到CSV文件
        Export calculation results to CSV file

        Parameters
        ----------
        filename : str
            输出文件名 / Output filename
        include_dates : bool
            是否包含日期列 / Whether to include date column
        """
        if not self.results:
            print("错误: 尚未计算结果 / Error: No results calculated yet")
            return

        print("\n" + "=" * 80)
        print("导出结果 / Exporting Results")
        print("=" * 80)

        # 准备导出数据 / Prepare export data
        export_lines = []

        # 构建表头 / Build header
        header_parts = []
        if include_dates and 'dates' in self.data:
            header_parts.append('date')

        # 添加输入变量 / Add input variables
        header_parts.extend(['temperature', 'relative_humidity', 'net_radiation', 'wind_speed'])

        # 添加计算结果 / Add calculation results
        result_columns = [key for key in self.results.keys()
                         if key not in ['quality_mask']]
        header_parts.extend(result_columns)

        export_lines.append(','.join(header_parts))

        # 准备数据行 / Prepare data rows
        n_records = len(self.data['temperature'])
        quality_mask = self.results.get('quality_mask', np.ones(n_records, dtype=bool))

        for i in range(n_records):
            if not quality_mask[i]:
                continue  # 跳过质量不良的记录 / Skip poor quality records

            row_parts = []

            # 添加日期 / Add date
            if include_dates and 'dates' in self.data:
                date_str = self.data['dates'][i].strftime('%Y-%m-%d')
                row_parts.append(date_str)

            # 添加输入数据 / Add input data
            row_parts.append(f"{self.data['temperature'][i]:.2f}")
            row_parts.append(f"{self.data['relative_humidity'][i]:.2f}")
            row_parts.append(f"{self.data['net_radiation'][i]:.2f}")
            row_parts.append(f"{self.data['wind_speed'][i]:.2f}")

            # 添加计算结果 / Add calculation results
            for col in result_columns:
                # 需要找到对应的索引 (考虑到可能有质量筛选)
                # Need to find corresponding index (considering quality filtering)
                if np.sum(quality_mask[:i+1]) <= len(self.results[col]):
                    idx = np.sum(quality_mask[:i+1]) - 1
                    row_parts.append(f"{self.results[col][idx]:.2f}")
                else:
                    row_parts.append('NA')

            export_lines.append(','.join(row_parts))

        # 写入文件 / Write to file
        with open(filename, 'w') as f:
            f.write('\n'.join(export_lines))

        print(f"结果已导出到: {filename}")
        print(f"Results exported to: {filename}")
        print(f"导出了 {len(export_lines)-1} 行数据")
        print(f"Exported {len(export_lines)-1} rows of data")


def create_sample_data(n_days: int = 30) -> Dict[str, np.ndarray]:
    """
    创建示例气象数据
    Create sample meteorological data

    Parameters
    ----------
    n_days : int
        天数 / Number of days

    Returns
    -------
    dict
        示例数据字典 / Sample data dictionary
    """
    print("=" * 80)
    print("创建示例数据 / Creating Sample Data")
    print("=" * 80)
    print(f"生成 {n_days} 天的模拟气象数据")
    print(f"Generating {n_days} days of synthetic meteorological data")
    print()

    # 生成模拟数据 / Generate synthetic data
    t = np.arange(n_days)

    # 温度: 20°C基准，±10°C季节波动 / Temperature: 20°C baseline, ±10°C seasonal
    temperature = 20 + 10 * np.sin(2 * np.pi * t / 365) + np.random.randn(n_days) * 2

    # 相对湿度: 60%基准，±20%波动 / RH: 60% baseline, ±20% variation
    relative_humidity = 60 + 20 * np.sin(2 * np.pi * t / 365 + np.pi/2) + np.random.randn(n_days) * 5
    relative_humidity = np.clip(relative_humidity, 20, 95)

    # 净辐射: 400 W/m²基准 / Net radiation: 400 W/m² baseline
    net_radiation = 400 + 200 * np.sin(2 * np.pi * t / 365) + np.random.randn(n_days) * 50
    net_radiation = np.maximum(net_radiation, 100)

    # 风速: 2 m/s基准 / Wind speed: 2 m/s baseline
    wind_speed = 2 + 1 * np.sin(2 * np.pi * t / 365) + np.random.randn(n_days) * 0.5
    wind_speed = np.maximum(wind_speed, 0.1)

    # 大气压强: 标准大气压 ± 小幅波动 / Pressure: standard ± small variation
    pressure = 101325 + np.random.randn(n_days) * 500

    # 生成日期 / Generate dates
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(n_days)]

    return {
        'temperature': temperature,
        'relative_humidity': relative_humidity,
        'net_radiation': net_radiation,
        'wind_speed': wind_speed,
        'pressure': pressure,
        'dates': dates,
    }


def main():
    """主函数 / Main function"""
    print("\n")
    print("=" * 80)
    print("PET-CR 真实数据工作流示例 / PET-CR Real Data Workflow Example")
    print("=" * 80)
    print()

    # 创建示例数据 (模拟真实站点数据)
    # Create sample data (simulating real station data)
    sample_data = create_sample_data(n_days=90)  # 90天数据 / 90 days

    # 初始化数据处理器 / Initialize data processor
    processor = MeteoDataProcessor(ground_heat_flux=50.0)

    # 加载数据 / Load data
    print("\n" + "=" * 80)
    print("加载数据 / Loading Data")
    print("=" * 80)
    processor.load_data(
        temperature=sample_data['temperature'],
        relative_humidity=sample_data['relative_humidity'],
        net_radiation=sample_data['net_radiation'],
        wind_speed=sample_data['wind_speed'],
        pressure=sample_data['pressure'],
        dates=sample_data['dates']
    )

    # 数据质量控制 / Data quality control
    qc_stats = processor.quality_control(verbose=True)

    # 计算蒸散发 / Calculate ET
    # 可以指定特定模型，例如: models=['Sigmoid', 'Bouchet']
    # Can specify specific models, e.g.: models=['Sigmoid', 'Bouchet']
    results = processor.calculate_et(models=None, use_only_good_data=True)

    # 验证结果 / Validate results
    validation_stats = processor.validate_results()

    # 统计摘要 / Statistical summary
    print("\n" + "=" * 80)
    print("统计摘要 / Statistical Summary")
    print("=" * 80)
    print(f"\n{'变量/Variable':<20} {'均值/Mean':<12} {'标准差/Std':<12} "
          f"{'最小值/Min':<12} {'最大值/Max':<12}")
    print("-" * 80)

    for key, values in results.items():
        if key == 'quality_mask':
            continue
        print(f"{key:<20} {np.mean(values):<12.2f} {np.std(values):<12.2f} "
              f"{np.min(values):<12.2f} {np.max(values):<12.2f}")

    # 导出结果 / Export results
    # processor.export_results(filename='et_results.csv', include_dates=True)

    print("\n" + "=" * 80)
    print("工作流程完成! / Workflow Completed!")
    print("=" * 80)
    print()
    print("使用提示 / Usage Tips:")
    print("-" * 80)
    print("1. 替换 create_sample_data() 为你自己的数据加载函数")
    print("   Replace create_sample_data() with your own data loading function")
    print()
    print("2. 根据需要调整质量控制阈值")
    print("   Adjust quality control thresholds as needed")
    print()
    print("3. 选择适合你研究区域的CR模型")
    print("   Select CR models suitable for your study region")
    print()
    print("4. 取消注释 export_results() 来保存结果")
    print("   Uncomment export_results() to save results")
    print()
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
