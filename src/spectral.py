import numpy as np
from scipy.signal import welch

def mean_psd(signals, window_ids, colum, fs=100, nperseg=500):
    psds = []
    for w in window_ids:
        x  = signals.loc[signals['window'] == w, colum].to_numpy()
        f, Pxx = welch(x, fs=fs, nperseg=nperseg)
        psds.append(Pxx)
    return f, np.mean(psds, axis = 0)

def peak_frequency(f, P, f_min, f_max):
    """Frequency (Hz) of the PSD maximum within [f_min, f_max]."""
    band = (f >= f_min) & (f <= f_max)
    f_band = f[band]
    P_band = P[band]
    return f_band[np.argmax(P_band)]

def band_rms(f, P, f_min, f_max):
    """RMS acceleration (m/s^2) within [f_min, f_max], from the area under the PSD."""
    band = (f >= f_min) & (f <= f_max)
    return np.sqrt(np.trapezoid(P[band], f[band]))