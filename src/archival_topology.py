import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt, hilbert
from scipy.interpolate import CubicSpline

def extract_archival_phase_space(csv_path, start_sample=0, num_samples=2500):
    """
    Ingests digitized archival paper-scanned ECG coordinates, smooths out 
    grid-quantization noise, and maps it to a unified continuous phase-locked attractor.
    """
    df = pd.read_csv(csv_path)
    
    # Archival digitization pipelines typically output 'voltage', 'signal', or column index 1
    if 'voltage' in df.columns:
        raw_signal = df['voltage'].values
    elif 'signal' in df.columns:
        raw_signal = df['signal'].values
    else:
        raw_signal = df.iloc[:, 1].values
        
    signal_window = raw_signal[start_sample : start_sample + num_samples]
    
    # 1. SPECIALIZED ARCHIVAL SMOOTHING FILTER
    # Digitized paper scans suffer from high-frequency pixel jaggedness.
    # We apply a low-pass filter at 0.035 to iron out the paper-grain noise cleanly.
    b_high, a_high = butter(3, 0.01, btype='high', analog=False)
    drift_removed = filtfilt(b_high, a_high, signal_window)
    
    b_low, a_low = butter(3, 0.035, btype='low', analog=False)
    smoothed = filtfilt(b_low, a_low, drift_removed)
    
    # 2. UNIFIED 4x SUPER-SAMPLING CUBIC SPLINE
    # This acts as a digital remaster, turning rigid pixel steps into fluid curves.
    x_old = np.arange(len(smoothed))
    x_new = np.linspace(0, len(smoothed) - 1, len(smoothed) * 4)
    spline = CubicSpline(x_old, smoothed)
    signal_dense = spline(x_new)
    
    # 3. ANALYTIC PHASE-SPACE HILBERT TRACE ENGINE
    analytic_signal = hilbert(signal_dense)
    
    # Construct identical coordinate vectors
    x_axis = signal_dense
    y_axis = np.imag(analytic_signal)  # 90-degree phase-shifted vector
    z_axis = np.gradient(signal_dense)  # Instantaneous velocity vector
    
    # Standardize and center sytematically
    x_axis = (x_axis - np.mean(x_axis)) / np.std(x_axis)
    y_axis = (y_axis - np.mean(y_axis)) / np.std(y_axis)
    z_axis = (z_axis - np.mean(z_axis)) / np.std(z_axis)
    
    # 4. TEMPORAL MODULO GRADIENT ENGINE (Identical Phase Clock)
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(np.abs(z_axis), distance=400, prominence=1.2)
    
    true_phase_gradient = np.zeros(len(x_axis))
    
    if len(peaks) > 1:
        cycle_lengths = np.diff(peaks)
        avg_cycle_len = int(np.mean(cycle_lengths))
        
        for i in range(len(true_phase_gradient)):
            time_step_in_cycle = i % avg_cycle_len
            true_phase_gradient[i] = (time_step_in_cycle / avg_cycle_len) * 100.0
    else:
        true_phase_gradient = np.linspace(0, 100, len(x_axis))
        
    return pd.DataFrame({
        'X': x_axis, 'Y': y_axis, 'Z': z_axis,
        'Timeline': true_phase_gradient
    })