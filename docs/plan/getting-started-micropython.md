# Getting Started with MicroPython on STM32

## Purpose

This document is a **master plan** for enabling MicroPython on supported STM32 boards through automated, agent-driven development. The plan is organized into two phases:

- **Phase 1 — Board Bring-Up**: Firmware flashing, REPL verification, and peripheral-by-peripheral hardware validation. Orchestrated by `phase1-program.md` and its sub-prompts (`01-setup-environment.md` through `15-integration-test.md`). Phase 1 is board-generic — it works for any supported STM32 board using `<PREFIX>_board_config.json` for pin mappings and peripheral availability.

- **Phase 2 — Application Development**: Once Phase 1 confirms the board is operational, the developer provides an application specification (as a prompt or `.md` file). Phase 2 is orchestrated by `phase2-program.md`, which generates application-specific sub-prompts (`16-xxx.md`, `17-xxx.md`, etc.) that build on the verified peripheral foundation from Phase 1. Phase 2 sub-prompts follow the same naming convention (incrementing numbers) and the same do-verify-retry loop pattern.

The separation ensures that board bring-up is always reusable and repeatable, while application logic is layered on top without modifying the Phase 1 prompts.

## Multi-Board Naming Convention

This project supports multiple STM32 boards simultaneously. To prevent board-specific files from being overwritten or deleted when switching boards, **all board-specific files use a family prefix**:

| Board | Family | Prefix | Example Files |
|-------|--------|--------|---------------|
| NUCLEO-G0B1RE | G0 | `g0_` | `g0_board_config.json`, `g0_test_results.json`, `g0_test_gpio.py`, `g0_main.py` |
| NUCLEO-G474RE | G4 | `g4_` | `g4_board_config.json`, `g4_test_results.json`, `g4_test_gpio.py`, `g4_main.py` |

The prefix is derived from the MCU family: **G0** → `g0_`, **G4** → `g4_`, **F4** → `f4_`, etc.

### Prefix Rules

- **Config files** (project root): `<PREFIX>_board_config.json`, `<PREFIX>_test_results.json`
- **Test scripts** (`tests/`): `<PREFIX>_test_<module>.py` (e.g., `g4_test_gpio.py`)
- **Application scripts** (`scripts/`): `<PREFIX>_main.py` (e.g., `g4_main.py`)
- **Firmware** (`firmware/`): Board-specific firmware files coexist (named by board, no prefix needed)
- **Shared files**: `scripts/pyboard.py`, `scripts/boot.py`, and all `docs/` files are shared across boards — do not prefix these.

When the agent runs Phase 1 or Phase 2 for a board, it must:
1. Determine the board prefix from the board's MCU family in lowercase (e.g., `NUCLEO_G474RE` → family `G4` → prefix `g4_`).
2. Use `<PREFIX>_board_config.json` and `<PREFIX>_test_results.json` for that board's state.
3. Name all generated test scripts as `<PREFIX>_test_<module>.py`.
4. Name the application script as `<PREFIX>_main.py`.
5. **Never overwrite or delete** files belonging to another board's prefix.

---

## Scope

### Supported STM32 Families and Reference Boards

| Family | Core | Reference Board(s) | Flash / RAM | Notes |
|--------|------|---------------------|-------------|-------|
| **F0** | Cortex-M0 @ 48 MHz | Nucleo F091RC | 256 KB / 32 KB | Entry-level, limited peripherals |
| **F4** | Cortex-M4F @ 168 MHz | Nucleo F401RE, F411RE, F446RE, Discovery F4, F429I | 256–2048 KB / 64–256 KB | Most common target, full peripheral set |
| **F7** | Cortex-M7 @ 216 MHz | Nucleo F746ZG, F767ZI, Discovery F7, F769I | 512–2048 KB / 256–512 KB | High performance, DMA2D, LCD |
| **G0** | Cortex-M0+ @ 64 MHz | Nucleo G0B1RE | 512 KB / 144 KB | Modern low-cost, good peripheral set |
| **G4** | Cortex-M4F @ 170 MHz | Nucleo G474RE | 512 KB / 128 KB | Mixed-signal, CORDIC, FMAC |
| **H5** | Cortex-M33 @ 250 MHz | Nucleo H563ZI | 2048 KB / 640 KB | Security features, TrustZone |
| **H7** | Cortex-M7 @ 480 MHz | Nucleo H743ZI, H723ZG, Discovery H747I | 1–2048 KB / 1 MB+ | Dual-core (H747), highest performance |
| **L0** | Cortex-M0+ @ 32 MHz | Nucleo L073RZ | 192 KB / 20 KB | Ultra-low-power |
| **L1** | Cortex-M3 @ 32 MHz | Nucleo L152RE | 512 KB / 80 KB | Low-power with LCD driver |
| **L4** | Cortex-M4F @ 80 MHz | Nucleo L476RG, L432KC, Discovery L476, B-L475E-IOT01A | 256–1024 KB / 96–320 KB | Low-power + performance balance |
| **WB** | Cortex-M4F + M0+ @ 64 MHz | Nucleo WB55, USBDONGLE_WB55 | 1024 KB / 256 KB | BLE 5.0 + IEEE 802.15.4 |
| **WL** | Cortex-M4 + M0+ @ 48 MHz | Nucleo WL55 | 256 KB / 64 KB | Sub-GHz radio (LoRa) |

