import yaml
from pathlib import Path
from pydantic import BaseModel
from typing import List


class DefaultCfg(BaseModel):
    sample_rate: int
    pre_margin_s: float
    post_margin_s: float
    bandpass_hz: List[int]
    upsample_factor: int


class Mic(BaseModel):
    mic_id: str
    x: float
    y: float
    z: float = 0.0


class DevicesCfg(BaseModel):
    mics: List[Mic]


class Cfg(BaseModel):
    defaults: DefaultCfg
    devices: DevicesCfg


def load_cfg() -> Cfg:
    base = Path(__file__).resolve().parents[2]

    with open(base / "configs" / "default.yaml", "r") as f:
        defaults = DefaultCfg(**yaml.safe_load(f))

    with open(base / "configs" / "devices.yaml", "r") as f:
        devices = DevicesCfg(**yaml.safe_load(f))

    return Cfg(defaults=defaults, devices=devices)


if __name__ == "__main__":
    cfg = load_cfg()
    print(cfg.defaults.sample_rate)
    for mic in cfg.devices.mics:
        print(mic.mic_id, mic.x, mic.y, mic.z)