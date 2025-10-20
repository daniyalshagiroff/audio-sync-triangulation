# src/rtgun/tdoa_gcc.py
from __future__ import annotations
import numpy as np
from typing import Dict, Tuple
from .sync_refine import refine_against

def tdoa_delays(chans: Dict[str, np.ndarray],
                fs: int,
                ref_mic: str = "M1",
                max_lag_s: float | None = None
                ) -> Tuple[Dict[str, float], Dict[str, float], Dict[str, float]]:
    """
    Wrapper: compute GCC-PHAT delays for all mics vs ref_mic.
    Returns:
        delays_samples[mic] -> float
        delays_sec[mic]     -> float
        peaks[mic]          -> float
    """
    assert ref_mic in chans, f"ref_mic '{ref_mic}' not in chans"

    # order dict to ensure ref first (not strictly required, just neat)
    ordered = {ref_mic: chans[ref_mic]} | {k: v for k, v in chans.items() if k != ref_mic}

    delays_samples, peaks = refine_against(
        ref=ordered[ref_mic],
        chans=ordered,
        fs=fs,
        max_lag_s=max_lag_s,
        ref_mic=ref_mic,
    )
    delays_samples = {k: -v for k, v in delays_samples.items()}
    print("Delays (samples):", delays_samples)
    delays_sec = {k: v / float(fs) for k, v in delays_samples.items()}
    print("Delays (sec):", delays_sec)
    print("Peaks:", peaks)
    return delays_samples, delays_sec, peaks