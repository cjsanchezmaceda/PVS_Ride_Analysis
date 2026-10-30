import numpy as np
from scipy.signal import freqs, welch, tf2zpk, bilinear_zpk, zpk2sos, sosfilt

def wk_coefficients():
    """Analog transfer function of the ISO 2631-1 Wk weighting (vertical, seated).

    Returns numerator b and denominator a, as polynomial coefficients in s
    (highest power first).
    """
    w = lambda f: 2 * np.pi * f
    w1, w2, w3, w4, w5, w6 = map( w, [0.4,  100, 12.5, 12.5, 2.37, 3.35])
    Q4, Q5, Q6 = 0.63, 0.91, 0.91

    #band limit: high and low pass filter
    b_l, a_l = [w2**2], [1, np.sqrt(2)*w2, w2**2]
    b_h, a_h = [1, 0, 0], [1, np.sqrt(2)*w1, w1**2]

    #acceleration - velocity transition
    b_t, a_t = [1/w3, 1], [1/w4**2, 1/(w4*Q4), 1]

    #upward step
    b_s = np.array([1/w5**2, 1/(w5*Q5), 1])*(w5/w6)**2
    a_s = [1/w6**2, 1/(w6*Q6), 1]

    b = np.polymul(np.polymul(b_l, b_h), np.polymul(b_t, b_s))
    a = np.polymul(np.polymul(a_l, a_h), np.polymul(a_t, a_s))

    return b, a

def wk_gain(f):
    """Magnitude of the Wk weighting at frequencies f (Hz)."""
    b, a = wk_coefficients()
    _, h = freqs(b, a, worN=2 * np.pi * np.asarray(f))
    return np.abs(h)

def weighted_rms(x, fs=100, nperseg=500):
    """ISO 2631-1 frequency-weighted RMS acceleration (Wk) of a signal, from its PSD."""
    f, P = welch(x, fs=fs, nperseg=nperseg)
    return np.sqrt(np.trapezoid(wk_gain(f)**2*P, f))

def wk_sos(fs=100):
    """Digital (bilinear) version of the Wk weighting, as second-order sections."""
    b, a = wk_coefficients()
    z, p, k = tf2zpk(b, a)
    zd, pd_, kd = bilinear_zpk(z, p, k, fs)
    return zpk2sos(zd, pd_, kd)

def apply_wk(x, fs=100):
    """Apply the Wk weighting to an acceleration signal in the time domain."""
    return sosfilt(wk_sos(fs), x)

def crest_factor(aw):
    """Crest factor of a frequency-weighted signal: peak / RMS."""
    return np.max(np.abs(aw))/np.sqrt(np.mean(aw**2))

def vdv(aw, fs=100):
    """Vibration dose value of a frequency-weighted signal (m/s^1.75)."""
    return np.trapezoid(aw**4, dx=1/fs)**0.25