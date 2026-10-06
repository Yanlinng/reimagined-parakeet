# 第五项：进阶挑战（PySpice 三电路）

本提交包只对应任务书第五项，选择方案 1：使用 PySpice 完成三个电路。

## 文件

```text
.
├── rc_low_pass.py
├── thevenin.py
├── nmos_common_source.py
├── requirements.txt
├── 第五项报告.pdf
├── report.html
├── report.css
├── figures/
│   ├── rc_low_pass_circuit.svg
│   ├── rc_transient_reference.svg
│   ├── rc_bode_reference.svg
│   ├── thevenin_circuit.svg
│   ├── nmos_common_source.svg
│   └── nmos_transient_reference.svg
└── results/
    ├── rc_results_reference.csv
    ├── thevenin_results_reference.csv
    └── nmos_results_reference.csv
```

## 三个电路

### 1. RC 低通滤波

自选参数：

```text
R = 1.6 kΩ
C = 100 nF
输入方波 = 0 V / 1 V，1 kHz
```

理论截止频率：

```text
τ = RC
  = 1600 × 100 × 10^-9
  = 1.60 × 10^-4 s

fc = 1 / (2πRC)
   = 1 / (2π × 1.6 × 10^3 × 100 × 10^-9)
   = 994.718 Hz
```

1 kHz 时的理论响应：

```text
|H| = 1 / sqrt(1 + (f/fc)²)
    = 0.70752

20 log10(|H|) = -3.008 dB
φ = -atan(f/fc) = -45.15°
```

### 2. 戴维南定理验证

自选含源二端网络：

```text
Vs = 12 V
R1 = 2 kΩ，串联
R2 = 4 kΩ，并联在输出端口
RL = 2 kΩ
端口 A-B 位于 R2 两端
```

开路电压：

```text
Voc = Vs × R2 / (R1 + R2)
    = 12 × 4000 / (2000 + 4000)
    = 8 V
```

短路电流：

```text
Isc = Vs / R1
    = 12 / 2000
    = 6 mA
```

等效内阻：

```text
Rth = R1 || R2
    = (2000 × 4000) / (2000 + 4000)
    = 1333.333 Ω
```

接入 2 kΩ 负载后的理论端口量：

```text
VL = Voc × RL / (Rth + RL)
   = 8 × 2000 / (1333.333 + 2000)
   = 4.8 V

IL = 4.8 / 2000
   = 2.4 mA
```

### 3. NMOS 共源级放大电路

题卡固定参数：

```text
VDD = 5 V
Rg1 = 60 kΩ
Rg2 = 40 kΩ
Rd = 2 kΩ
KP = 0.8 mA/V²
Vth = 1 V
λ = 0.02 /V
W/L = 1
Vi = 10 mV，1 kHz 正弦波
```

静态栅极电压：

```text
VG = VDD × Rg2 / (Rg1 + Rg2)
   = 5 × 40 / (60 + 40)
   = 2 V

VGS = 2 V
Vov = VGS - Vth = 1 V
```

按 SPICE Level-1 NMOS 模型：

```text
ID = (KP/2) × Vov² × (1 + λVDS)
VDS = VDD - ID × Rd
```

联立解得：

```text
ID = 0.43307 mA
VDS = 5 - 0.43307 × 2
    = 4.13386 V
```

饱和区判断：

```text
VDS = 4.13386 V
VGS - Vth = 1 V
VDS > VGS - Vth
结论：工作在饱和区
```

小信号参数：

```text
gm = 2ID / Vov
   = 2 × 0.43307 / 1
   = 0.86614 mS

ro = 1 / (λID)
   = 1 / (0.02 × 0.43307 × 10^-3)
   = 115.455 kΩ

Rout = Rd || ro
     = 1.96594 kΩ

Av = -gm × Rout
   = -0.86614 × 10^-3 × 1965.94
   = -1.70279
```

输入正弦波幅值为 10 mV，因此输出幅值约为：

```text
|Vout| = 10 mV × 1.70279
       = 17.03 mV
```

输出与输入反相。

## 理论值与 PySpice 参考值

### RC 低通

| 指标 | 手算值 | PySpice 参考值 | 误差控制 |
|---|---:|---:|---:|
| `fc` | 994.718 Hz | 994.7 Hz | ±0.5% |
| 1 kHz 幅频 | -3.008 dB | -3.0 dB | ±0.2 dB |
| 1 kHz 相频 | -45.15° | -45.1° | ±1° |

### 戴维南

| 场景 | 指标 | 手算值 | PySpice 参考值 |
|---|---|---:|---:|
| 原电路开路 | `Voc` | 8.000 V | 8.000 V |
| 原电路短路 | `Isc` | 6.000 mA | 6.000 mA |
| 原电路接负载 | `VL` | 4.800 V | 4.800 V |
| 原电路接负载 | `IL` | 2.400 mA | 2.400 mA |
| 等效电路接负载 | `VL` | 4.800 V | 4.800 V |
| 等效电路接负载 | `IL` | 2.400 mA | 2.400 mA |

### NMOS 共源级

| 指标 | 手算值 | PySpice 参考值 |
|---|---:|---:|
| `VGS` | 2.000 V | 2.000 V |
| `ID` | 0.4331 mA | 0.433 mA |
| `VDS` | 4.1339 V | 4.134 V |
| `gm` | 0.8661 mS | 0.866 mS |
| `ro` | 115.455 kΩ | 115.5 kΩ |
| `Rout` | 1.9659 kΩ | 1.966 kΩ |
| `Av` | -1.7028 | -1.703 |
| 输出幅值 | 17.03 mV | 17.03 mV |

## 运行

建议使用 Python 3.10 或 3.11，并先安装 ngspice。

Windows PowerShell：

```powershell
python -m pip install -r requirements.txt
$env:NGSPICE_LIBRARY_PATH = "C:\path\to\ngspice.dll"
python rc_low_pass.py
python thevenin.py
python nmos_common_source.py
```

Linux：

```bash
sudo apt install ngspice
python -m pip install -r requirements.txt
python rc_low_pass.py
python thevenin.py
python nmos_common_source.py
```

运行后将生成：

- `results/rc_transient.csv`
- `results/rc_bode.csv`
- `results/rc_summary.csv`
- `results/thevenin_results.csv`
- `results/nmos_operating_point.csv`
- `results/nmos_transient.csv`
- `results/nmos_ac.csv`
- `results/nmos_summary.csv`
- `figures/generated_rc_transient.png`
- `figures/generated_rc_bode.png`
- `figures/generated_nmos_transient.png`

仓库中带 `_reference` 的图和表是按解析模型计算出的提交参考值。
运行脚本后，以 `generated_*.png` 和普通 CSV 中的 PySpice 实测值为最终结果。

## 代码说明

- `rc_low_pass.py`：直流工作点不需要分析，包含 1 kHz 方波瞬态和 10 Hz 至 1 MHz AC 扫描。
- `thevenin.py`：分别建立开路、短路、原电路带负载和戴维南等效电路带负载四种情况。
- `nmos_common_source.py`：包含 Level-1 MOS 模型、静态工作点、瞬态分析和 AC 增益分析。

三个脚本彼此独立，均可直接运行，不依赖另外两个 Python 文件。