### Peripheral Modules to Test

Each board will be tested against these peripheral categories (availability depends on the specific MCU):

| # | Module | MicroPython Class | Description |
|---|--------|-------------------|-------------|
| 1 | GPIO | `machine.Pin`, `pyb.Pin` | Digital input/output, push-pull/open-drain |
| 2 | UART | `machine.UART`, `pyb.UART` | Async serial TX/RX |
| 3 | SPI | `machine.SPI`, `pyb.SPI` | SPI controller mode |
| 4 | I2C | `machine.I2C`, `machine.SoftI2C` | I2C controller, bus scan |
| 5 | ADC | `machine.ADC`, `pyb.ADC` | Analog-to-digital conversion |
| 6 | DAC | `pyb.DAC` | Digital-to-analog (F4/F7/H7/L4 only) |
| 7 | PWM/Timer | `pyb.Timer` | Timer-based PWM output |
| 8 | RTC | `pyb.RTC` | Real-time clock set/read |
| 9 | Watchdog | `machine.WDT` | Independent watchdog |
| 10 | ExtInt | `pyb.ExtInt` | External interrupt on pin edge |
| 11 | CAN | `pyb.CAN` | CAN bus (where available) |
| 12 | I2S | `machine.I2S` | Audio interface (where available) |

---

## Workflow Overview

```
Developer provides:
  1. Supported STM32 board (connected via ST-Link or on-board debugger)
  2. Board datasheet (PDF) or board name (agent can web-search)
  3. COM port / device path

PHASE 1 — Board Bring-Up (generic, reusable):

Developer triggers:
  phase1-program.md  -->  01-setup-environment.md
                          02-flash-firmware.md
                          03-verify-repl.md
                          04-gpio.md
                          05-uart.md
                          06-spi.md
                          07-i2c.md
                          08-adc.md
                          09-dac.md
                          10-pwm-timer.md
                          11-rtc.md
                          12-watchdog.md
                          13-extint.md
                          14-can.md
                          15-integration-test.md

  Output: <PREFIX>_board_config.json, <PREFIX>_test_results.json, <PREFIX>_main.py with peripheral menu

PHASE 2 — Application Development (user-specific):

Developer provides application specification (prompt or .md file), then triggers:
  phase2-program.md  -->  16-<app-module>.md    (auto-generated from spec)
                          17-<app-module>.md
                          18-<app-module>.md
                          ...
                          NN-app-integration.md

  Output: Application-specific scripts uploaded to board
```

Each sub-prompt in both phases follows a **do-verify loop**: execute a step, then run a verification check. If verification fails, the agent diagnoses and retries before moving to the next module.

---

## Phase 1: Board Bring-Up

Phase 1 is orchestrated by `phase1-program.md`. It is entirely generic — the same prompts work for any supported STM32 board. Board-specific details (pin maps, peripheral availability, firmware URL) are resolved at runtime via `<PREFIX>_board_config.json` (see Multi-Board Naming Convention above).

### Phase 1 Sub-Sections

#### Environment and Firmware

### 01-setup-environment.md

**Objective**: Ensure all host-side tools are installed and the board is detected.

