import plotly.graph_objects as go
import os
import sys

# Ensure parent directory is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.archival_topology import extract_archival_phase_space

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Target your digitized archival csv file path
    # CHANGE THIS LINE to point to your extracted numerical data file
    # (Update 'processed_strip.csv' to whatever your actual extracted file is named)
    csv_target_path = os.path.join(script_dir, "..", "data", "archival_ecg", "processed_strip.csv")
    try:
        print("Ingesting digitized archival paper stream...")
        embedded_topology = extract_archival_phase_space(
            csv_path=csv_target_path,
            start_sample=0,
            num_samples=2000
        )
        
        print("Constructing Remastered Archival Phase Space Canvas...")
        
        # Build the single continuous 3D line trace matching the modern style exactly
        fig = go.Figure(data=go.Scatter3d(
            x=embedded_topology['X'],
            y=embedded_topology['Y'],
            z=embedded_topology['Z'],
            mode='lines',
            line=dict(
                color=embedded_topology['Timeline'], # Phase-locked temporal clock
                colorscale='Turbo',                 # Matching fluid rainbow spectrum
                width=5.5                           # Identical ribbon thickness
            )
        ))
        
        fig.update_layout(
            title="Archival Health Data Science: Remastered 3D Phase Space Attractor",
            height=850,
            margin=dict(l=0, r=0, b=0, t=40),
            scene=dict(
                xaxis_title='Signal State, x(t)',
                yaxis_title='Phase Shifted Orthogonal Vector',
                zaxis_title='Signal Velocity Vector',
                xaxis=dict(gridcolor="rgba(180, 200, 230, 0.25)"),
                yaxis=dict(gridcolor="rgba(180, 200, 230, 0.25)"),
                zaxis=dict(gridcolor="rgba(180, 200, 230, 0.25)")
            ),
            coloraxis=dict(
                colorscale='Turbo',
                showscale=True,
                colorbar=dict(
                    title="Cardiac Phase Vector",
                    tickvals=[15, 50, 85],
                    ticktext=["P Wave Domain", "QRS Target Zone", "T Wave Domain"]
                )
            )
        )
        
        print("Launching interactive archival visualization panel...")
        fig.show()

    except Exception as err:
        print(f"Pipeline execution halted: {err}")
        print("\n💡 Confirm that your archival filename matches and resides in the data/archival_ecg/ directory!")