# src/rtgun/sync_refine.py
from __future__ import annotations
import numpy as np
from typing import Dict, Tuple

def _next_pow2(n: int) -> int:
    return 1 << (int(n - 1).bit_length())

def _parabolic_interp(y_minus: float, y0: float, y_plus: float) -> float:
    """
    Sub-sample peak refine for a discrete peak at index 0 using 3-point parabola.
    returns fractional offset in [-0.5, 0.5] (0 = at center).
    """
    denom = (y_minus - 2.0 * y0 + y_plus)
    if abs(denom) < 1e-12:
        return 0.0
    return 0.5 * (y_minus - y_plus) / denom

def gcc_phat_delay(a: np.ndarray,
                   b: np.ndarray,
                   fs: int,
                   max_lag_s: float | None = None) -> Tuple[float, float]:
    """
    Estimate delay (in samples, float) between a (reference) and b using GCC-PHAT.
    delay > 0  => b is later than a
    Returns: (delay_samples_float, peak_value)

    max_lag_s: optional limit of physically plausible lag (e.g., baseline/c). If set,
               correlation is zeroed outside ±max_lag_s before picking the peak.
    """
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)

    # zero-mean (helps with DC)
    a = a - np.mean(a)
    b = b - np.mean(b)

    N = _next_pow2(len(a) + len(b))
    A = np.fft.rfft(a, N)
    B = np.fft.rfft(b, N)
    R = A * np.conj(B)
    R /= (np.abs(R) + 1e-12)   # PHAT weighting

    r = np.fft.irfft(R, N)

    # make lags symmetric around 0 by circular shift
    r = np.concatenate([r[-(N // 2):], r[:(N // 2)]])
    lags = np.arange(-N // 2, N // 2, dtype=np.int64)

    if max_lag_s is not None:
        max_lag = int(round(max_lag_s * fs))
        mask = (lags >= -max_lag) & (lags <= max_lag)
        r = r * mask

    k0 = int(np.argmax(np.abs(r)))
    peak = float(np.abs(r[k0]))

    # parabolic sub-sample refinement around k0
    if 0 < k0 < len(r) - 1:
        frac = _parabolic_interp(r[k0 - 1], r[k0], r[k0 + 1])
    else:
        frac = 0.0

    delay_samples = (lags[k0] + frac)
    return float(delay_samples), peak

def refine_against(ref: np.ndarray,
                   chans: Dict[str, np.ndarray],
                   fs: int,
                   max_lag_s: float | None = None,
                   ref_mic: str | None = None) -> Tuple[Dict[str, float], Dict[str, float]]:
    """
    Compute per-mic delay relative to ref (in samples, float) via GCC-PHAT.
    Returns:
        delays_samples[mic] -> float
        peaks[mic]          -> float
    """
    delays: Dict[str, float] = {}
    peaks: Dict[str, float] = {}
    for mic, x in chans.items():
        if ref_mic is not None and mic == ref_mic:
            delays[mic], peaks[mic] = 0.0, 1.0
            continue
        if x is ref:
            delays[mic], peaks[mic] = 0.0, 1.0
            continue
        d, p = gcc_phat_delay(ref, x, fs, max_lag_s=max_lag_s)
        delays[mic], peaks[mic] = d, p
    return delays, peaks