**Steps**:
1. Verify Python 3.x is installed on the host.
2. Install `pyserial`: `pip install pyserial`
3. Confirm `pyboard.py` is present in the repo working directory.
4. Detect the board's COM port (Windows) or `/dev/ttyACMx` (Linux/Mac).
5. Parse the user-supplied datasheet to extract: MCU part number, flash size, RAM size, pin count, available peripherals.

**Verification**:
```
python -c "import serial; print(serial.VERSION)"
python pyboard.py --device <COMx> -c "print('hello')"
```
- **Pass**: "hello" is printed back from the board (board already has MicroPython), OR connection error indicates firmware needs flashing (proceed to 02).
- **Fail**: COM port not found — prompt user to check cable/driver.

**Agent output**: A `<PREFIX>_board_config.json` file containing extracted MCU info (e.g., `g4_board_config.json` for G4 family):
```json
{
  "mcu": "STM32F411RE",
  "family": "F4",
  "flash_kb": 512,
  "ram_kb": 128,
  "com_port": "COM3",
  "peripherals": ["GPIO", "UART", "SPI", "I2C", "ADC", "DAC", "PWM", "RTC", "CAN"],
  "pin_map": {}
}
```

### 02-flash-firmware.md

**Objective**: Download and flash the correct MicroPython firmware onto the board.

**Steps**:
1. From `<PREFIX>_board_config.json`, determine the MCU family and board name.
2. Download the appropriate `.dfu` or `.hex` firmware from `https://micropython.org/download/` for the identified board.
3. Flash using one of:
   - **DFU mode** (USB): `python -m dfu --device <USB_ID> firmware.dfu` (requires `pydfu.py` or `dfu-util`)
   - **ST-Link**: Use `STM32_Programmer_CLI` (from STM32CubeProgrammer):
     ```
     STM32_Programmer_CLI -c port=SWD -w firmware.hex -v -rst
     ```
   - **pyboard.py mass-erase + flash** (if board is already in DFU mode)
4. Reset the board after flashing.

**Verification**:
```
python pyboard.py --device <COMx> -c "import sys; print(sys.implementation)"
```
- **Pass**: Output contains `(name='micropython', version=(1, 2x, 0), ...)`.
- **Fail**: No response or garbled output — retry flash, check baud rate (115200).

### 03-verify-repl.md

**Objective**: Confirm REPL access and basic MicroPython functionality.

**Steps**:
1. Open serial connection at 115200 baud.
2. Send soft-reset (Ctrl+D) and confirm `MicroPython vX.XX.X on YYYY-MM-DD; <BOARD> with STM32Fxxx` banner appears.
3. Execute basic expressions via `pyboard.py`:
   ```
   python pyboard.py --device <COMx> -c "print(2+2)"
   python pyboard.py --device <COMx> -c "import machine; print(machine.freq())"
   python pyboard.py --device <COMx> -c "import os; print(os.listdir('/'))"
   ```
4. Upload and retrieve a test file:
   ```
   python pyboard.py --device <COMx> -f cp test_hello.py :
   python pyboard.py --device <COMx> -f cat :test_hello.py
   ```

**Verification**:
- **Pass**: All four commands return expected values; file round-trips correctly.
- **Fail**: Diagnose — check COM port, baud rate, firmware version.

**Agent output**: Update `<PREFIX>_board_config.json` with `"micropython_version"` and `"filesystem_ok": true`.

---

#### Peripheral Modules

Each module below follows a common pattern:

```
1. Read <PREFIX>_board_config.json to determine if the peripheral is available.
2. Read the datasheet to identify the correct pins for this peripheral.
3. Generate a test script (e.g., <PREFIX>_test_gpio.py) in the tests/ folder.
4. Upload via pyboard.py.
5. Execute and capture output.
6. Parse output for PASS/FAIL markers.
7. If FAIL: diagnose, adjust pin mapping, retry (max 3 attempts).
8. Log result to <PREFIX>_test_results.json.
```

### 04-gpio.md

**Objective**: Verify digital output and input on at least 2 pins.

**Datasheet dependency**: LED pin (e.g., PA5 on Nucleo boards), user button pin (e.g., PC13).

