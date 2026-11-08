"""Top-down breadboard pictures matching hw/WIRING.md. Run: python breadboard_views.py"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Wedge

HERE = os.path.dirname(os.path.abspath(__file__))
MIRROR = True  # draw as seen with column a on the right (e d c b a), matching the user's board


def H(ha):
    if not MIRROR:
        return ha
    return {'left': 'right', 'right': 'left'}.get(ha, ha)
for f in font_manager.findSystemFonts():
    if 'NotoSansCJK-Regular' in f or 'NotoSansCJKkr' in f:
        font_manager.fontManager.addfont(f)
plt.rcParams['font.family'] = ['Noto Sans CJK KR', 'Noto Sans CJK JP', 'DejaVu Sans']

S = 1.7  # hole pitch in drawing units
_cols = {'L+': 0.0, 'L-': 1.0, 'a': 3.0, 'b': 4.0, 'c': 5.0, 'd': 6.0, 'e': 7.0,
         'f': 9.0, 'g': 10.0, 'h': 11.0, 'i': 12.0, 'j': 13.0, 'R+': 15.0, 'R-': 16.0}
COLX = {k: v * S for k, v in _cols.items()}
WIRE = {'red': '#d62728', 'black': '#222222', 'yellow': '#e6b800', 'blue': '#1f5fbf', 'green': '#2a9d3a',
        'orange': '#ff7f0e', 'purple': '#7b3fa0', 'white': '#9a9a9a', 'brown': '#8c564b'}


def P(col, row):
    return COLX[col], -row * S


class Board:
    def __init__(self, title, r0, r1, right_rails=False, rail_labels=None):
        self.r0, self.r1 = r0, r1
        self.fig, self.ax = plt.subplots(figsize=(13, 0.55 * (r1 - r0 + 6) + 1.5))
        ax = self.ax
        ax.set_aspect('equal'); ax.set_axis_off()
        xr = COLX['R-'] if right_rails else COLX['j']
        ax.add_patch(FancyBboxPatch((-0.9, -r1 * S - 0.9), xr + 1.8, (r1 - r0) * S + 1.8, boxstyle='round,pad=0.1',
                                    fc='#f7f7f2', ec='#bbbbbb'))
        ax.add_patch(Rectangle((COLX['e'] + 0.6, -r1 * S - 0.9), COLX['f'] - COLX['e'] - 1.2, (r1 - r0) * S + 1.8,
                               fc='#e9e9e2', ec='none'))
        rl = rail_labels or {}
        for col in COLX:
            if col in ('R+', 'R-') and not right_rails:
                continue
            for r in range(r0, r1 + 1):
                x, y = P(col, r)
                ax.add_patch(Circle((x, y), 0.17, fc='#555555', ec='none', zorder=1))
        for col, color in (('L+', 'red'), ('L-', 'blue')) + ((('R+', 'red'), ('R-', 'blue')) if right_rails else ()):
            x = COLX[col]
            ax.plot([x + (0.45 if '+' in col else -0.45)] * 2, [-r0 * S + 0.6, -r1 * S - 0.6],
                    color=WIRE['red'] if color == 'red' else WIRE['blue'], lw=1.5, zorder=0)
            ax.text(x, -r0 * S + 1.0, ('+' if '+' in col else '−') + '\n' + rl.get(col, ''), ha='center', va='bottom',
                    fontsize=9, color=WIRE['red'] if '+' in col else WIRE['blue'], fontweight='bold')
        for c in 'abcde':
            ax.text(COLX[c], -r0 * S + 1.0, c, ha='center', fontsize=11, fontweight='bold')
        for r in range(r0, r1 + 1):
            ax.text((COLX['e'] + COLX['f']) / 2 + 0.25, -r * S, str(r), ha='center', va='center', fontsize=9, color='#777777')
        ax.set_title(title, fontsize=13, loc='left')
        self.left_labels = []

    def jumper(self, a, b, color, label=None):
        (x1, y1), (x2, y2) = P(*a), P(*b)
        self.ax.plot([x1, x2], [y1, y2], color=WIRE[color], lw=4, solid_capstyle='round', zorder=3)
        # on-board jumpers are male-male; see the note under each picture

    def offboard(self, hole, color, label, side='left', mid=False):
        x, y = P(*hole)
        xe = -8.0 if side == 'left' else COLX['R-'] + 8.0
        xend = xe + (1.0 if side == 'left' else -1.0)
        if mid:  # leave the hole, then run halfway between rows so the wire never passes over a hole
            ym = y - S / 2
            xs, ys = [x, x, xend], [y, ym, ym]
            ylab = ym
        else:
            xs, ys = [x, xend], [y, y]
            ylab = y
        self.ax.plot(xs, ys, color=WIRE[color], lw=4, solid_capstyle='round', solid_joinstyle='round',
                     zorder=2, alpha=0.9)
        self.ax.text(xe + (0.8 if side == 'left' else -0.8), ylab, label, fontsize=8.5,
                     ha=H('right' if side == 'left' else 'left'), va='center', zorder=6,
                     bbox=dict(fc='white', ec=WIRE[color], lw=1.2, boxstyle='round,pad=0.25'))

    def resistor(self, a, b, value):
        (x1, y1), (x2, y2) = P(*a), P(*b)
        self.ax.plot([x1, x2], [y1, y2], color='#666666', lw=1.5, zorder=4)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        horiz = abs(x2 - x1) > abs(y2 - y1)
        w, h = (1.3, 0.5) if horiz else (0.5, 1.3)
        self.ax.add_patch(Rectangle((mx - w / 2, my - h / 2), w, h, fc='#e8c88a', ec='#7a5a20', zorder=5))
        self.ax.text(mx + (0 if horiz else 0.4), my + (0.35 if horiz else 0), value, fontsize=9,
                     ha='center' if horiz else H('left'), va='bottom' if horiz else 'center', zorder=6,
                     fontweight='bold')

    def mosfet(self, col, rows, name):
        xs = [P(col, r) for r in rows]
        x = xs[0][0]
        self.ax.add_patch(Rectangle((x - 0.4, xs[-1][1] - 0.45), 0.8, xs[0][1] - xs[-1][1] + 0.9,
                                    fc='#111111', ec='black', zorder=5))
        for (xx, yy), lab in zip(xs, 'SGD'):
            self.ax.text(xx + 0.6, yy, lab, fontsize=10, va='center', ha=H('left'), fontweight='bold', zorder=6)
        self.ax.text(COLX['f'] - 0.2, (xs[0][1] + xs[-1][1]) / 2, name, fontsize=8.5, va='center', ha=H('left'), zorder=6,
                     bbox=dict(fc='white', ec='#333333', lw=0.8, boxstyle='round,pad=0.2'))

    def led(self, cathode, anode, name):
        (x1, y1), (x2, y2) = P(*cathode), P(*anode)
        cx, cy = COLX['L+'] - 3.2, (y1 + y2) / 2
        self.ax.add_patch(Circle((cx, cy), 0.6, fc='#fffbe0', ec='#999900', lw=1.5, zorder=5))
        for (xx, yy), lab in (((x1, y1), '− 짧은 다리'), ((x2, y2), '+ 긴 다리')):
            self.ax.plot([xx, cx + 0.5], [yy, cy + (0.25 if yy > cy else -0.25)], color='#aaaa00', lw=1.6, zorder=4)
            self.ax.text(xx - 0.3, yy + (0.3 if yy > cy else -0.3), lab, fontsize=8, ha=H('right'),
                         va='bottom' if yy > cy else 'top', zorder=6)
        self.ax.text(cx - 0.8, cy, name, fontsize=8.5, ha=H('right'), va='center', zorder=6)

    def note(self, text):
        import matplotlib.transforms as mt
        tr = mt.blended_transform_factory(self.ax.transAxes, self.ax.transData)
        self.ax.text(0.12, -self.r1 * S - 1.8, text, fontsize=9.5, va='top', ha='left', transform=tr)

    def save(self, name):
        self.ax.set_xlim(-19, COLX['R-'] + 19); self.ax.set_ylim(-self.r1 * S - 6, -self.r0 * S + 3.4)
        if MIRROR:
            self.ax.invert_xaxis()
        self.fig.savefig(os.path.join(HERE, name), dpi=140, bbox_inches='tight')
        plt.close(self.fig)


# ---------------- Pico 1 ----------------
b = Board('피코 1 브레드보드 (센서 LED)', 8, 16, right_rails=False,
          rail_labels={'L+': '5 V', 'L-': 'GND'})
b.offboard(('L+', 8), 'red', '피코 40번 (VBUS)  암-수')
b.offboard(('L-', 9), 'black', '피코 18번 (GND)  암-수')
b.mosfet('e', [10, 11, 12], '2N7000\n평평한 면이\n나를 향하게')
b.jumper(('a', 10), ('L-', 10), 'black', '수-수')
b.resistor(('d', 11), ('d', 14), '220 Ω')
b.resistor(('c', 11), ('L-', 11), '10 kΩ')
b.led(('a', 12), ('a', 13), '5 mm 백색 LED')
b.resistor(('b', 13), ('L+', 13), '100 Ω')
b.offboard(('a', 14), 'yellow', '피코 20번 (GP15)  암-수', mid=True)
b.note('카메라(HM01B0)는 브레드보드를 안 거치고 암-암 점퍼로 피코에 직결 (WIRING.md 표).\n'
       '테스트: a14 점퍼의 피코 쪽 끝을 + 레일에 잠깐 대면 LED가 켜져야 함.\n'
       '레일은 위치가 아니라 빨간 선(+) / 파란 선(−) 색으로 맞출 것.\n'
       '보드 안의 굵은 짧은 선 = 수-수 점퍼. 보드 밖으로 나가는 선 = 표시된 종류(대부분 암-수).\n'
       '보드 밖으로 나가는 선이 구멍에서 반 칸 꺾이는 건 그림을 안 겹치게 하려는 것일 뿐, 꽂는 구멍은 꺾이기 전 점.')
b.save('BB_pico1.png')

# ---------------- Pico 2 ----------------
b = Board('피코 2 브레드보드 (투과율계 · 온도 · 서보)', 8, 33, right_rails=True,
          rail_labels={'L+': '3V3', 'L-': 'GND', 'R+': '5 V', 'R-': 'GND'})
b.offboard(('L+', 8), 'red', '피코 36번 (3V3)  암-수')
b.offboard(('L-', 9), 'black', '피코 38번 (GND)  암-수')
b.offboard(('R+', 8), 'red', '피코 40번 (VBUS 5 V)  암-수', side='right')
b.offboard(('R-', 9), 'black', '피코 28번 (GND)  암-수', side='right')
# transmissometer LED driver
b.mosfet('e', [10, 11, 12], '2N7000')
b.jumper(('a', 10), ('L-', 10), 'black', '수-수')
b.resistor(('d', 11), ('d', 14), '220 Ω')
b.resistor(('c', 11), ('L-', 11), '10 kΩ')
b.offboard(('a', 12), 'white', '투과율계 LED − (짧은 다리), 긴 선', mid=True)
b.offboard(('a', 13), 'white', '투과율계 LED + (긴 다리), 긴 선', mid=True)
b.resistor(('b', 13), ('b', 16), '100 Ω')
b.offboard(('a', 14), 'yellow', '피코 20번 (GP15)  암-수', mid=True)
b.jumper(('a', 16), ('R+', 16), 'red', '수-수 (5 V 레일로)')
# photodiode
b.offboard(('a', 20), 'white', 'BPW34 캐소드, 긴 선', mid=True)
b.jumper(('b', 20), ('L+', 20), 'red', '수-수')
b.offboard(('a', 21), 'white', 'BPW34 애노드, 긴 선', mid=True)
b.offboard(('d', 21), 'green', '피코 31번 (GP26)  암-수', side='right', mid=True)
b.resistor(('c', 21), ('c', 23), '100 kΩ')
b.offboard(('a', 23), 'black', '피코 33번 (AGND)  암-수', mid=True)
# DS18B20
b.offboard(('a', 26), 'red', 'DS18B20 모듈 VCC  암-수', mid=True)
b.jumper(('b', 26), ('L+', 26), 'red', '수-수')
b.offboard(('a', 27), 'yellow', 'DS18B20 모듈 DAT  암-수', mid=True)
b.offboard(('d', 27), 'yellow', '피코 29번 (GP22)  암-수', side='right', mid=True)
b.offboard(('a', 28), 'black', 'DS18B20 모듈 GND  암-수', mid=True)
b.jumper(('b', 28), ('L-', 28), 'black', '수-수')
# servo
b.offboard(('a', 30), 'orange', '피코 21번 (GP16)  암-수', mid=True)
b.offboard(('d', 30), 'orange', '서보 주황선  수-수', side='right', mid=True)
b.offboard(('R+', 33), 'red', '서보 빨간선  수-수', side='right')
b.offboard(('R-', 32), 'brown', '서보 갈색선  수-수', side='right')
b.note('피코 1과 다른 브레드보드를 쓸 것 (a열 옆 + 레일이 여기서는 3V3, 피코 1에서는 5 V).\n'
       '3V3 레일과 5 V 레일에 테이프로 이름을 붙일 것. 5 V를 DS18B20·BPW34·GPIO에 연결하지 말 것.\n'
       '왼쪽으로 나간 선(GP26, GP22, 서보 주황)은 브레드보드 위를 가로질러 d21, d27, d30 구멍에 꽂는다는 뜻.\n'
       '레일 구멍은 세로로 전부 연결돼 있어서, 레일 쪽 끝은 아무 행에 꽂아도 같음.\n'
       '보드 안의 굵은 짧은 선 = 수-수 점퍼. 흰 선 = 수조 끝까지 가는 긴 선.\n'
       '보드 밖으로 나가는 선이 구멍에서 반 칸 꺾이는 건 그림을 안 겹치게 하려는 것일 뿐, 꽂는 구멍은 꺾이기 전 점.')
b.save('BB_pico2.png')
print('ok')
