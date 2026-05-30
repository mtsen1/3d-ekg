import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt, hilbert
from scipy.interpolate import CubicSpline

def extract_digital_phase_space(csv_path, lead_column=None, start_sample=0, num_samples=2200):
    df = pd.read_csv(csv_path)
    df.columns = [str(col).lower() for col in df.columns]
    
    if lead_column and lead_column.lower() in df.columns:
        raw_signal = df[lead_column.lower()].values
    else:
        raw_signal = df.iloc[:, 1].values
        
    signal_window = raw_signal[start_sample : start_sample + num_samples]
    
    # Dual-stage filtration system
    b_high, a_high = butter(3, 0.01, btype='high', analog=False)
    drift_removed = filtfilt(b_high, a_high, signal_window)
    
    b_low, a_low = butter(3, 0.04, btype='low', analog=False)
    smoothed = filtfilt(b_low, a_low, drift_removed)
    
    # 3x Super-Sampling Cubic Spline
    x_old = np.arange(len(smoothed))
    x_new = np.linspace(0, len(smoothed) - 1, len(smoothed) * 3)
    spline = CubicSpline(x_old, smoothed)
    signal_dense = spline(x_new)
    
    # Hilbert Transform State Space Construction
    analytic_signal = hilbert(signal_dense)
    x_axis = (signal_dense - np.mean(signal_dense)) / np.std(signal_dense)
    y_axis = np.imag(analytic_signal)
    y_axis = (y_axis - np.mean(y_axis)) / np.std(y_axis)
    z_axis = np.gradient(signal_dense)
    z_axis = (z_axis - np.mean(z_axis)) / np.std(z_axis)
    
    # Temporal Modulo Clock
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(np.abs(z_axis), distance=500, prominence=1.5)
    true_phase_gradient = np.zeros(len(x_axis))
    
    if len(peaks) > 1:
        cycle_lengths = np.diff(peaks)
        avg_cycle_len = int(np.mean(cycle_lengths))
        for i in range(len(true_phase_gradient)):
            true_phase_gradient[i] = ((i % avg_cycle_len) / avg_cycle_len) * 100.0
    else:
        true_phase_gradient = np.linspace(0, 100, len(x_axis))
        
    return pd.DataFrame({
        'Raw_Signal': signal_dense, # Kept for the 2D slider waveform path
        'X': x_axis, 'Y': y_axis, 'Z': z_axis,
        'Timeline': true_phase_gradient
    })