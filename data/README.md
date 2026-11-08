# Data

Raw recordings from the tank. Licence: CC BY 4.0.

File naming: `<kind>_<YYYY-MM-DD>_<block>.<ext>`, for example `env_2026-11-20_pilot.csv`, `scope_2026-11-21_frame-1ohm.csv`.

Kinds:
- `env_*.csv`: Pico 2 log (tools/log_serial.py). Columns: pc_iso, t_ms, temp_c, adc_on, adc_off, adc_diff, servo_deg.
- `scope_*.csv`: oscilloscope waveform (Tektronix CSV), with `*_summary.json` and `*_pulses.csv` from tools/scope_energy.py.
- `frames_*`: sensor frames (format defined with the measurement firmware).

Every run gets a line in `runlog.csv`: date, file, block, lighting, turbidity step, target, load resistor, shunt value, wiring changes, notes.
Never edit raw files; corrections go in runlog.csv.
