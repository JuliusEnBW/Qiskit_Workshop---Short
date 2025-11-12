# Interactive Bloch Sphere Widget
# Optimized version with degree input for Rx, Ry, Rz with automatic conversion to radians

from ipywidgets import FloatSlider, IntSlider, ToggleButtons, Button, HBox, VBox, Output
from qiskit.visualization import plot_bloch_vector, plot_histogram
from qiskit import QuantumCircuit
from qiskit_aer import Aer
import numpy as np
import math

def create_interactive_bloch_sphere():
    """Creates and returns the interactive Bloch sphere widget."""
    
    # Simulators
    backend_state = Aer.get_backend('statevector_simulator')
    backend_qasm = Aer.get_backend('qasm_simulator')

    # Analytical Bloch vector calculation for |0> --Rx--> --Ry--> --Rz-->
    # Starting state |0>: Bloch (0,0,1)
    def bloch_after_rotations(rx_rad, ry_rad, rz_rad):
        x, y, z = 0.0, 0.0, 1.0
        if abs(rx_rad) > 1e-12:
            y, z = y*math.cos(rx_rad) - z*math.sin(rx_rad), y*math.sin(rx_rad) + z*math.cos(rx_rad)
        if abs(ry_rad) > 1e-12:
            x, z = x*math.cos(ry_rad) + z*math.sin(ry_rad), -x*math.sin(ry_rad) + z*math.cos(ry_rad)
        if abs(rz_rad) > 1e-12:
            x, y = x*math.cos(rz_rad) - y*math.sin(rz_rad), x*math.sin(rz_rad) + y*math.cos(rz_rad)
        return [x, y, z]

    # Widgets (now in degrees - more understandable for beginners)
    # Range 0° .. 360° (full rotation). Step 1° for fine control.
    slider_rx = FloatSlider(min=0, max=360, step=1, value=0, description='X (°)')
    slider_ry = FloatSlider(min=0, max=360, step=1, value=0, description='Y (°)')
    slider_rz = FloatSlider(min=0, max=360, step=1, value=0, description='Z (°)')
    slider_shots = IntSlider(min=50, max=2000, step=50, value=500, description='Messungen')
    mode = ToggleButtons(options=['Schnell','Simulator'], description='Modus')
    btn_update = Button(description='Aktualisieren', button_style='primary', tooltip='Manuell neu rendern')
    output = Output()

    help_text = Output()
    with help_text:
        print("Erklärung der Regler (Grad):")
        print("- X (°): Rotation um X-Achse. Bewegt Zustand vom Nordpol zum Südpol (ändert Mess-Wahrsch.).")
        print("- Y (°): Rotation um Y-Achse. Ebenfalls Änderung der 0/1-Wahrscheinlichkeiten.")
        print("- Z (°): Rotation um Z-Achse. Ändert NUR die Phase (sichtbar nach Basiswechsel, z.B. via H).")
        print("- Messungen: Anzahl der Wiederholungen zur statistischen Approximation.")
        print("- Modus 'Schnell': Formeln ohne echten Simulator. 'Simulator': echter Statevector + Messung.")
        print("Hinweis: 180° ≙ π Radiant, 360° ≙ 2π Radiant.")

    rendering = False

    # Bloch sphere + histogram side by side
    from matplotlib.ticker import PercentFormatter as _PF

    def _display_bloch_and_hist(bloch_vec, prob_dict, bloch_title, hist_title):
        import matplotlib.pyplot as _plt
        
        # Close all previous plots to avoid memory leak
        _plt.close('all')
        
        fig = _plt.figure(figsize=(8,4))
        ax_b = fig.add_subplot(1,2,1, projection='3d')
        ax_h = fig.add_subplot(1,2,2)
        plot_bloch_vector(bloch_vec, title=bloch_title, ax=ax_b)
        p0 = prob_dict.get('0', 0.0)
        p1 = prob_dict.get('1', 0.0)
        bars = ax_h.bar(['0','1'], [p0,p1], color=['#1f77b4','#ff7f0e'])
        ax_h.set_title(hist_title)
        ax_h.set_ylim(0,1.0)
        ax_h.set_ylabel('Prozent')
        ax_h.yaxis.set_major_formatter(_PF(xmax=1, decimals=0))
        for rect,val in zip(bars,[p0,p1]):
            ax_h.text(rect.get_x()+rect.get_width()/2, val+0.02, f"{val*100:.0f}%", ha='center', va='bottom', fontsize=9)
        try:
            fig.tight_layout()
        except Exception:
            pass
        from IPython.display import display as _display
        _display(fig)
        
        # Close figure after display to avoid further accumulation
        _plt.close(fig)

    def render():
        nonlocal rendering
        if rendering:  # simple reentrancy guard
            return
        rendering = True
        with output:
            output.clear_output(wait=True)
            # Read values in degrees
            rx_deg, ry_deg, rz_deg, shots = slider_rx.value, slider_ry.value, slider_rz.value, slider_shots.value
            # Convert to radians for calculation / Qiskit gates
            rx = math.radians(rx_deg)
            ry = math.radians(ry_deg)
            rz = math.radians(rz_deg)
            if mode.value == 'Schnell':
                bloch = bloch_after_rotations(rx, ry, rz)
                z = bloch[2]
                p0 = (1+z)/2
                p1 = 1-p0
                # Probabilities directly (not first counts → then normalize)
                probs = {'0': p0, '1': p1}
                print(f"Analytisch | Rx={rx_deg:.0f}° Ry={ry_deg:.0f}° Rz={rz_deg:.0f}° -> p(0)≈{p0:.3f} p(1)≈{p1:.3f}")
                qc = QuantumCircuit(1,1)
                if rx: qc.rx(rx,0)
                if ry: qc.ry(ry,0)
                if rz: qc.rz(rz,0)
                try:
                    # Close previous plots
                    import matplotlib.pyplot as plt
                    plt.close('all')
                    from IPython.display import display
                    display(qc.draw('mpl'))
                except Exception:
                    print(qc.draw())
                _display_bloch_and_hist(bloch, probs, 'Bloch-Sphäre (analytisch)', 'Messung (approximiert, %)')
            else:
                qc = QuantumCircuit(1,1)
                if rx: qc.rx(rx,0)
                if ry: qc.ry(ry,0)
                if rz: qc.rz(rz,0)
                sv = backend_state.run(qc).result().get_statevector(qc)
                a, b = sv[0], sv[1]
                x = 2 * np.real(np.conjugate(a) * b)
                y = 2 * np.imag(np.conjugate(a) * b)
                z = np.abs(a)**2 - np.abs(b)**2
                bloch = [x,y,z]
                qc_m = qc.copy(); qc_m.measure(0,0)
                counts = backend_qasm.run(qc_m, shots=shots).result().get_counts(qc_m)
                # Normalize to probabilities
                total = sum(counts.values()) or 1
                probs = {k: v/total for k,v in counts.items()}
                print(f"Simulator | Rx={rx_deg:.0f}° Ry={ry_deg:.0f}° Rz={rz_deg:.0f}° -> Prozent: " + 
                      ", ".join(f"{b}={(p*100):.1f}%" for b,p in sorted(probs.items())))
                try:
                    # Close previous plots
                    import matplotlib.pyplot as plt
                    plt.close('all')
                    from IPython.display import display
                    display(qc.draw('mpl'))
                except Exception:
                    print(qc.draw())
                _display_bloch_and_hist(bloch, probs, 'Bloch-Sphäre (Simulator)', 'Messung (Simulator, %)')
        rendering = False

    # Auto-update on slider changes
    for w in (slider_rx, slider_ry, slider_rz, slider_shots, mode):
        w.observe(lambda change: render() if change['name']=='value' else None, names='value')
    btn_update.on_click(lambda _: render())

    controls = VBox([
        help_text,
        HBox([slider_rx, slider_ry, slider_rz]),
        HBox([slider_shots, mode, btn_update])
    ])

    # Create the complete widget
    widget = VBox([controls, output])
    
    # Initial render
    render()
    
    return widget
