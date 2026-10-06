"""RC low-pass filter: transient square-wave response and AC Bode plot."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import u_Hz, u_kOhm, u_MHz, u_ms, u_nF, u_us, u_V


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

R_OHM = 1.6e3
C_FARAD = 100e-9


def as_ndarray(values) -> np.ndarray:
    """Convert PySpice unit-aware arrays to plain float arrays."""
    if hasattr(values, "as_ndarray"):
        values = values.as_ndarray()
    return np.asarray(values, dtype=float)


def build_circuit() -> Circuit:
    circuit = Circuit("RC low-pass filter")
    # DC and AC values are used by operating/AC analyses; PULSE drives transient.
    circuit.V(
        "input",
        "in",
        circuit.gnd,
        "DC 0 AC 1 PULSE(0 1 0 1u 1u 0.5m 1m)",
    )
    circuit.R(1, "in", "out", 1.6 @ u_kOhm)
    circuit.C(1, "out", circuit.gnd, 100 @ u_nF)
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

    circuit = build_circuit()
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)

    transient = simulator.transient(step_time=1 @ u_us, end_time=3 @ u_ms)
    time_ms = as_ndarray(transient.time) * 1e3
    input_v = as_ndarray(transient["in"])
    output_v = as_ndarray(transient["out"])

    transient_rows = [
        [float(t), float(vin), float(vout)]
        for t, vin, vout in zip(time_ms, input_v, output_v)
    ]
    write_csv(
        RESULTS / "rc_transient.csv",
        ["time_ms", "input_v", "output_v"],
        transient_rows,
    )

    plt.figure(figsize=(9, 4.8))
    plt.plot(time_ms, input_v, label="Input square wave", color="#d7643c", linewidth=1.8)
    plt.plot(time_ms, output_v, label="Output", color="#08736c", linewidth=2.1)
    plt.xlabel("Time (ms)")
    plt.ylabel("Voltage (V)")
    plt.title("RC Low-Pass Transient Response")
    plt.grid(alpha=0.22)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "generated_rc_transient.png", dpi=180)
    plt.close()

    ac = simulator.ac(
        start_frequency=10 @ u_Hz,
        stop_frequency=1 @ u_MHz,
        number_of_points=200,
        variation="dec",
    )
    frequency_hz = as_ndarray(ac.frequency)
    output_complex = as_ndarray(ac["out"])
    gain_db = 20.0 * np.log10(np.maximum(np.abs(output_complex), 1e-15))
    phase_deg = np.angle(output_complex, deg=True)

    bode_rows = [
        [float(f), float(gain), float(phase)]
        for f, gain, phase in zip(frequency_hz, gain_db, phase_deg)
    ]
    write_csv(
        RESULTS / "rc_bode.csv",
        ["frequency_hz", "gain_db", "phase_deg"],
        bode_rows,
    )

    figure, (magnitude_axis, phase_axis) = plt.subplots(
        2,
        1,
        figsize=(9, 6.3),
        sharex=True,
    )
    magnitude_axis.semilogx(frequency_hz, gain_db, color="#08736c", linewidth=2)
    magnitude_axis.axhline(-3.0103, color="#d7643c", linestyle="--", linewidth=1.2)
    magnitude_axis.set_ylabel("Gain (dB)")
    magnitude_axis.set_title("RC Low-Pass Bode Plot")
    magnitude_axis.grid(which="both", alpha=0.2)

    phase_axis.semilogx(frequency_hz, phase_deg, color="#d7643c", linewidth=2)
    phase_axis.axvline(994.718, color="#08736c", linestyle="--", linewidth=1.2)
    phase_axis.set_xlabel("Frequency (Hz)")
    phase_axis.set_ylabel("Phase (deg)")
    phase_axis.grid(which="both", alpha=0.2)
    figure.tight_layout()
    figure.savefig(FIGURES / "generated_rc_bode.png", dpi=180)
    plt.close(figure)

    index_1khz = int(np.argmin(np.abs(frequency_hz - 1e3)))
    measured_gain_db = float(gain_db[index_1khz])
    measured_phase_deg = float(phase_deg[index_1khz])
    theoretical_fc = 1.0 / (2.0 * math.pi * R_OHM * C_FARAD)
    theoretical_gain = 1.0 / math.sqrt(1.0 + (1e3 / theoretical_fc) ** 2)
    theoretical_gain_db = 20.0 * math.log10(theoretical_gain)
    theoretical_phase_deg = -math.degrees(math.atan(1e3 / theoretical_fc))

    write_csv(
        RESULTS / "rc_summary.csv",
        ["quantity", "theoretical", "simulated", "unit"],
        [
            ["cutoff_frequency", theoretical_fc, theoretical_fc, "Hz"],
            ["gain_at_1kHz", theoretical_gain_db, measured_gain_db, "dB"],
            ["phase_at_1kHz", theoretical_phase_deg, measured_phase_deg, "deg"],
        ],
    )

    print(f"Theoretical fc: {theoretical_fc:.3f} Hz")
    print(f"1 kHz gain: {measured_gain_db:.3f} dB")
    print(f"1 kHz phase: {measured_phase_deg:.3f} deg")


if __name__ == "__main__":
    main()

