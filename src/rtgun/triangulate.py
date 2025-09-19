# src/rtgun/triangulate.py
from __future__ import annotations
import numpy as np
from typing import Dict, Tuple

def _normalize_deg(a: float) -> float:
    # keep angle in [0, 360)
    a %= 360.0
    return a if a >= 0 else a + 360.0

def azimuth_from_tdoa_xy(
    mic_xy: Dict[str, Tuple[float, float]],
    delays_sec: Dict[str, float],
    c: float = 343.0,
    ref_mic: str = "M1",
) -> float:
    """
    Compute azimuth in 2D from mic geometry and TDOA.
    mic_xy: {mic_id: (x,y)} positions
    delays_sec: {mic_id: delay_sec} relative to ref
    c: speed of sound
    ref_mic: reference microphone id
    Return: angle in degrees, 0°=+X, 90°=+Y
    """
    r_ref = np.array(mic_xy[ref_mic], dtype=float)

    A, b = [], []
    for mic, tau in delays_sec.items():
        if mic == ref_mic or mic not in mic_xy:
            continue
        ri = np.array(mic_xy[mic], dtype=float)
        A.append(ri - r_ref)  # vector baseline
        b.append(c * float(tau))  # distance difference

    if not A:
        return float("nan")

    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)

    # least squares solve: A*n = b
    n, *_ = np.linalg.lstsq(A, b, rcond=None)
    if np.linalg.norm(n) < 1e-12:
        return float("nan")

    u = -n / np.linalg.norm(n)  # direction to source
    az = np.degrees(np.arctan2(u[1], u[0]))
    return _normalize_deg(float(az))