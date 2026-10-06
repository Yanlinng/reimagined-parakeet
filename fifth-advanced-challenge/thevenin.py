"""Verify Thevenin equivalence from open-circuit, short-circuit and load tests."""

from __future__ import annotations

import csv
from pathlib import Path

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import u_Ohm, u_V, u_kOhm


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

VS_VOLT = 12.0
R1_OHM = 2_000.0
R2_OHM = 4_000.0
RL_OHM = 2_000.0
SHORT_RESISTANCE_OHM = 0.001


def scalar(value) -> float:
    if hasattr(value, "as_ndarray"):
        return float(value.as_ndarray().reshape(-1)[0])
    return float(value)


def solve_source_circuit(
    *,
    load_ohm: float | None = None,
    short_circuit: bool = False,
) -> tuple[float, float]:
    circuit = Circuit("Thevenin source network")
    circuit.V("source", "source", circuit.gnd, VS_VOLT @ u_V)
    circuit.R("series", "source", "out", R1_OHM @ u_Ohm)
    circuit.R("shunt", "out", circuit.gnd, R2_OHM @ u_Ohm)

    if short_circuit:
        circuit.R("short", "out", circuit.gnd, SHORT_RESISTANCE_OHM @ u_Ohm)

    if load_ohm is not None:
        circuit.R("load", "out", circuit.gnd, load_ohm @ u_Ohm)

    analysis = circuit.simulator(temperature=25, nominal_temperature=25).operating_point()
    voltage = scalar(analysis["out"])
    resistance = (
        SHORT_RESISTANCE_OHM
        if short_circuit
        else (load_ohm if load_ohm is not None else float("inf"))
    )
    current = voltage / resistance if resistance != float("inf") else 0.0
    return voltage, current


def solve_equivalent_circuit(vth: float, rth: float, load_ohm: float) -> tuple[float, float]:
    circuit = Circuit("Thevenin equivalent network")
    circuit.V("equivalent", "equivalent_source", circuit.gnd, vth @ u_V)
    circuit.R("equivalent_resistance", "equivalent_source", "out", rth @ u_Ohm)
    circuit.R("load", "out", circuit.gnd, load_ohm @ u_Ohm)
    analysis = circuit.simulator(temperature=25, nominal_temperature=25).operating_point()
    voltage = scalar(analysis["out"])
    return voltage, voltage / load_ohm


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)

    theoretical_voc = VS_VOLT * R2_OHM / (R1_OHM + R2_OHM)
    theoretical_isc = VS_VOLT / R1_OHM
    theoretical_rth = (R1_OHM * R2_OHM) / (R1_OHM + R2_OHM)
    theoretical_load_v = theoretical_voc * RL_OHM / (theoretical_rth + RL_OHM)
    theoretical_load_i = theoretical_load_v / RL_OHM

    voc, _ = solve_source_circuit()
    _, isc = solve_source_circuit(short_circuit=True)
    original_load_v, original_load_i = solve_source_circuit(load_ohm=RL_OHM)
    equivalent_load_v, equivalent_load_i = solve_equivalent_circuit(
        theoretical_voc,
        theoretical_rth,
        RL_OHM,
    )

    rows = [
        {
            "scenario": "open_circuit",
            "quantity": "Voc",
            "theoretical": theoretical_voc,
            "simulated": voc,
            "unit": "V",
        },
        {
            "scenario": "short_circuit",
            "quantity": "Isc",
            "theoretical": theoretical_isc,
            "simulated": isc,
            "unit": "A",
        },
        {
            "scenario": "original_with_load",
            "quantity": "VL",
            "theoretical": theoretical_load_v,
            "simulated": original_load_v,
            "unit": "V",
        },
        {
            "scenario": "original_with_load",
            "quantity": "IL",
            "theoretical": theoretical_load_i,
            "simulated": original_load_i,
            "unit": "A",
        },
        {
            "scenario": "equivalent_with_load",
            "quantity": "VL",
            "theoretical": theoretical_load_v,
            "simulated": equivalent_load_v,
            "unit": "V",
        },
        {
            "scenario": "equivalent_with_load",
            "quantity": "IL",
            "theoretical": theoretical_load_i,
            "simulated": equivalent_load_i,
            "unit": "A",
        },
    ]

    with (RESULTS / "thevenin_results.csv").open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["scenario", "quantity", "theoretical", "simulated", "unit"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Theoretical Voc: {theoretical_voc:.6f} V")
    print(f"Theoretical Isc: {theoretical_isc * 1e3:.6f} mA")
    print(f"Theoretical Rth: {theoretical_rth:.6f} ohm")
    print(f"Load voltage: original={original_load_v:.6f} V, equivalent={equivalent_load_v:.6f} V")


if __name__ == "__main__":
    main()

