"""Variant-specific helpers separated from the main workshop utilities.

Currently contains a wrapper for Variante 1 ("Immer 1" durch X-Gatter) so the
Notebook cell can stay minimal. Participants only add the X gate themselves;
this module just standardizes execution & plotting (delegates to workshop_utils).
"""
from __future__ import annotations
from qiskit import QuantumCircuit  # re-export for convenience
from typing import Tuple, Dict

from workshop_utils import run_single_qubit_demo

__all__ = ["run_variant1_demo", "run_variant2_demo", "QuantumCircuit"]


def run_variant1_demo(qc: QuantumCircuit, shots: int, backend=None) -> Tuple[Dict[str, int], Dict[str, float]]:
    """Run the Variante 1 (X -> immer 1) demo.

    The circuit should already contain measurement. Title is adapted.
    Returns counts & probabilities.
    """
    return run_single_qubit_demo(qc, shots, backend, title_prefix="Variante 1: X -> immer 1")


def run_variant2_demo(qc: QuantumCircuit, shots: int, backend=None, theta_deg: float | None = None) -> Tuple[Dict[str, int], Dict[str, float]]:
    """Run the Variante 2 (RY rotation) demo.

    Parameters
    ----------
    qc : QuantumCircuit
        User-prepared circuit including the RY gate (optional) and measurement.
    shots : int
        Number of repetitions.
    backend : optional
        Aer backend (qasm_simulator) if not provided fetched internally.
    theta_deg : float | None
        Angle shown in the title (purely informational). Not used internally; user must
        already have applied the correct rotation to the circuit.
    """
    prefix = f"Variante 2: RY({theta_deg}°)" if theta_deg is not None else "Variante 2: RY"
    return run_single_qubit_demo(qc, shots, backend, title_prefix=prefix)
