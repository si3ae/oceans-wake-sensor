"""Pico pin maps (which Pico pin goes where). Run: python pico_pinmaps.py"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle

HERE = os.path.dirname(os.path.abspath(__file__))
for f in font_manager.findSystemFonts():
    if 'NotoSansCJK-Regular' in f:
        font_manager.fontManager.addfont(f)
plt.rcParams['font.family'] = ['Noto Sans CJK KR', 'Noto Sans CJK JP', 'DejaVu Sans']

LEFT = ['GP0', 'GP1', 'GND', 'GP2', 'GP3', 'GP4', 'GP5', 'GND', 'GP6', 'GP7', 'GP8', 'GP9', 'GND',
        'GP10', 'GP11', 'GP12', 'GP13', 'GND', 'GP14', 'GP15']                      # pins 1..20, top to bottom
RIGHT = ['VBUS', 'VSYS', 'GND', '3V3_EN', '3V3(OUT)', 'ADC_VREF', 'GP28', 'AGND', 'GP27', 'GP26',
         'RUN', 'GP22', 'GND', 'GP21', 'GP20', 'GP19', 'GP18', 'GND', 'GP17', 'GP16']  # pins 40..21, top to bottom
COL = {'red': '#d62728', 'black': '#222222', 'yellow': '#e6b800', 'blue': '#1f5fbf', 'green': '#2a9d3a',
       'orange': '#ff7f0e', 'purple': '#7b3fa0', 'gray': '#8a8a8a', 'brown': '#8c564b', 'cyan': '#17a2b8'}


def pin_xy(n):
    if 1 <= n <= 20:
        return -1.6, -(n - 1) * 0.6
    return 1.6, -(40 - n) * 0.6


def draw(title, uses, note, fname):
    """uses: {pin_number: (destination text, color)}"""
    fig, ax = plt.subplots(figsize=(12, 9.5))
    ax.set_aspect('equal'); ax.set_axis_off()
    ax.add_patch(FancyBboxPatch((-1.9, -11.75), 3.8, 12.4, boxstyle='round,pad=0.05', fc='#2f7d4f', ec='#1d4d31', lw=2))
    ax.add_patch(Rectangle((-0.55, 0.45), 1.1, 0.6, fc='#c0c0c0', ec='#777777', zorder=3))
    ax.text(0, 1.25, 'USB', ha='center', fontsize=10, fontweight='bold')
    ax.add_patch(Rectangle((-0.7, -6.2), 1.4, 1.4, fc='#111111', ec='none'))
    ax.text(0, -5.5, 'RP2040', ha='center', va='center', color='white', fontsize=8)
    ax.add_patch(Rectangle((-0.5, -1.6), 0.6, 0.35, fc='white', ec='#999999'))
    ax.text(0.25, -1.43, 'BOOTSEL', fontsize=6.5, va='center', color='white')
    for n in range(1, 41):
        x, y = pin_xy(n)
        name = LEFT[n - 1] if n <= 20 else RIGHT[40 - n]
        used = n in uses
        ax.add_patch(Circle((x, y), 0.17, fc='#ffd700' if used else '#d9d9d9', ec='#555555', zorder=4))
        inner = 0.35 if n <= 20 else -0.35
        ax.text(x + inner, y, f'{n}', fontsize=7.5, va='center', ha='left' if n <= 20 else 'right', color='white')
        outer = -0.55 if n <= 20 else 0.55
        ax.text(x + outer, y, name, fontsize=8.5, va='center', ha='right' if n <= 20 else 'left',
                fontweight='bold' if used else 'normal', color='black' if used else '#888888')
        if used:
            dest, c = uses[n]
            xe = -7.6 if n <= 20 else 7.6
            ax.plot([x + (-1.75 if n <= 20 else 2.45), xe], [y, y], color=COL[c], lw=3.5, zorder=2,
                    solid_capstyle='round')
            ax.text(xe + (-0.15 if n <= 20 else 0.15), y, dest, fontsize=9, va='center',
                    ha='right' if n <= 20 else 'left',
                    bbox=dict(fc='white', ec=COL[c], lw=1.3, boxstyle='round,pad=0.25'))
    ax.text(-1.6, 0.55, '1번', fontsize=8, ha='center', color='#d62728', fontweight='bold')
    ax.text(0, -12.5, note, fontsize=9.5, ha='center', va='top')
    ax.set_title(title, fontsize=14, loc='left')
    ax.set_xlim(-15.5, 15.5); ax.set_ylim(-15.0, 2.2)
    fig.savefig(os.path.join(HERE, fname), dpi=140, bbox_inches='tight')
    plt.close(fig)


draw('피코 1: 어느 핀이 어디로 가나 (USB를 위로, 칩이 보이는 면을 위로)', {
    6: ('카메라 SDA   (암-암)', 'blue'),
    7: ('카메라 SCL   (암-암)', 'green'),
    9: ('카메라 VSYNC (암-암)', 'purple'),
    10: ('카메라 HREF  (암-암)', 'cyan'),
    11: ('카메라 PCLK  (암-암)', 'orange'),
    12: ('카메라 D0    (암-암)', 'brown'),
    18: ('브레드보드 a쪽 − 레일 (GND)  (암-수)', 'black'),
    20: ('브레드보드 a14 (LED 신호)  (암-수)', 'yellow'),
    36: ('카메라 VCC   (암-암)', 'red'),
    38: ('카메라 GND   (암-암)', 'black'),
    40: ('브레드보드 a쪽 + 레일 (5 V)  (암-수)', 'red'),
}, '카메라 쪽은 기판(UC-805)에 인쇄된 글자를 보고 같은 이름끼리 연결. RESET, MCLK(XCLK), INT, TRIG, D1~D7 등 나머지는 비워 둠.\n'
   '카메라 VCC는 반드시 36번(3V3). 40번(VBUS, 5 V)에 꽂으면 카메라가 망가질 수 있음.\n'
   '핀 번호는 피코 뒷면에도 인쇄돼 있음. 왼쪽 줄 1~20번은 위에서 아래로, 오른쪽 줄은 위가 40번.', 'PINS_pico1.png')

draw('피코 2: 어느 핀이 어디로 가나 (USB를 위로, 칩이 보이는 면을 위로)', {
    20: ('브레드보드 a14 (투과율계 LED 신호)  (암-수)', 'yellow'),
    21: ('브레드보드 a30 (서보 신호)  (암-수)', 'orange'),
    28: ('브레드보드 j쪽 − 레일 (GND)  (암-수)', 'black'),
    29: ('브레드보드 d27 (DS18B20 DAT)  (암-수)', 'yellow'),
    31: ('브레드보드 d21 (BPW34)  (암-수)', 'green'),
    33: ('브레드보드 a23 (AGND)  (암-수)', 'gray'),
    36: ('브레드보드 a쪽 + 레일 (3V3)  (암-수)', 'red'),
    38: ('브레드보드 a쪽 − 레일 (GND)  (암-수)', 'black'),
    40: ('브레드보드 j쪽 + 레일 (5 V)  (암-수)', 'red'),
}, '피코 2에는 카메라를 연결하지 않음. DS18B20 모듈은 피코에 직결하지 않고 브레드보드(a26~a28)를 거침 (BB_pico2.png).\n'
   '3V3(36번)과 VBUS(40번)는 서로 다른 레일. 레일에 테이프로 3V3 / 5 V 이름을 붙일 것.', 'PINS_pico2.png')
print('ok')