**Test script** (`<PREFIX>_test_gpio.py`):
```python
from machine import Pin
import time

led = Pin("<LED_PIN>", Pin.OUT)
button = Pin("<BUTTON_PIN>", Pin.IN, Pin.PULL_UP)

# Test output
led.value(1)
time.sleep(0.1)
assert led.value() == 1, "FAIL: LED did not go HIGH"
led.value(0)
assert led.value() == 0, "FAIL: LED did not go LOW"
print("PASS: GPIO output")

# Test input (read button state — expect HIGH when not pressed due to PULL_UP)
val = button.value()
assert val == 1, "FAIL: Button pin not HIGH with PULL_UP (got {})".format(val)
print("PASS: GPIO input")
print("GPIO_TEST_COMPLETE")
```

**Verification**: Output contains `GPIO_TEST_COMPLETE` and both `PASS` markers.

### 05-uart.md

**Objective**: Verify UART TX/RX using the ST-Link VCP (Virtual COM Port).

**Datasheet dependency**: UART instance connected to ST-Link (typically UART2 on Nucleo boards), TX/RX pins.

**Test script** (`<PREFIX>_test_uart.py`):
```python
from machine import UART
import time

uart = UART(<UART_NUM>, baudrate=115200)
test_msg = b"UART_LOOPBACK_TEST_1234"
uart.write(test_msg)
time.sleep(0.1)
print("PASS: UART TX")

# Echo test (agent reads from host side)
uart.write(b"UART_TEST_COMPLETE\r\n")
```

**Verification**: Host-side `pyboard.py` captures `UART_TEST_COMPLETE` in output.

**Advanced** (if TX/RX loopback jumper is available):
```python
uart.write(b"ECHO")
time.sleep(0.1)
if uart.any():
    data = uart.read()
    assert data == b"ECHO", "FAIL: loopback mismatch"
    print("PASS: UART loopback")
```

### 06-spi.md

**Objective**: Initialize SPI bus and perform a write/read cycle.

**Datasheet dependency**: SPI instance number, SCK/MOSI/MISO pins.

**Test script** (`<PREFIX>_test_spi.py`):
```python
from machine import Pin, SPI

spi = SPI(<SPI_NUM>, baudrate=1000000, polarity=0, phase=0,
          sck=Pin("<SCK_PIN>"), mosi=Pin("<MOSI_PIN>"), miso=Pin("<MISO_PIN>"))
print("PASS: SPI init, baudrate={}".format(spi.init))

# Write test (no target device needed — just confirm no crash)
spi.write(b'\x00\xFF')
print("PASS: SPI write")

# If a device is connected, attempt read
data = spi.read(1)
print("SPI read byte: 0x{:02X}".format(data[0]))
print("SPI_TEST_COMPLETE")
```

**Verification**: Output contains `SPI_TEST_COMPLETE`.

### 07-i2c.md

**Objective**: Initialize I2C and scan for connected devices.

**Datasheet dependency**: I2C instance, SDA/SCL pins.

**Test script** (`<PREFIX>_test_i2c.py`):
```python
from machine import I2C, Pin

i2c = I2C(<I2C_NUM>, scl=Pin("<SCL_PIN>"), sda=Pin("<SDA_PIN>"), freq=400000)
devices = i2c.scan()
print("I2C devices found: {}".format([hex(d) for d in devices]))

if len(devices) > 0:
    print("PASS: I2C scan found {} device(s)".format(len(devices)))
else:
    print("WARN: No I2C devices found (none connected?)")

print("PASS: I2C init")
print("I2C_TEST_COMPLETE")
```

**Verification**: Output contains `I2C_TEST_COMPLETE` and `PASS: I2C init`.

### 08-adc.md

**Objective**: Read analog voltage from a pin and the internal temperature sensor.

**Datasheet dependency**: ADC-capable pin, ADC resolution (12-bit typical).

**Test script** (`<PREFIX>_test_adc.py`):
```python
from machine import ADC, Pin

adc = ADC(Pin("<ADC_PIN>"))
raw = adc.read_u16()
voltage = raw * 3.3 / 65535
print("ADC raw={}, voltage={:.3f}V".format(raw, voltage))
assert 0 <= voltage <= 3.3, "FAIL: voltage out of range"
print("PASS: ADC read")

# Internal temp sensor (pyb module)
try:
    import pyb
    adc_temp = pyb.ADCAll(12)
    temp = adc_temp.read_core_temp()
    print("Core temp: {:.1f}C".format(temp))
    assert 10 < temp < 80, "FAIL: temp out of expected range"
    print("PASS: ADC internal temp")
except Exception as e:
    print("SKIP: Internal temp not available ({})".format(e))

print("ADC_TEST_COMPLETE")
```

