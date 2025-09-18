from rtgun.sync_timebase import sync_window
from rtgun.tdoa_gcc import tdoa_delays

def test_tdoa_delays():
    chans, fs = sync_window("2025-09-16T11:00:00.5Z")
    d_smpl, d_sec, peaks = tdoa_delays(chans, fs, ref_mic="M1", max_lag_s=0.02)
    print("Samples:", d_smpl)
    print("Seconds:", d_sec)
    print("Peaks:", peaks)

    # Для синтетики проверка: M2 ~ +0.004s, M3 ~ +0.008s
    assert 0.003 <= d_sec["M2"] <= 0.005
    assert 0.007 <= d_sec["M3"] <= 0.009