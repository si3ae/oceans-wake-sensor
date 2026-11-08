"""Schematics for the tank rig. Run: python schematics.py  -> writes PNGs next to this file."""
import os
import schemdraw
import schemdraw.elements as elm

HERE = os.path.dirname(os.path.abspath(__file__))
schemdraw.config(fontsize=11, unit=2.2)


def save(d, name):
    d.save(os.path.join(HERE, name), dpi=150)


# (A) Pico 1: sensor LED driver (2N7000 low-side switch, 5 mm white LED)
with schemdraw.Drawing(show=False) as d:
    d += elm.Label().label('(A) Pico 1: sensor LED driver', fontsize=13)
    d.move(0, -1)
    d += elm.Vdd().label('VBUS 5 V (pin 40)')
    d += elm.Resistor().down().label('R1 100 Ω', loc='bottom')
    d += elm.LED().down().label('LED1 5 mm white', loc='bottom')
    d += elm.Line().down(0.5)
    q = elm.NFet(bulk=False).anchor('drain').label('Q1 2N7000', loc='right', ofst=0.3)
    d += q
    d += elm.Ground().at(q.source)
    d += elm.Line().left(0.6).at(q.gate)
    d += (g := elm.Dot())
    d += elm.Resistor().left().label('R2 220 Ω')
    d += elm.Dot(open=True).label('GP15 (pin 20)', loc='left')
    d += elm.Resistor().down().at(g.center).label('R3 10 kΩ\npull-down', loc='bottom')
    d += elm.Ground()
    save(d, 'A_sensor_led.png')


def conn_diagram(title, groups, name):
    """groups: list of (module label, [(module pin, pico pin label), ...])"""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows = sum(len(g[1]) for g in groups) + 1.2 * len(groups)
    fig, ax = plt.subplots(figsize=(8.5, 0.42 * rows + 0.9))
    ax.set_axis_off()
    y = 0
    for mod, pins in groups:
        top = y
        for mp, pp in pins:
            y -= 1
            ax.plot([3.4, 6.2], [y, y], color='k', lw=1.6)
            ax.plot([6.2], [y], 'o', mfc='white', mec='k', ms=6)
            ax.text(3.25, y, mp, ha='right', va='center', fontsize=10)
            ax.text(6.45, y, pp, ha='left', va='center', fontsize=10)
        bot = y - 0.6
        ax.add_patch(plt.Rectangle((0.0, bot), 3.4, top - bot - 0.2, fill=False, lw=1.6))
        ax.text(0.85, (top + bot) / 2 - 0.1, mod, ha='center', va='center', fontsize=9.5)
        y = bot - 0.8
    ax.text(0, 0.6, title, fontsize=12, ha='left', va='bottom')
    ax.set_xlim(-0.2, 10.2); ax.set_ylim(y, 1.4)
    fig.savefig(os.path.join(HERE, name), dpi=150, bbox_inches='tight')
    plt.close(fig)


# (B) Pico 1: HM01B0 camera (female-female jumpers, no breadboard)
conn_diagram('(B) Pico 1: HM01B0 camera (female-female jumpers)', [
    ('HM01B0\nArducam B0315', [('VCC', '3V3(OUT), pin 36'), ('GND', 'GND, pin 38'),
                                ('SDA', 'GP4, pin 6'), ('SCL', 'GP5, pin 7'),
                                ('VSYNC', 'GP6, pin 9'), ('HREF', 'GP7, pin 10'),
                                ('PCLK', 'GP8, pin 11'), ('D0', 'GP9, pin 12')]),
], 'B_camera.png')

# (C) Pico 2: transmissometer (remote LED + BPW34 at opposite tank ends)
with schemdraw.Drawing(show=False) as d:
    d += elm.Label().label('(C) Pico 2: transmissometer', fontsize=13)
    d.move(0, -1)
    # LED side
    d += elm.Vdd().label('VBUS 5 V (pin 40)')
    d += elm.Resistor().down().label('R4 100 Ω', loc='bottom')
    d += elm.LED().down().label('LED2 5 mm white\n(tank end A, long wires)', loc='bottom')
    d += elm.Line().down(0.5)
    q = elm.NFet(bulk=False).anchor('drain').label('Q2 2N7000', loc='right', ofst=0.3)
    d += q
    d += elm.Ground().at(q.source)
    d += elm.Line().left(0.6).at(q.gate)
    d += (g := elm.Dot())
    d += elm.Resistor().left().label('R5 220 Ω')
    d += elm.Dot(open=True).label('GP15 (pin 20)', loc='left')
    d += elm.Resistor().down().at(g.center).label('R6 10 kΩ', loc='bottom')
    d += elm.Ground()
    # photodiode side, to the right
    d.move_from(q.drain, dx=6, dy=2.2)
    d += elm.Vdd().label('3V3 (pin 36)')
    d += elm.Photodiode().down().reverse().label('PD1 BPW34\nreverse-biased\n(tank end B)', loc='bottom')
    d += (n := elm.Dot())
    d += elm.Line().right(1.5)
    d += elm.Dot(open=True).label('GP26 / ADC0 (pin 31)', loc='right')
    d += elm.Resistor().down().at(n.center).label('R7 100 kΩ\n(47 k to 1 M)', loc='bottom')
    d += elm.Ground().label('AGND (pin 33)', loc='right')
    save(d, 'C_transmissometer.png')

# (D) Pico 2: DS18B20 + servo
conn_diagram('(D) Pico 2: water temperature and target servo', [
    ('DS18B20\nmodule\n(pull-up\non board)', [('VCC', '3V3 rail (pin 36)'), ('DAT', 'GP22, pin 29'),
                                              ('GND', 'GND rail (pin 38)')]),
    ('SG90 servo', [('orange SIG', 'GP16, pin 21'), ('red V+', '5 V rail (VBUS, pin 40)'),
                    ('brown GND', 'GND (pin 28)')]),
], 'D_temp_servo.png')

# (E) Energy measurement: low-side shunt + oscilloscope
with schemdraw.Drawing(show=False) as d:
    d += elm.Label().label('(E) Energy measurement: low-side shunt (USB unplugged)', fontsize=13)
    d.move(0, -1)
    d += (top := elm.Dot())
    d += elm.SourceV().down().reverse().label('Bench supply\n5.0 V fixed\n(QJ-3005SH III)', loc='bottom').length(3)
    d += (bot := elm.Dot())
    d += elm.Ground().label('scope probe\nground clip here', loc='right')
    d += elm.Line().right(5).at(top.center)
    load = elm.Ic(pins=[elm.IcPin(name='VSYS', side='top'), elm.IcPin(name='GND', side='bot')],
                  edgepadH=0.8, label='Pico 1 + HM01B0\n(+ LED if measured)')
    d += load.anchor('VSYS')
    d += elm.Resistor().down().at(load.GND).label('Rshunt\n1 Ω (system)\n10 to 100 Ω (camera only)', loc='bottom').length(2.5)
    d += (sh := elm.Dot())
    d += elm.Wire('-|').at(sh.center).to(bot.center)
    d += elm.Line().right(2).at(load.GND)
    d += elm.Dot(open=True).label('scope CH1 tip\nI = V / Rshunt', loc='right')
    d += elm.Label().at((1, -8.6)).label('Vload = Vsupply - Vshunt;  E = integral of Vload * I dt', fontsize=10)
    save(d, 'E_energy_shunt.png')

print('ok')
