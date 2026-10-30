import numpy as np
from scipy.optimize import least_squares

def transmissibility_sdof(f, fn, zeta):
     """Complex transmissibility of a base-excited single-degree-of-freedom system."""
     s = 2j * np.pi * f
     wn = 2 * np.pi * fn
     return (2 * zeta * wn * s + wn**2)/(s**2 + 2 * zeta * wn * s + wn**2)

def fit_sdof(f, H, coh, f_min, f_max, x0=(1.5, 0.3)):
    """Fit fn and zeta to a measured transmissibility |H| within [f_min, f_max].

    Residuals are differences in log10 magnitude, weighted by the square root of the coherence.
    Returns the fitted (fn, zeta) and the full optimisation result.
    """
    band = (f >= f_min) & (f <= f_max)

    def residuals(p):
        fn, zeta = p
        model = np.abs(transmissibility_sdof(f[band], fn, zeta))
        return np.sqrt(coh[band])*(np.log10(model)-np.log10(np.abs(H[band])))

    result = least_squares(residuals, x0, bounds=([0.3, 0.01], [5.0, 2.0]))
    return result.x, result