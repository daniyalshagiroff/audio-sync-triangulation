# tests/test_timebase.py
import numpy as np
import soundfile as sf
from pathlib import Path

FS = 48000
PRE = 3.0
POST = 3.0
WIN_SAMPLES = int((PRE + POST) * FS)

def load_synced():
    p = Path("data/synced")
    files = sorted(p.glob("*_M*_synced.wav"))
    assert files, "No synced wavs found. Run gen_clicks.py and rtgun sync first."
    by_mic = {}
    for f in files:
        # ...__M1_synced.wav → M1
        mic = f.stem.split("_")[-2]
        x, fs = sf.read(f, always_2d=False)
        assert fs == FS
        if x.ndim > 1: x = x[:,0]
        by_mic[mic] = np.asarray(x, dtype=np.float32)
    return by_mic

def test_all_same_length():
    by_mic = load_synced()
    lens = {k: len(v) for k,v in by_mic.items()}
    assert len(set(lens.values())) == 1, f"Different lengths: {lens}"
    assert next(iter(lens.values())) == WIN_SAMPLES, f"Unexpected window length {lens}"

def test_click_present_near_center():
    by_mic = load_synced()
    # Center sample ~ PRE seconds от начала окна
    center = int(PRE * FS)
    for mic, x in by_mic.items():
        # Находим максимальный пик в окне ±50 мс вокруг центра
        w = int(0.05 * FS)
        segment = x[center - w:center + w]
        peak_idx = np.argmax(np.abs(segment))
        # пик должен существовать
        assert np.abs(segment[peak_idx]) > 0.5, f"No clear peak for {mic}"

def test_relative_delays_consistent():
    # В synthetic: M2 запаздывает ~4 ms, M3 ~8 ms относительно M1
    by_mic = load_synced()
    x1, x2, x3 = by_mic["M1"], by_mic["M2"], by_mic["M3"]

    def coarse_delay(a, b):
        # простая кросс-корреляция (грубая оценка), для синтетики достаточно
        corr = np.correlate(b, a, mode="full")
        lag = np.argmax(corr) - (len(a) - 1)
        return lag

    d12 = coarse_delay(x1, x2)  # samples (x2 позже → положительный лаг)
    d13 = coarse_delay(x1, x3)

    ms12 = d12 * 1000.0 / FS
    ms13 = d13 * 1000.0 / FS

    # допускаем погрешность ±1 ms на грубой оценке
    assert 3.0 <= ms12 <= 5.0, f"M2 delay {ms12:.2f} ms not ~4 ms"
    assert 7.0 <= ms13 <= 9.0, f"M3 delay {ms13:.2f} ms not ~8 ms"