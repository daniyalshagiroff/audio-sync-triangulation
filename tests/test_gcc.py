# tests/test_gcc.py
from rtgun.utils_time import utc_to_sample

def test_utc_to_sample_simple():
    fs = 48000
    s = utc_to_sample("2025-09-16T11:00:00Z", "2025-09-16T11:00:01Z", fs)
    assert s == fs