"""NMOS common-source amplifier: DC operating point, gain and transient response."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import u_Hz, u_kHz, u_MHz, u_ms, u_mV, u_uF, u_um, u_us


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

VDD = 5.0
RG1_OHM = 60_000.0
RG2_OHM = 40_000.0
RD_OHM = 2_000.0
KP = 0.8e-3
VTH = 1.0
LAMBDA = 0.02
INPUT_AMPLITUDE_V = 0.010
INPUT_FREQUENCY_HZ = 1_000.0


def as_ndarray(values) -> np.ndarray:
    if hasattr(values, "as_ndarray"):
        values = values.as_ndarray()
    return np.asarray(values, dtype=float)


def scalar(value) -> float:
    if hasattr(value, "as_ndarray"):
        return float(value.as_ndarray().reshape(-1)[0])
    return float(value)


def solve_theoretical_operating_point() -> tuple[float, float, float, float, float]:
    vg = VDD * RG2_OHM / (RG1_OHM + RG2_OHM)
    vov = vg - VTH
    coefficient = 0.5 * KP * vov**2
    # ID = coefficient * (1 + lambda * (VDD - ID * RD)).
    id_a = coefficient * (1.0 + LAMBDA * VDD) / (
        1.0 + coefficient * LAMBDA * RD_OHM
    )
    vds = VDD - id_a * RD_OHM
    gm = KP * vov * (1.0 + LAMBDA * vds)
    return vg, id_a, vds, gm, vov


def build_circuit() -> Circuit:
    circuit = Circuit("NMOS common-source amplifier")
    circuit.model(
        "NMOS_LEVEL1",
        "NMOS",
        LEVEL=1,
        VTO=VTH,
        KP=KP,
        LAMBDA=LAMBDA,
    )
    circuit.V("supply", "vdd", circuit.gnd, VDD)
    circuit.V(
        "input",
        "input",
        circuit.gnd,
        "DC 0 AC 1 SIN(0 10m 1k)",
    )
    circuit.R("gate_upper", "vdd", "gate", RG1_OHM)
    circuit.R("gate_lower", "gate", circuit.gnd, RG2_OHM)
    circuit.R("drain", "vdd", "drain", RD_OHM)
    circuit.C("coupling", "input", "gate", 1 @ u_uF)
    circuit.MOSFET(
        "M1",
        "drain",
        "gate",
        circuit.gnd,
        circuit.gnd,
        model="NMOS_LEVEL1",
        w=100 @ u_um,
        l=100 @ u_um,
    )
    return circuit


def write_csv(path: Path, headers: list[str], rows: list[list[float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    theoretical_vg, theoretical_id, theoretical_vds, theoretical_gm, vov = (
        solve_theoretical_operating_point()
    )
    theoretical_ro = 1.0 / (LAMBDA * theoretical_id)
    theoretical_rout = RD_OHM * theoretical_ro / (RD_OHM + theoretical_ro)
    theoretical_av = -theoretical_gm * theoretical_rout

    circuit = build_circuit()
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)

    operating_point = simulator.operating_point()
    simulated_vg = scalar(operating_point["gate"])
    simulated_vd = scalar(operating_point["drain"])
    simulated_id = (VDD - simulated_vd) / RD_OHM
    simulated_vds = simulated_vd
    simulated_gm = 2.0 * simulated_id / (simulated_vg - VTH)
    simulated_ro = 1.0 / (LAMBDA * simulated_id)
    simulated_rout = RD_OHM * simulated_ro / (RD_OHM + simulated_ro)

    write_csv(
        RESULTS / "nmos_operating_point.csv",
        ["quantity", "theoretical", "simulated", "unit"],
        [
            ["VGS", theoretical_vg, simulated_vg, "V"],
            ["ID", theoretical_id, simulated_id, "A"],
            ["VDS", theoretical_vds, simulated_vds, "V"],
            ["gm", theoretical_gm, simulated_gm, "S"],
            ["ro", theoretical_ro, simulated_ro, "ohm"],
            ["Rout", theoretical_rout, simulated_rout, "ohm"],
            [
                "saturation_margin",
                theoretical_vds - vov,
                simulated_vds - (simulated_vg - VTH),
                "V",
            ],
        ],
    )

    transient = simulator.transient(step_time=2 @ u_us, end_time=10 @ u_ms)
    time_ms = as_ndarray(transient.time) * 1e3
    input_v = as_ndarray(transient["input"])
    gate_v = as_ndarray(transient["gate"])
    output_v = as_ndarray(transient["drain"])

    start_index = int(np.searchsorted(time_ms, 8.0))
    transient_rows = [
        [float(t), float(vin), float(vg), float(vout)]
        for t, vin, vg, vout in zip(
            time_ms[start_index:],
            input_v[start_index:],
            gate_v[start_index:],
            output_v[start_index:],
        )
    ]
    write_csv(
        RESULTS / "nmos_transient.csv",
        ["time_ms", "input_v", "gate_v", "output_v"],
        transient_rows,
    )

    centered_time = time_ms[start_index:] - time_ms[start_index]
    plt.figure(figsize=(9, 4.8))
    plt.plot(
        centered_time,
        input_v[start_index:] * 1e3,
        label="Input (mV)",
        color="#d7643c",
        linewidth=1.8,
    )
    plt.plot(
        centered_time,
        output_v[start_index:] * 1e3,
        label="Output (mV)",
        color="#08736c",
        linewidth=2.0,
    )
    plt.xlabel("Time after 8 ms (ms)")
    plt.ylabel("Voltage (mV)")
    plt.title("NMOS Common-Source Amplifier: Inverting Output")
    plt.grid(alpha=0.22)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "generated_nmos_transient.png", dpi=180)
    plt.close()

    ac = simulator.ac(
        start_frequency=10 @ u_Hz,
        stop_frequency=10 @ u_MHz,
        number_of_points=150,
        variation="dec",
    )
    frequency_hz = as_ndarray(ac.frequency)
    gain_complex = as_ndarray(ac["drain"]) / as_ndarray(ac["input"])
    gain_magnitude = np.abs(gain_complex)
    gain_db = 20.0 * np.log10(np.maximum(gain_magnitude, 1e-15))
    phase_deg = np.angle(gain_complex, deg=True)

    write_csv(
        RESULTS / "nmos_ac.csv",
        ["frequency_hz", "gain_magnitude", "gain_db", "phase_deg"],
        [
            [float(f), float(gain), float(gain_db_value), float(phase)]
            for f, gain, gain_db_value, phase in zip(
                frequency_hz,
                gain_magnitude,
                gain_db,
                phase_deg,
            )
        ],
    )

    index_1khz = int(np.argmin(np.abs(frequency_hz - INPUT_FREQUENCY_HZ)))
    simulated_av_abs = float(gain_magnitude[index_1khz])
    simulated_phase = float(phase_deg[index_1khz])

    write_csv(
        RESULTS / "nmos_summary.csv",
        ["quantity", "theoretical", "simulated", "unit"],
        [
            ["Av_magnitude", abs(theoretical_av), simulated_av_abs, "V/V"],
            ["Av_db", 20.0 * math.log10(abs(theoretical_av)), 20.0 * math.log10(simulated_av_abs), "dB"],
            ["phase_at_1kHz", -180.0 if theoretical_av < 0 else 0.0, simulated_phase, "deg"],
            [
                "output_amplitude",
                abs(theoretical_av) * INPUT_AMPLITUDE_V,
                simulated_av_abs * INPUT_AMPLITUDE_V,
                "V",
            ],
        ],
    )

    saturation = simulated_vds > (simulated_vg - VTH)
    print(f"VGS = {simulated_vg:.6f} V")
    print(f"ID = {simulated_id * 1e3:.6f} mA")
    print(f"VDS = {simulated_vds:.6f} V")
    print(f"Saturation: {saturation}")
    print(f"gm = {simulated_gm * 1e3:.6f} mS")
    print(f"Av = {-simulated_av_abs:.6f} at 1 kHz ({simulated_phase:.2f} deg)")


if __name__ == "__main__":
    main()

