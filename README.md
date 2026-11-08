# Low-power wake sensor for long-term deep-sea observation: tank rig


[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24050748.svg)](https://doi.org/10.5281/zenodo.24050748)

Hardware, firmware and tools for the tank experiments behind an IEEE/MTS OCEANS 2027 student poster
(abstract due 2027-01-15). A 160 x 120 HM01B0 camera on a Raspberry Pi Pico watches a dark tank and decides
when to wake a main camera; the rig measures false wakes and energy per frame under controlled lighting,
turbidity and targets, against a time-lapse baseline on a Raspberry Pi 4.

Status (2026-11-07): rig documented, parts in hand, nothing verified on hardware yet. The analysis notebooks
and pre-registered designs from the simulation and public-recording stages live elsewhere and will be added.

## Layout

| Path | Contents |
|---|---|
| `hw/WIRING.md` | Pin tables and breadboard rows for both Picos, energy-measurement wiring |
| `hw/BOM.csv` | Parts, sources and prices |
| `hw/*.png`, `hw/schematics.py` | Schematics A to E and the script that draws them |
| `firmware/pico1_camera/` | Camera demo firmware (USB webcam) and build record |
| `firmware/pico2_env/main.py` | MicroPython: water temperature, transmissometer, target servo |
| `tools/log_serial.py` | Logs the Pico 2 stream to CSV on the PC, steps the servo |
| `tools/scope_energy.py` | Energy per pulse from a Tektronix CSV of a low-side shunt |
| `data/` | Raw recordings (see `data/README.md`) |

## Boards

| Board | Role |
|---|---|
| Pico 1 (Pico H) + HM01B0 | wake sensor; sensor LED via 2N7000 |
| Pico 2 (Pico H) | DS18B20 water temperature, BPW34 transmissometer, SG90 target servo |
| Raspberry Pi 4 + Pi camera module | time-lapse baseline |

## Licences

Code: MIT (`LICENSE`). Data and figures: CC BY 4.0. Third-party code keeps its own licence
(hm01b0-library-for-pico and TinyUSB: MIT).

## Citation

Zenodo DOI for all versions (resolves to the latest): https://doi.org/10.5281/zenodo.24050748
v0.1.0 (rig design, not yet verified on hardware): https://doi.org/10.5281/zenodo.24050749
