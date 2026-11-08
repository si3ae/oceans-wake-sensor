"""Log the Pico 2 environment stream to CSV on the PC, optionally stepping the servo.

Usage (Windows example):
    pip install pyserial
    python log_serial.py --port COM5 --out ../data/env_2026-11-20_pilot.csv --note "clear water, 100k load"
    python log_serial.py --port COM5 --out run.csv --servo 30,60,90,120,150 --dwell 20

Find the port: Thonny shows it bottom right, or Device Manager > Ports (COM & LPT).
Each data line from the Pico is written with the PC time prepended (pc_iso). Lines starting with '#'
(start-up info, command echoes) go into the file too, so the file is a complete record.
Stop with Ctrl+C. Close Thonny first: only one program can hold the port.
"""
import argparse
import datetime as dt
import sys
import time

import serial  # pyserial


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--baud', type=int, default=115200)
    ap.add_argument('--servo', default='', help='comma-separated angles to step through, e.g. 30,60,90')
    ap.add_argument('--dwell', type=float, default=20.0, help='seconds per servo angle')
    ap.add_argument('--repeat', type=int, default=1, help='times to repeat the servo sequence')
    ap.add_argument('--note', default='', help='free text written at the top of the file')
    a = ap.parse_args()

    angles = [int(x) for x in a.servo.split(',') if x.strip()]
    schedule = [ang for _ in range(a.repeat) for ang in angles]

    with serial.Serial(a.port, a.baud, timeout=0.2) as ser, open(a.out, 'a', encoding='utf-8') as f:
        f.write(f'# log_serial start {dt.datetime.now().isoformat(timespec="seconds")} port={a.port}\n')
        if a.note:
            f.write(f'# note: {a.note}\n')
        if schedule:
            f.write(f'# servo schedule: {schedule} dwell_s={a.dwell}\n')
        f.write('pc_iso,t_ms,temp_c,adc_on,adc_off,adc_diff,servo_deg\n')
        next_change = time.monotonic()
        idx = 0
        buf = b''
        try:
            while True:
                if idx < len(schedule) and time.monotonic() >= next_change:
                    ser.write(f'S {schedule[idx]}\n'.encode())
                    idx += 1
                    next_change = time.monotonic() + a.dwell
                elif schedule and idx >= len(schedule) and time.monotonic() >= next_change:
                    print('servo schedule finished; still logging (Ctrl+C to stop)')
                    schedule = []
                buf += ser.read(256)
                while b'\n' in buf:
                    raw, buf = buf.split(b'\n', 1)
                    line = raw.decode(errors='replace').strip()
                    if not line:
                        continue
                    now = dt.datetime.now().isoformat(timespec='milliseconds')
                    if line.startswith('#'):
                        f.write(line + '\n')
                    elif line.startswith('t_ms'):
                        pass  # header already written by the logger
                    else:
                        f.write(f'{now},{line}\n')
                    f.flush()
                    print(line)
        except KeyboardInterrupt:
            f.write(f'# log_serial stop {dt.datetime.now().isoformat(timespec="seconds")}\n')
            print('stopped')


if __name__ == '__main__':
    sys.exit(main())