**Verification**: Output contains `ADC_TEST_COMPLETE` and at least one `PASS`.

### 09-dac.md

**Objective**: Output a known voltage via DAC and optionally verify with ADC.

**Availability**: F4, F7, H7, L4 families only. Skip for F0, G0, G4, L0, L1, WB, WL.

**Datasheet dependency**: DAC output pin (typically PA4 or PA5).

**Test script** (`<PREFIX>_test_dac.py`):
```python
from pyb import DAC, ADC, Pin

dac = DAC(Pin("<DAC_PIN>"))
dac.write(128)  # Mid-scale (8-bit mode)
print("PASS: DAC write 128")

# Self-verify: if DAC pin is also ADC-capable or jumpered to an ADC pin
try:
    adc = ADC(Pin("<VERIFY_ADC_PIN>"))
    val = adc.read()
    expected_v = (128 / 255) * 3.3
    actual_v = val * 3.3 / 4095
    print("DAC expected ~{:.2f}V, ADC read {:.2f}V".format(expected_v, actual_v))
    if abs(expected_v - actual_v) < 0.3:
        print("PASS: DAC-ADC cross-verify")
    else:
        print("WARN: DAC-ADC delta > 0.3V")
except:
    print("SKIP: DAC-ADC cross-verify (no ADC available on verify pin)")

print("DAC_TEST_COMPLETE")
```

### 10-pwm-timer.md

**Objective**: Generate a PWM signal on a timer channel.

**Datasheet dependency**: Timer number, channel, output pin.

**Test script** (`<PREFIX>_test_pwm.py`):
```python
from pyb import Timer, Pin

pin = Pin("<PWM_PIN>", Pin.OUT_PP)
tim = Timer(<TIMER_NUM>, freq=1000)
ch = tim.channel(<CHANNEL_NUM>, Timer.PWM, pin=pin)

# Sweep duty cycle
for duty in [0, 25, 50, 75, 100]:
    ch.pulse_width_percent(duty)
    print("PWM duty={}%".format(duty))

ch.pulse_width_percent(50)
print("PASS: PWM at 1kHz, 50% duty")
print("PWM_TEST_COMPLETE")
```

### 11-rtc.md

**Objective**: Set and read the real-time clock.

**Test script** (`<PREFIX>_test_rtc.py`):
```python
from pyb import RTC
import time

rtc = RTC()
rtc.datetime((2026, 5, 6, 1, 12, 0, 0, 0))
time.sleep(2)
dt = rtc.datetime()
print("RTC: {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*dt[:3], dt[4], dt[5], dt[6]))
assert dt[6] >= 2, "FAIL: RTC did not advance"
print("PASS: RTC set/read")
print("RTC_TEST_COMPLETE")
```

### 12-watchdog.md

**Objective**: Verify the independent watchdog timer triggers a reset.

**Test script** (`<PREFIX>_test_wdt.py`):
```python
from machine import WDT
import time

# Test 1: Feed the watchdog — board should NOT reset
wdt = WDT(timeout=5000)
wdt.feed()
time.sleep(1)
wdt.feed()
print("PASS: WDT feed (no reset)")
print("WDT_TEST_COMPLETE")
# NOTE: Do NOT test WDT expiry in automated scripts — it resets the board
#       and breaks the pyboard.py session. Manual-only test.
```

### 13-extint.md

**Objective**: Configure an external interrupt on the user button.

**Datasheet dependency**: Button pin, expected edge (falling for active-low).

**Test script** (`<PREFIX>_test_extint.py`):
```python
from pyb import Pin, ExtInt
import time

triggered = False

def callback(line):
    global triggered
    triggered = True
    print("ExtInt triggered on line {}".format(line))

pin = Pin("<BUTTON_PIN>", Pin.IN, Pin.PULL_UP)
ext = ExtInt(pin, ExtInt.IRQ_FALLING, Pin.PULL_UP, callback)

print("ExtInt configured. Simulating via pin toggle...")

# Self-test: use a second pin jumpered to button pin, or test config only
print("PASS: ExtInt configured without error")
print("EXTINT_TEST_COMPLETE")
# NOTE: Physical button press verification requires user interaction.
#       Agent logs this as PASS (config) + MANUAL (trigger).
```

