"""Energy per pulse from an oscilloscope capture of a low-side shunt (hw/WIRING.md, schematic E).

Input: a CSV saved by the Tektronix TBS1000-series (Save/Recall > Save Waveform > CSV) or any CSV whose
last two numeric columns per row are time [s] and shunt voltage [V].

    python scope_energy.py TEK0000.CSV --rshunt 1.02 --vsupply 5.00
    python scope_energy.py TEK0001.CSV --rshunt 1.02 --vsupply 5.00 --thresh 0.030 --plot

Model (low-side shunt):
    I(t)     = Vshunt(t) / Rshunt
    Vload(t) = Vsupply - Vshunt(t)
    P(t)     = Vload(t) * I(t)
Pulses are the runs where I(t) is above the threshold (default: halfway between the baseline, taken as
the 20th percentile of I, and the 99th percentile). For each pulse it reports the duration, the charge,
the total energy, and the energy above baseline (the extra cost of that event over idling).

Before trusting a number:
  - Probe switch and the scope's probe menu must agree (both 1X for mV-level shunt signals).
  - The scope stores 2,500 points per capture. Pick a time/div so one pulse spans at least ~50 points,
    and check the 'points per pulse' column.
  - Use the multimeter-measured shunt resistance, not the nominal value.
  - Cross-check once: a steady load measured here should match the multimeter's current reading.
"""
import argparse
import csv
import json
import math
import os
import sys


def read_scope_csv(path):
    meta, t, v = {}, [], []
    with open(path, newline='', encoding='utf-8', errors='replace') as f:
        for row in csv.reader(f):
            if not row:
                continue
            nums = []
            for cell in row:
                try:
                    nums.append(float(cell))
                except ValueError:
                    nums.append(None)
            # metadata like "Probe Atten,1.000000e+00" in the first two columns
            if row[0].strip() and not _isnum(row[0]) and len(row) > 1:
                meta[row[0].strip()] = row[1].strip()
            vals = [x for x in nums if x is not None]
            pos = [i for i, x in enumerate(nums) if x is not None]
            if len(vals) >= 2 and pos[-1] - pos[-2] == 1:
                t.append(vals[-2])
                v.append(vals[-1])
    if len(t) < 10:
        raise SystemExit(f'{path}: found only {len(t)} data rows; is this a waveform CSV?')
    return meta, t, v


def _isnum(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def pct(xs, q):
    s = sorted(xs)
    k = (len(s) - 1) * q
    lo, hi = math.floor(k), math.ceil(k)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def trapz(y, x):
    return sum((x[i + 1] - x[i]) * (y[i] + y[i + 1]) / 2 for i in range(len(x) - 1))


def analyse(t, vsh, rshunt, vsupply, thresh=None, merge_s=0.0):
    i = [x / rshunt for x in vsh]
    p = [(vsupply - x) * ii for x, ii in zip(vsh, i)]
    base_i = pct(i, 0.20)
    top_i = pct(i, 0.99)
    th = thresh if thresh is not None else base_i + 0.5 * (top_i - base_i)
    base_p = (vsupply - base_i * rshunt) * base_i
    # runs above threshold
    runs, start = [], None
    for k, ii in enumerate(i):
        if ii > th and start is None:
            start = k
        elif ii <= th and start is not None:
            runs.append([start, k - 1]); start = None
    if start is not None:
        runs.append([start, len(i) - 1])
    merged = []
    for r in runs:
        if merged and t[r[0]] - t[merged[-1][1]] <= merge_s:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    pulses = []
    for a, b in merged:
        a0, b0 = max(a - 1, 0), min(b + 1, len(t) - 1)  # include the edges
        tt, ii, pp = t[a0:b0 + 1], i[a0:b0 + 1], p[a0:b0 + 1]
        dur = tt[-1] - tt[0]
        e = trapz(pp, tt)
        pulses.append(dict(t_start_s=tt[0], duration_s=dur, points=len(tt),
                           peak_a=max(ii), charge_c=trapz(ii, tt),
                           energy_j=e, energy_above_base_j=e - base_p * dur,
                           clipped_at_edge=(a == 0 or b == len(t) - 1)))
    summary = dict(n_points=len(t), dt_s=(t[-1] - t[0]) / (len(t) - 1), window_s=t[-1] - t[0],
                   rshunt_ohm=rshunt, vsupply_v=vsupply,
                   baseline_a=base_i, baseline_w=base_p, threshold_a=th,
                   mean_a=trapz(i, t) / (t[-1] - t[0]), energy_total_j=trapz(p, t),
                   n_pulses=len(pulses))
    return summary, pulses, i


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('csv')
    ap.add_argument('--rshunt', type=float, required=True, help='measured shunt resistance [ohm]')
    ap.add_argument('--vsupply', type=float, required=True, help='supply voltage at the board [V]')
    ap.add_argument('--thresh', type=float, default=None, help='pulse threshold current [A] (default: auto)')
    ap.add_argument('--merge', type=float, default=0.0, help='merge pulses closer than this [s]')
    ap.add_argument('--plot', action='store_true', help='save <csv>_current.png')
    a = ap.parse_args()

    meta, t, v = read_scope_csv(a.csv)
    summary, pulses, i = analyse(t, v, a.rshunt, a.vsupply, a.thresh, a.merge)
    summary['source_file'] = os.path.basename(a.csv)
    summary['scope_meta'] = {k: meta[k] for k in meta if k in (
        'Source', 'Probe Atten', 'Sample Interval', 'Record Length', 'Vertical Scale', 'Horizontal Scale', 'Model Number')}

    stem = os.path.splitext(a.csv)[0]
    with open(stem + '_pulses.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(pulses[0].keys()) if pulses else ['none'])
        w.writeheader()
        for p in pulses:
            w.writerow(p)
    with open(stem + '_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))
    for k, p in enumerate(pulses):
        flag = '  CLIPPED: pulse touches the capture edge' if p['clipped_at_edge'] else ''
        few = '  FEW POINTS: use a faster time/div' if p['points'] < 50 else ''
        print(f"pulse {k}: {p['duration_s']*1e3:.3f} ms, {p['points']} pts, peak {p['peak_a']*1e3:.2f} mA, "
              f"E {p['energy_j']*1e3:.4f} mJ, above base {p['energy_above_base_j']*1e3:.4f} mJ{flag}{few}")
    if a.plot:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(9, 3.2))
        ax.plot([x * 1e3 for x in t], [x * 1e3 for x in i], lw=0.8)
        ax.axhline(summary['threshold_a'] * 1e3, ls='--', lw=0.8, color='gray')
        ax.set_xlabel('time [ms]'); ax.set_ylabel('current [mA]')
        ax.set_title(os.path.basename(a.csv))
        fig.tight_layout(); fig.savefig(stem + '_current.png', dpi=140)
    return 0


if __name__ == '__main__':
    sys.exit(main())
