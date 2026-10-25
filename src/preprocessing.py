def flag_frozen(signal, min_run=10):
    is_zero = signal.diff() == 0
    run_id = (is_zero != is_zero.shift()).cumsum()
    run_length = is_zero.groupby(run_id).transform('size')
    return  is_zero & (run_length >= 10)

from scipy.signal import butter, sosfiltfilt

def bandpass(signal, f_low, f_high, fs, order=4):
    sos = butter(order, [f_low, f_high], btype='band', fs=fs, output='sos')
    centred = signal - signal.mean()
    return sosfiltfilt(sos, centred)

import numpy as np

def make_windows(df, window_size=500, min_speed=10/3.6, max_speed_std=1.0):
    df = df.copy()    
    df['surface_run'] = (df['surface'] != df['surface'].shift()).cumsum()
    df['window_in_run'] = df.groupby('surface_run').cumcount() // window_size
    df['window'] = df.groupby(['surface_run', 'window_in_run']).ngroup()
    windows = df.groupby('window').agg(
        t_start = ('t','min'),
        n_rows = ('t','size'),
        n_surfaces = ('surface', 'nunique'),
        surface = ('surface', 'first'),
        speed_mean = ('speed', 'mean'),
        speed_std = ('speed', 'std'),
        has_invalid = ('invalid', 'any'),
    )

    windows['valid'] = (
        (windows['n_rows'] == window_size) 
        & (windows['n_surfaces'] == 1)
        & (windows['speed_mean'] > min_speed)
        & (windows['speed_std'] < max_speed_std)
        & (~windows['has_invalid'])
    )
    return df, windows