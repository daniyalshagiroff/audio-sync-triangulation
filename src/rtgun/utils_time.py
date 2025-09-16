from datetime import datetime, timezone, timedelta

ISO_FMT = "%Y-%m-%dT%H:%M:%S%z"  # expects 'Z' → we’ll handle separately

def parse_iso(iso: str) -> datetime:
    # Accept '...Z' or with offset
    if iso.endswith("Z"):
        iso = iso[:-1] + "+0000"
    elif iso[-3] == ":" and (iso[-6] in "+-"):
        # e.g. +03:00 -> +0300
        iso = iso[:-3] + iso[-2:]
    #Return datetime 
    return datetime.strptime(iso, ISO_FMT)

def to_iso_z(dt: datetime) -> str:
    #Return in UTC time
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def utc_to_sample(utc_start_iso: str, utc_target_iso: str, fs: int) -> int:
    t0 = parse_iso(utc_start_iso).astimezone(timezone.utc)
    tt = parse_iso(utc_target_iso).astimezone(timezone.utc)
    #Calculate difference between target and start
    dt = (tt - t0).total_seconds()
    return int(round(dt * fs))

def shift_iso(iso: str, seconds: float) -> str:
    t = parse_iso(iso).astimezone(timezone.utc) + timedelta(seconds=seconds)
    return to_iso_z(t)

def iso_to_filename_stamp(iso: str) -> str:
    """'2025-09-16T11:00:00Z' -> '2025-09-16T11-00-00Z'"""
    return iso.replace(":", "-")