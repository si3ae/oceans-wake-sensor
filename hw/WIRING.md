# Wiring

Status: design as of 2026-11-07 (rev 2: 220 Ω moved to column d; Pico 2 signal jumpers moved to column d; pictures in BB_pico1.png, BB_pico2.png). Not yet verified on hardware. Update this file whenever a wire moves, and note the date.

Rails are named by the column they sit next to: "a-side" rails run beside column a, "j-side" rails beside column j. The pictures BB_pico1.png and BB_pico2.png are drawn with column a on the right (e d c b a), as on the bench.

## Pico pin numbers

Hold the Pico with the USB port at the top. Pin 1 is top left. Pins 1 to 20 run down the left edge, pins 21 to 40 run up the right edge. The GP names are also printed on the back of the board.

Pins used here: 6 GP4, 7 GP5, 9 GP6, 10 GP7, 11 GP8, 12 GP9, 18 GND, 20 GP15, 21 GP16, 28 GND, 29 GP22, 31 GP26/ADC0, 33 AGND, 36 3V3(OUT), 38 GND, 40 VBUS (5 V, only when USB is plugged in).

Never connect 5 V (pin 40) to the camera, the DS18B20 data line, the photodiode, or any GPIO.

## Pico 1: wake sensor

### Camera (female-female jumpers, no breadboard) (schematic B)

| HM01B0 pin | Pico pin |
|---|---|
| VCC | 36 (3V3) |
| GND | 38 (GND) |
| SDA | 6 (GP4) |
| SCL | 7 (GP5) |
| VSYNC | 9 (GP6) |
| HREF | 10 (GP7) |
| PCLK | 11 (GP8) |
| D0 | 12 (GP9) |

Leave RESET and MCLK unconnected. This matches the default pins of the hm01b0-library-for-pico examples.

### Sensor LED driver (breadboard, columns a to e) (schematic A)

Rails on the a side: + = 5 V (VBUS), − = GND.

| Row | Parts |
|---|---|
| 10 | 2N7000 S at e10; male-male jumper a10 → a-side − rail |
| 11 | 2N7000 G at e11; 220 Ω from d11 to d14; 10 kΩ from c11 to a-side − rail |
| 12 | 2N7000 D at e12; LED short leg (cathode) at a12 |
| 13 | LED long leg (anode) at a13; 100 Ω from b13 to a-side + rail |
| 14 | 220 Ω (other end) at d14; Pico GP15 at a14 |

Female-male jumpers from the Pico: pin 40 (VBUS) → a-side + rail, pin 18 (GND) → a-side − rail, pin 20 (GP15) → a14.

2N7000 legs: flat face toward you, legs down, left to right = S, G, D. Check against the datasheet.

Hardware test without firmware: with the Pico on USB, move the Pico end of the a14 jumper from GP15 to the a-side + rail for a moment. The LED should light, and go off when removed.

Expected LED current is about (5 − 3.1 − 0.2) / 100 ≈ 17 mA (assumed forward voltage). At a 3.3 V gate some 2N7000 parts only partly turn on; if the LED is dim from GP15 but bright from the + rail test, swap the 2N7000 or use an IRLZ44N.

## Pico 2: environment

Pico 2 has no camera. Its 3V3 pin feeds a rail shared by the DS18B20 and the photodiode, so the DS18B20 goes through the breadboard instead of a direct female-female link.

Rails: a-side + = **3V3** (pin 36), a-side − = GND (pin 38); j-side + = **5 V** (VBUS, pin 40), j-side − = GND (pin 28). Label the rails with tape so 3V3 and 5 V are never mixed up.

### Transmissometer LED driver (schematic C, left half)

The LED itself sits at one end of the tank, on long wires (about 50 cm).

| Row | Parts |
|---|---|
| 10 | 2N7000 S at e10; male-male a10 → a-side − rail |
| 11 | 2N7000 G at e11; 220 Ω d11 to d14; 10 kΩ c11 to a-side − rail |
| 12 | 2N7000 D at e12; long wire from LED cathode at a12 |
| 13 | long wire from LED anode at a13; 100 Ω b13 to b16 |
| 14 | 220 Ω end at d14; Pico GP15 (pin 20) at a14 |
| 16 | 100 Ω end at b16; male-male a16 → j-side + rail (5 V) |

### Photodiode (BPW34) (schematic C, right half)

The photodiode sits at the opposite end of the tank, facing the LED, on long wires.

| Row | Parts |
|---|---|
| 20 | long wire from BPW34 cathode at a20; male-male b20 → a-side + rail (3V3) |
| 21 | long wire from BPW34 anode at a21; Pico GP26 (pin 31) at d21; 100 kΩ c21 to c23 |
| 23 | 100 kΩ end at c23; Pico AGND (pin 33) at a23 |

Finding the cathode: multimeter in diode mode. Red probe on the anode, black on the cathode reads about 0.3 to 0.6 V; reversed reads OL.

Choosing the load resistor: start with 100 kΩ. If the reading with the LED on is near full scale (3.0 V or more), use 47 kΩ; if it is below about 0.1 V, use 1 MΩ. Write down the value used; it changes the scale of every reading.

### DS18B20 (schematic D)

| Row | Parts |
|---|---|
| 26 | module VCC (female-male) at a26; male-male b26 → a-side + rail (3V3) |
| 27 | module DAT at a27; Pico GP22 (pin 29) at d27 |
| 28 | module GND at a28; male-male b28 → a-side − rail |

Probe wires into the module's screw terminal: red → VCC, yellow → DAT, black → GND (check the product page if colours differ).

### Target servo (SG90) (schematic D)

| Row | Parts |
|---|---|
| 30 | Pico GP16 (pin 21) at a30; male-male from d30 into the servo's orange wire |

Servo red → j-side + rail (5 V), brown → j-side − rail, with male-male jumpers pushed into the servo plug. If the Pico resets when the servo moves, power the servo from the bench supply 5 V output instead and join its ground to the Pico ground.

## Energy measurement (schematic E)

- USB must be unplugged. Power Pico 1 from the bench supply's fixed 5 V output into VSYS (pin 39) and GND.
- The shunt goes on the low side (between the board's GND and the supply's negative terminal). The scope ground clip goes on the supply negative; the probe tip on the board-side end of the shunt. A high-side shunt with the clip attached shorts the circuit through the scope's earth.
- Whole board: 1 Ω. Camera only: 10 to 100 Ω in the camera's GND wire.
- No other ground connection may bypass the shunt during a measurement (UART to another board, a USB cable, the LED supply). If one is needed, share the ground on the supply side of the shunt and note it.
- Measure the shunt's actual resistance with the multimeter and record it.
