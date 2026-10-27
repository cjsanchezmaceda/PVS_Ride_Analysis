import numpy as np
from scipy.signal import welch, csd

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

def mean_cross_spectral(signals, windows_ids, col_in, col_out, fs=100, nperseg=500):
    """Average auto- and cross-spectra of an input/output pair over a set of windows.
    Returns f, Pxx (input PSD), Pyy (output PSD) and Pxy (cross-spectrum).
    """
    Pxx_list, Pyy_list, Pxy_list = [], [], []
    for w in windows_ids:
        seg = signals[signals['window'] == w]
        x = seg[col_in].to_numpy()
        y = seg[col_out].to_numpy()
        f, Pxx = welch(x, fs = fs, nperseg = nperseg)
        _, Pyy = welch(y, fs = fs, nperseg = nperseg)
        _, Pxy = csd(x, y, fs = fs, nperseg = nperseg)
        Pxx_list.append(Pxx)
        Pyy_list.append(Pyy)
        Pxy_list.append(Pxy)
    return f, np.mean(Pxx_list, axis = 0), np.mean(Pyy_list, axis = 0), np.mean(Pxy_list, axis = 0)

def half_power_damping(f, mag, f_min, f_max):
    """Estimate natural frequency, peak magnitude and damping ratio of a resonance
    with the half-power bandwidth method.

    f, mag: frequency vector and |T| (magnitude of the transfer function)
    f_min, f_max: band in which to look for the peak
    Returns fn, peak, zeta, f1, f2 (f1, f2: half-power frequencies; NaN if not found)
    """
    band_idx = np.where((f >= f_min) & (f <= f_max))[0]
    i_peak = band_idx[np.argmax(mag[band_idx])]
    fn, peak = f[i_peak], mag[i_peak]
    level = peak / np.sqrt(2)

    # walk left from the peak until the curve drops below the half-power level
    i = i_peak
    while i > 0 and mag[i] > level:
        i -= 1
    f1 = np.interp(level, [mag[i], mag[i + 1]], [f[i], f[i + 1]]) if mag[i] <= level else np.nan

    # walk right from the peak
    j = i_peak
    while j < len(f) - 1 and mag[j] > level:
        j += 1
    f2 = np.interp(level, [mag[j], mag[j - 1]], [f[j], f[j - 1]]) if mag[j] <= level else np.nan

    zeta = (f2 - f1) / (2 * fn)
    return fn, peak, zeta, f1, f2