### 14-can.md

**Objective**: Initialize CAN bus (where hardware is available).

**Availability**: F4 (F446, F429, etc.), G4, H7, WL. Skip for F0, L0, L1, WB.

**Datasheet dependency**: CAN instance, TX/RX pins.

**Test script** (`<PREFIX>_test_can.py`):
```python
from pyb import CAN

can = CAN(1, CAN.LOOPBACK, baudrate=500000)
can.send(b'\x01\x02\x03', 0x123)
msg = can.recv(0, timeout=1000)
print("CAN TX id=0x123, RX id=0x{:03X} data={}".format(msg[0], msg[3]))
assert msg[0] == 0x123 and msg[3] == b'\x01\x02\x03', "FAIL: CAN loopback mismatch"
print("PASS: CAN loopback")
print("CAN_TEST_COMPLETE")
```

---

#### Integration

### 15-integration-test.md

**Objective**: Generate a unified `<PREFIX>_main.py` that provides a menu-driven interface to all verified peripherals.

**Steps**:
1. Read `<PREFIX>_test_results.json` to determine which peripherals passed.
2. Generate `<PREFIX>_main.py` under `scripts/` with:
   - Board-specific pin mappings from `<PREFIX>_board_config.json`.
   - A UART menu listing all passing peripherals.
   - Each menu option runs the corresponding peripheral demo in a `try/except KeyboardInterrupt` block.
3. Upload `<PREFIX>_main.py` as `main.py` on the board, along with `boot.py`.
4. Reset and verify the menu appears over UART.

**Verification**:
```
python pyboard.py --device <COMx> --no-soft-reset -c "import os; print(os.listdir('/'))"
```
Confirm `main.py` and `boot.py` are on the filesystem.

Reset board and confirm menu banner over serial.

---

## Prompt File Structure

```
prompts/
  phase1-program.md         # Phase 1 orchestrator — board bring-up
  01-setup-environment.md
  02-flash-firmware.md
  03-verify-repl.md
  04-gpio.md
  05-uart.md
  06-spi.md
  07-i2c.md
  08-adc.md
  09-dac.md
  10-pwm-timer.md
  11-rtc.md
  12-watchdog.md
  13-extint.md
  14-can.md
  15-integration-test.md
  phase2-program.md         # Phase 2 orchestrator — application development
  16-<app-module>.md        # Generated at runtime from application spec
  17-<app-module>.md
  ...
  changelog.md              # Deviations and prompt updates log
```

### phase1-program.md Behavior

`phase1-program.md` is the Phase 1 entry point. It must:

1. **Accept inputs**: board datasheet (PDF path or URL), COM port, board name (optional — auto-detect).
2. **Execute sub-prompts sequentially**: `01` through `15`.
3. **Maintain state** via `<PREFIX>_board_config.json` and `<PREFIX>_test_results.json` in the working directory.
4. **Skip inapplicable modules**: e.g., skip `09-dac.md` for STM32F0, skip `14-can.md` for boards without CAN.
5. **Verification loop per module**:
   ```
   for each module:
     attempt = 0
     while attempt < 3:
       run module
       if verify() == PASS:
         log PASS to <PREFIX>_test_results.json
         break
       else:
         attempt += 1
         diagnose and adjust (pin map, init params)
     if attempt == 3:
       log FAIL to <PREFIX>_test_results.json
       continue to next module
   ```
6. **Final report**: Print summary table of PASS/FAIL/SKIP per peripheral.
7. **Hand off**: Inform the developer that Phase 1 is complete and they can proceed to `phase2-program.md` for application-specific development.

### phase2-program.md Behavior

`phase2-program.md` is the Phase 2 entry point. It must:

1. **Verify Phase 1 completion**: Check that `<PREFIX>_test_results.json` exists and has passing results for the peripherals needed by the application.
2. **Accept application specification**: The developer provides a spec as either:
   - An inline prompt describing the application requirements, OR
   - A path to an `.md` file containing the application specification.
