import numpy as np
from scipy.signal import welch

def mean_psd(signals, window_ids, colum, fs=100, nperseg=500):
    psds = []
    for w in window_ids:
        x  = signals.loc[signals['window'] == w, colum].to_numpy()
        f, Pxx = welch(x, fs=fs, nperseg=nperseg)
        psds.append(Pxx)
    return f, np.mean(psds, axis = 0)