"""Utility helpers for the Qiskit workshop demo.

Goal: Keep notebook cells minimal (only pedagogical lines) while
centralizing repetitive boilerplate like drawing, running circuits,
normalizing counts to probabilities, and producing percentage-scaled
histograms.
"""
from __future__ import annotations

from typing import Dict, Tuple, Union

from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram

try:  # Optional: matplotlib objects for type hints
    from matplotlib.axes import Axes  # type: ignore
    from matplotlib.figure import Figure  # type: ignore
except Exception:  # pragma: no cover
    class Axes:  # minimal fallbacks to satisfy type checkers
        pass
    class Figure:  # minimal fallbacks
        pass

from matplotlib.ticker import PercentFormatter

__all__ = [
    "run_single_qubit_demo",
]


def _percent_hist(probs: Dict[str, float], title: str):
    """Create a histogram scaled 0..1 with y-axis in percent.

    Returns the matplotlib object (Figure or Axes) that plot_histogram yields
    so caller can embed or further modify if needed.
    """
    fig_or_ax = plot_histogram(probs, title=title)
    if hasattr(fig_or_ax, "axes"):
        ax = fig_or_ax.axes[0]
    else:  # plot_histogram may return an Axes-like already
        ax = fig_or_ax
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Prozent")
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
    return fig_or_ax


def run_single_qubit_demo(
    qc: QuantumCircuit,
    shots: int,
    backend=None,
    title_prefix: str = "Hadamard Ergebnis",
    display_circuit: bool = True,
    return_objects: bool = False,
) -> Tuple[Dict[str, int], Dict[str, float]]:
    """Execute a (single-qubit) measurement demo circuit and plot results.

    Parameters
    ----------
    qc : QuantumCircuit
        Circuit that already contains any state preparation & a measurement.
    shots : int
        Number of repetitions for sampling.
    backend : Optional backend
        If None, uses Aer qasm_simulator.
    title_prefix : str
        Text prefix for the histogram title.
    display_circuit : bool
        If True, renders the circuit diagram.
    return_objects : bool
        If True, also returns (counts, probs, fig_or_ax) instead of just (counts, probs).

    Returns
    -------
    (counts, probs) or (counts, probs, fig_or_ax)
    """
    if backend is None:
        backend = Aer.get_backend("qasm_simulator")

    # Execute
    job = backend.run(qc, shots=shots)
    result = job.result()
    counts = result.get_counts(qc)

    # Normalize to probabilities
    probs = {k: v / shots for k, v in counts.items()}
    percent_line = " , ".join(
        f"{bit} = {p*100:.1f}%" for bit, p in sorted(probs.items(), reverse=True)
    )

    # Optionally display circuit & histogram
    try:
        from IPython.display import display as _display  # type: ignore

        if display_circuit:
            try:
                _display(qc.draw("mpl"))
            except Exception:  # fallback to text drawer
                print(qc.draw())
        fig_or_ax = _percent_hist(probs, title=f"{title_prefix} (Prozent) | {percent_line}")
        # Ensure figure shown if object was returned
        if hasattr(fig_or_ax, "axes"):
            _display(fig_or_ax)
        else:
            _display(fig_or_ax.figure)  # type: ignore[attr-defined]
    except Exception:
        # Headless or no IPython: still print textual summary
        print("Circuit (Text):")
        print(qc.draw())
        print(f"Prozent: {percent_line}")
        fig_or_ax = None  # type: ignore

    if return_objects:
        return counts, probs, fig_or_ax  # type: ignore
    return counts, probs