3. **Decompose the spec into sub-prompts**: Parse the application requirements and generate numbered sub-prompt files (`16-xxx.md`, `17-xxx.md`, etc.) under `docs/prompts/`. Each sub-prompt addresses one feature or module of the application.
4. **Execute sub-prompts sequentially**: Starting from `16`, each sub-prompt follows the same do-verify-retry pattern as Phase 1.
5. **Final integration**: The last generated sub-prompt produces the application's `<PREFIX>_main.py`, uploads it as `main.py` on the board, and verifies it runs correctly.
6. **Log all changes**: Record any deviations or prompt updates in `changelog.md`.

### Sub-prompt Contract

Each sub-prompt (`NN-module.md`) must:

- Read `<PREFIX>_board_config.json` for MCU-specific parameters.
- Accept the datasheet PDF path for pin/peripheral lookup.
- Generate a self-contained test script (`<PREFIX>_test_<module>.py`) in the `tests/` folder.
- Upload and execute the script via `pyboard.py`.
- Parse stdout for `PASS`, `FAIL`, `WARN`, `SKIP` markers.
- Return a structured result: `{ "module": "<name>", "status": "PASS|FAIL|SKIP", "details": "..." }`.

---

## State Files

All state files use the board family prefix (see Multi-Board Naming Convention above).

### <PREFIX>_board_config.json

Created by `01-setup-environment.md`, updated by subsequent modules (e.g., `g0_board_config.json`, `g4_board_config.json`):

```json
{
  "mcu": "STM32F411RE",
  "family": "F4",
  "flash_kb": 512,
  "ram_kb": 128,
  "com_port": "COM3",
  "micropython_version": "1.28.0",
  "peripherals": ["GPIO", "UART", "SPI", "I2C", "ADC", "DAC", "PWM", "RTC", "WDT", "ExtInt", "CAN"],
  "pin_map": {
    "led": "PA5",
    "button": "PC13",
    "uart_tx": "PA2",
    "uart_rx": "PA3",
    "uart_num": 2,
    "spi_num": 1,
    "spi_sck": "PA5",
    "spi_mosi": "PA7",
    "spi_miso": "PA6",
    "i2c_num": 1,
    "i2c_scl": "PB6",
    "i2c_sda": "PB7",
    "adc_pin": "PA0",
    "dac_pin": "PA4",
    "pwm_pin": "PA8",
    "pwm_timer": 1,
    "pwm_channel": 1,
    "can_tx": "PB9",
    "can_rx": "PB8"
  },
  "filesystem_ok": true
}
```

### <PREFIX>_test_results.json

Accumulated as each module completes (e.g., `g0_test_results.json`, `g4_test_results.json`):

```json
{
  "board": "NUCLEO_F411RE",
  "timestamp": "2026-05-06T12:00:00",
  "results": [
    { "module": "gpio", "status": "PASS", "attempts": 1 },
    { "module": "uart", "status": "PASS", "attempts": 1 },
    { "module": "spi", "status": "PASS", "attempts": 2 },
    { "module": "i2c", "status": "PASS", "attempts": 1 },
    { "module": "adc", "status": "PASS", "attempts": 1 },
    { "module": "dac", "status": "PASS", "attempts": 1 },
    { "module": "pwm", "status": "PASS", "attempts": 1 },
    { "module": "rtc", "status": "PASS", "attempts": 1 },
    { "module": "wdt", "status": "PASS", "attempts": 1 },
    { "module": "extint", "status": "PASS", "attempts": 1 },
    { "module": "can", "status": "SKIP", "attempts": 0, "reason": "No CAN on F411" }
  ]
}
```

---

## Family-Specific Notes

### Peripheral Availability Matrix

| Peripheral | F0 | F4 | F7 | G0 | G4 | H5 | H7 | L0 | L1 | L4 | WB | WL |
|------------|----|----|----|----|----|----|----|----|----|----|----|----|
| GPIO       | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  |
| UART       | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  |
| SPI        | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  |
| I2C        | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  |
| ADC        | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  |
| DAC        | -  | Y  | Y  | -  | Y  | Y  | Y  | Y  | Y  | Y  | -  | Y  |
| PWM/Timer  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  |
| RTC        | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  |
| WDT        | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  |
| ExtInt     | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  | Y  |
| CAN        | -  | *  | Y  | -  | Y  | Y  | Y  | -  | -  | -  | -  | -  |
| I2S        | -  | Y  | Y  | -  | -  | -  | Y  | -  | -  | -  | -  | -  |
| BLE        | -  | -  | -  | -  | -  | -  | -  | -  | -  | -  | Y  | -  |
| Sub-GHz    | -  | -  | -  | -  | -  | -  | -  | -  | -  | -  | -  | Y  |

