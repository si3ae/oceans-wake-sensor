# Pico 2 environment logger (MicroPython, RP2040)
#
# Every PERIOD_MS it prints one CSV line over USB serial:
#   t_ms,temp_c,adc_on,adc_off,adc_diff,servo_deg
#   - temp_c   : DS18B20 water temperature (nan if no sensor found)
#   - adc_on   : BPW34 reading with the transmissometer LED on   (raw 0..65535, mean of N_AVG samples)
#   - adc_off  : mean of the readings just before and just after (ambient + offset)
#   - adc_diff : adc_on - adc_off  (proportional to light through the water)
# Transmittance for a turbidity step = adc_diff / adc_diff of clear water (computed on the PC).
#
# Commands (type in Thonny's shell or send from tools/log_serial.py), one per line:
#   S <deg>   move the servo to <deg> (0..180)
#   P <ms>    change the logging period (>= 1000)
#   L <0|1>   force the transmissometer LED off/on (for checking alignment); L x returns to auto
#
# Wiring: hw/WIRING.md (Pico 2). Pins: DS18B20 GP22, LED gate GP15, BPW34 ADC0 = GP26, servo GP16.

import sys
import time
import select
import machine
import onewire
import ds18x20

PIN_DS = 22
PIN_LED = 15
PIN_ADC = 26
PIN_SERVO = 16

PERIOD_MS = 2000
N_AVG = 64
SETTLE_MS = 5
DS_CONVERT_MS = 750

led = machine.Pin(PIN_LED, machine.Pin.OUT, value=0)
adc = machine.ADC(PIN_ADC)

ds = ds18x20.DS18X20(onewire.OneWire(machine.Pin(PIN_DS)))
roms = ds.scan()

servo = machine.PWM(machine.Pin(PIN_SERVO))
servo.freq(50)
servo_pos = 90
led_force = None  # None = automatic on/off cycle, 0 or 1 = forced


def servo_deg(deg):
    """SG90: 0.5 ms pulse = 0 deg, 2.5 ms = 180 deg."""
    global servo_pos
    deg = max(0, min(180, int(deg)))
    servo.duty_ns(int((500 + deg * 2000 / 180) * 1000))
    servo_pos = deg


def adc_mean(n):
    s = 0
    for _ in range(n):
        s += adc.read_u16()
    return s / n


def transmission():
    if led_force is not None:
        led.value(led_force)
        time.sleep_ms(SETTLE_MS)
        v = adc_mean(N_AVG)
        return (v, float('nan'), float('nan')) if led_force else (float('nan'), v, float('nan'))
    led.value(0); time.sleep_ms(SETTLE_MS); off1 = adc_mean(N_AVG)
    led.value(1); time.sleep_ms(SETTLE_MS); on = adc_mean(N_AVG)
    led.value(0); time.sleep_ms(SETTLE_MS); off2 = adc_mean(N_AVG)
    off = (off1 + off2) / 2
    return on, off, on - off


def handle(line):
    global PERIOD_MS, led_force
    parts = line.strip().split()
    if not parts:
        return
    cmd = parts[0].upper()
    try:
        if cmd == 'S' and len(parts) > 1:
            servo_deg(parts[1])
            print('# servo', servo_pos)
        elif cmd == 'P' and len(parts) > 1:
            PERIOD_MS = max(1000, int(parts[1]))
            print('# period_ms', PERIOD_MS)
        elif cmd == 'L' and len(parts) > 1:
            led_force = None if parts[1].lower() == 'x' else (1 if parts[1] == '1' else 0)
            print('# led_force', led_force)
        else:
            print('# unknown command:', line.strip())
    except ValueError:
        print('# bad value:', line.strip())


poll = select.poll()
poll.register(sys.stdin, select.POLLIN)

servo_deg(servo_pos)
print('# pico2_env start; ds18b20 found:', len(roms), '; n_avg', N_AVG, '; adc full scale 65535 = 3.3 V')
print('t_ms,temp_c,adc_on,adc_off,adc_diff,servo_deg')

next_t = time.ticks_ms()
while True:
    # commands
    while poll.poll(0):
        handle(sys.stdin.readline())

    now = time.ticks_ms()
    if time.ticks_diff(now, next_t) < 0:
        time.sleep_ms(10)
        continue
    next_t = time.ticks_add(next_t, PERIOD_MS)

    t0 = time.ticks_ms()
    if roms:
        ds.convert_temp()
    on, off, diff = transmission()          # done while the DS18B20 converts
    temp = float('nan')
    if roms:
        wait = DS_CONVERT_MS - time.ticks_diff(time.ticks_ms(), t0)
        if wait > 0:
            time.sleep_ms(wait)
        try:
            temp = ds.read_temp(roms[0])
        except Exception:
            temp = float('nan')
    print('%d,%.3f,%.1f,%.1f,%.1f,%d' % (t0, temp, on, off, diff, servo_pos))
