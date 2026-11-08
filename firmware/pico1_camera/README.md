# Pico 1 camera firmware

## usb_camera.uf2 (demo)

Turns the Pico into a 160 x 120 greyscale USB webcam (UVC, "TinyUSB UVC"). Used only to check the camera wiring.
It is the unmodified `usb_camera` example of hm01b0-library-for-pico. Auto exposure is left as the library sets it,
so it is not suitable for measurements.

Built 2026-11-05 with:

| Component | Version |
|---|---|
| hm01b0-library-for-pico | f834850419392a817306b618bfb62c10f95d4b7d |
| pico-sdk | 1.5.1 |
| TinyUSB (in pico-sdk/lib/tinyusb) | 5ce60c5d207b9e7de419be6956164aebde14c3f2 (required by the example) |
| Toolchain | arm-none-eabi-gcc 13.2.1, CMake, `-DPICO_BOARD=pico` |

Rebuild:

```
git clone -b 1.5.1 https://github.com/raspberrypi/pico-sdk.git
git -C pico-sdk/lib clone https://github.com/hathach/tinyusb.git && git -C pico-sdk/lib/tinyusb checkout 5ce60c5
git clone https://github.com/ArmDeveloperEcosystem/hm01b0-library-for-pico.git
mkdir build && cd build
PICO_SDK_PATH=$PWD/../pico-sdk cmake ../hm01b0-library-for-pico -DPICO_BOARD=pico && make
# -> build/examples/usb_camera/usb_camera.uf2
```

Flash: hold BOOTSEL, plug in USB (a data cable, not charge-only), drop the .uf2 on the RPI-RP2 drive.
View: Windows Camera app or VLC (Media > Open Capture Device > DirectShow).

## Measurement firmware (to do)

Needs: fixed exposure and gain (AE off), LED pulse synchronised to the exposure, a frame counter and timestamp
per frame, frames streamed to the PC with a header, and a sleep mode between frames for the energy runs.