`*` = available on some variants (e.g., F446 has CAN, F401 does not)

### API Differences by Family

- **F0 / G0 / L0**: Use `machine` module primarily. The `pyb` module has limited support. DAC is not available.
- **F4 / F7 / H7**: Full `pyb` module support. Use `pyb.Pin`, `pyb.ADC`, `pyb.DAC`, `pyb.Timer`, `pyb.CAN`.
- **L4**: `pyb` module available. DAC available. Low-power modes accessible via `machine.lightsleep()` / `machine.deepsleep()`.
- **WB**: BLE stack runs on the M0+ core. MicroPython runs on M4. BLE configuration is via `pyb` or custom firmware.
- **WL**: Sub-GHz radio requires custom MicroPython build or frozen modules.

### Flashing Method by Board Type

| Board Type | Method | Tool |
|------------|--------|------|
| Nucleo (any) | ST-Link SWD (on-board) | `STM32_Programmer_CLI -c port=SWD` |
| Discovery (any) | ST-Link SWD (on-board) | `STM32_Programmer_CLI -c port=SWD` |
| Generic board + ST-Link | External ST-Link SWD | `STM32_Programmer_CLI -c port=SWD` |
| USB DFU capable | USB DFU mode | `dfu-util -a 0 -D firmware.dfu` or `pydfu.py` |

---

## Phase 2: Application Development

Phase 2 begins after Phase 1 has validated the board and peripherals. It is orchestrated by `phase2-program.md`.

### Inputs

The developer provides an **application specification** — either as a text prompt or as a standalone `.md` file. The spec should describe:

- What the application does (functional requirements)
- Which peripherals it uses (the agent cross-references `<PREFIX>_test_results.json` to confirm they passed Phase 1)
- Any external hardware or sensors connected to the board
- Communication protocols or data formats required
- Timing, sampling rates, or real-time constraints
- Success criteria for verification

### How Phase 2 Sub-Prompts Are Generated

`phase2-program.md` decomposes the application specification into discrete, testable modules. Each module becomes a numbered sub-prompt file:

```
16-<first-app-module>.md
17-<second-app-module>.md
...
NN-app-integration.md       (final integration and upload)
```

Numbering continues from 16 (after Phase 1's `15-integration-test.md`) to maintain a single linear sequence across both phases.

### Sub-Prompt Contract (Phase 2)

Phase 2 sub-prompts follow the same contract as Phase 1:

- Read `<PREFIX>_board_config.json` for pin mappings and MCU parameters.
- Read `<PREFIX>_test_results.json` to confirm required peripherals are available.
- Generate a self-contained script for the module (named `<PREFIX>_test_<module>.py`).
- Upload and execute via `pyboard.py`.
- Parse stdout for `PASS`, `FAIL`, `WARN`, `SKIP` markers.
- Log results to `<PREFIX>_test_results.json` (appended under a `phase2_results` key).
- Follow the do-verify-retry loop (max 3 attempts per module).

### State Files (Phase 2 additions)

Phase 2 appends to the existing state files:

**`<PREFIX>_test_results.json`** gains a `phase2_results` array:
```json
{
  "board": "NUCLEO_G0B1RE",
  "results": [ ... Phase 1 results ... ],
  "phase2_results": [
    { "module": "sensor-read", "status": "PASS", "attempts": 1 },
    { "module": "data-logging", "status": "PASS", "attempts": 2 },
    { "module": "app-integration", "status": "PASS", "attempts": 1 }
  ],
  "application": {
    "name": "Temperature Logger",
    "spec_file": "docs/app-spec.md",
    "modules_generated": ["16-sensor-read.md", "17-data-logging.md", "18-app-integration.md"]
  }
}
```

### Example Phase 2 Flow

```
Developer: "I want a temperature logger that reads an I2C sensor every 5 seconds,
            stores readings in flash, and outputs CSV over UART when a button is pressed."

phase2-program.md generates:
  16-sensor-driver.md       — I2C driver for the specific temp sensor
  17-flash-storage.md       — File-based storage on the MicroPython filesystem
  18-csv-output.md          — CSV formatting and UART output on button press
  19-app-integration.md     — Unified main.py combining all modules, upload, verify
```
