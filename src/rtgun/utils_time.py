from datetime import datetime, timezone, timedelta

ISO_FMT = "%Y-%m-%dT%H:%M:%S%z"  # expects 'Z' → we’ll handle separately

def parse_iso(iso: str) -> datetime:
    s = iso.strip()
    # 'Z' -> '+00:00' для совместимости с fromisoformat
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    # datetime.fromisoformat понимает дробные секунды (.05, .500) и смещения с двоеточием
    dt = datetime.fromisoformat(s)
    return dt

def to_iso_z(dt: datetime) -> str:
    dt = dt.astimezone(timezone.utc)
    # .%f → микросекунды, срез [:3] → миллисекунды
    if dt.microsecond:
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    else:
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def utc_to_sample(utc_start_iso: str, utc_target_iso: str, fs: int) -> int:
    t0 = parse_iso(utc_start_iso).astimezone(timezone.utc)
    tt = parse_iso(utc_target_iso).astimezone(timezone.utc)
    #Calculate difference between target and start
    dt = (tt - t0).total_seconds()
    return int(round(dt * fs))

def shift_iso(iso: str, delta_s: float) -> str:
    print(f"Shifting {iso} by {delta_s} seconds")
    dt = parse_iso(iso).astimezone(timezone.utc)
    dt2 = dt + timedelta(seconds=delta_s)   # delta_s может быть 0.5
    print(f"Unprinted: {dt2}")
    print(f"Result: {to_iso_z(dt2)}")
    return to_iso_z(dt2)    

def iso_to_filename_stamp(iso: str) -> str:
    """'2025-09-16T11:00:00Z' -> '2025-09-16T11-00-00Z'"""
    return iso.replace(":", "-")