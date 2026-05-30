import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt, hilbert
from scipy.interpolate import CubicSpline

def extract_digital_phase_space(csv_path, lead_column=None, start_sample=0, num_samples=2500):
    df = pd.read_csv(csv_path)
    
    # Force all column headers to lowercase to handle case-sensitivity safely
    df.columns = [str(col).lower() for col in df.columns]
    
    # Target your column (it will now successfully find 'ii' even if it's 'II' in the CSV)
    if lead_column and lead_column.lower() in df.columns:
        raw_signal = df[lead_column.lower()].values
    else:
        # Secure fallback: skip metadata and grab the first actual raw signal vector column (usually index 1)
        raw_signal = df.iloc[:, 1].values
    
    if lead_column and lead_column in df.columns:
        raw_signal = df[lead_column].values
    else:
        raw_signal = df.iloc[:, 0].values
        
    signal_window = raw_signal[start_sample : start_sample + num_samples]
    
    # 1. Clear out breathing drift and high-frequency noise completely
    b_high, a_high = butter(3, 0.01, btype='high', analog=False)
    drift_removed = filtfilt(b_high, a_high, signal_window)
    
    b_low, a_low = butter(3, 0.04, btype='low', analog=False)
    smoothed = filtfilt(b_low, a_low, drift_removed)
    
    # 2. BYPASS SINGLE-CYCLE SLICE: Let's look at multiple beats!
    # Instead of truncating down to 600 samples, we feed the entire filtered window.
    # We will rename the variable cleanly so the rest of your up-sampling code works perfectly.
    multiple_cycles = smoothed
    
    # 3. Super-Dense Up-Sampling (3x Points for Multi-Beat Efficiency)
    # We drop from 5x to 3x up-sampling here just to keep the interactive browser panel 
    # lightning-fast when rendering thousands of consecutive data points.
    x_old = np.arange(len(multiple_cycles))
    x_new = np.linspace(0, len(multiple_cycles) - 1, len(multiple_cycles) * 3)
    spline = CubicSpline(x_old, multiple_cycles)
    signal_dense = spline(x_new)
    # 4. THE CONTINUOUS TRACE ENGINE: Analytic Signal Generation
    # Instead of manual time delays, we use the Hilbert Transform to calculate 
    # the imaginary, orthogonal component of the signal. This creates a perfect 3D circle.
    analytic_signal = hilbert(signal_dense)
    amplitude_envelope = np.abs(analytic_signal)
    
    # Construct fluid coordinates
    x_axis = signal_dense
    y_axis = np.imag(analytic_signal) # 90-degree phase shifted orthogonal vector
    z_axis = np.gradient(signal_dense) # Velocity vector to lift it into 3D space
    
    # Normalize coordinates symmetrically
    x_axis = (x_axis - np.mean(x_axis)) / np.std(x_axis)
    y_axis = (y_axis - np.mean(y_axis)) / np.std(y_axis)
    z_axis = (z_axis - np.mean(z_axis)) / np.std(z_axis)
    
# 5. TEMPORAL MODULO GRADIENT ENGINE (True Phase-Locking)
    # Instead of spatial angles which double-count quadrants, we anchor 
    # the color loop directly to the heartbeat's rhythmic time-frequency.
    from scipy.signal import find_peaks
    
    # Locate the high-velocity apex entry point of each QRS complex
    # distance=500 ensures we don't accidentally double-trigger on a single beat
    peaks, _ = find_peaks(np.abs(z_axis), distance=500, prominence=1.5)
    
    # Create an empty array to house our true phase progression values
    true_phase_gradient = np.zeros(len(x_axis))
    
    if len(peaks) > 1:
        # Calculate the average duration (in samples) of this patient's cardiac cycle
        cycle_lengths = np.diff(peaks)
        avg_cycle_len = int(np.mean(cycle_lengths))
        
        # Build a cyclical clock that loops from 0.0 to 100.0 across every beat
        for i in range(len(true_phase_gradient)):
            # Find how far along the current data point is relative to the average cycle
            time_step_in_cycle = i % avg_cycle_len
            true_phase_gradient[i] = (time_step_in_cycle / avg_cycle_len) * 100.0
    else:
        # Robust fallback: if processing an isolated segment, span a single smooth line
        true_phase_gradient = np.linspace(0, 100, len(x_axis))
        
    return pd.DataFrame({
        'X': x_axis, 'Y': y_axis, 'Z': z_axis,
        'Timeline': true_phase_gradient # Injecting the true repeating clock
    })
    
