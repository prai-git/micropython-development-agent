# 15 — Integration Test

## Objective

Generate a unified `<PREFIX>_main.py` that provides a UART menu for all peripherals that passed testing, upload it (as `main.py` on the board) along with `boot.py`, and verify the board boots into the menu.

## Prerequisites

- All peripheral modules (04-14) have been executed
- `<PREFIX>_test_results.json` exists with per-module results
- `<PREFIX>_board_config.json` has the complete pin map

## Steps

### 15.1 Read Test Results

Parse `<PREFIX>_test_results.json` to determine which peripherals passed. Only include passing peripherals in the menu.

### 15.2 Generate boot.py

Create `scripts/boot.py`:

```python
# boot.py -- run on boot to configure USB and filesystem
import machine
import pyb
```

### 15.3 Generate `<PREFIX>_main.py`

Create `scripts/<PREFIX>_main.py` using the pin map from `<PREFIX>_board_config.json` and the pass/fail results from `<PREFIX>_test_results.json`.

The generated `main.py` must follow this structure:

```python
from machine import Pin, UART, ADC, I2C, SPI
import time

# Board: NUCLEO-G0B1RE (STM32G0B1RET6)
# Auto-generated from test results

uart = UART(2, baudrate=115200)

def uart_print(msg):
    uart.write(msg.encode() if isinstance(msg, str) else msg)
    uart.write(b"\r\n")

# --- Peripheral demos (only for PASS modules) ---

def demo_gpio():
    led = Pin(LED_PIN, Pin.OUT)
    button = Pin(BTN_PIN, Pin.IN, Pin.PULL_UP)
    pressed = False
    def btn_irq(pin):
        nonlocal pressed
        time.sleep_ms(20)
        if pin.value() == 0:
            pressed = True
    button.irq(trigger=Pin.IRQ_FALLING, handler=btn_irq)
    uart_print("LED blink + button detect. Ctrl+C to stop.")
    try:
        while True:
            led.value(1 - led.value())
            if pressed:
                uart_print("Button pressed!")
                pressed = False
            time.sleep(0.5)
    finally:
        button.irq(handler=None)

def demo_uart_echo():
    uart_print("UART echo mode. Ctrl+C to stop.")
    line = b""
    while True:
        if uart.any():
            char = uart.read(1)
            if char in (b'\r', b'\n'):
                if line:
                    uart.write(b"Echo: " + line + b"\r\n")
                    line = b""
            else:
                line += char
        time.sleep_ms(10)

def demo_spi():
    spi = SPI(2, baudrate=1000000)
    tx = bytearray(b'\xAA\x55\x00\xFF')
    rx = bytearray(4)
    spi.write_readinto(tx, rx)
    uart_print("SPI2 TX={} RX={}".format(
        [hex(b) for b in tx], [hex(b) for b in rx]))
    spi.deinit()

def demo_i2c():
    i2c = I2C(1, freq=400000)
    devices = i2c.scan()
    uart_print("I2C1 scan: {} device(s)".format(len(devices)))
    for addr in devices:
        uart_print("  0x{:02X}".format(addr))

def demo_adc():
    adc = ADC(Pin('PA0'))
    uart_print("ADC continuous read on PA0. Ctrl+C to stop.")
    while True:
        raw = adc.read_u16()
        voltage = raw * 3.3 / 65535
        uart_print("ADC: raw={}, V={:.3f}".format(raw, voltage))
        time.sleep(0.5)

def demo_dac():
    try:
        from pyb import DAC
        dac = DAC(Pin('PA4'))
    except:
        from machine import DAC
        dac = DAC(Pin('PA4'))
    uart_print("DAC sweep on PA4...")
    for val in range(0, 256, 16):
        dac.write(val)
        uart_print("DAC={} (~{:.2f}V)".format(val, val * 3.3 / 255))
        time.sleep(0.2)
    uart_print("DAC sweep complete")

def demo_pwm():
    try:
        from machine import PWM
        pwm = PWM(Pin('PA6'), freq=1000, duty_u16=32768)
    except:
        from pyb import Timer
        tim = Timer(3, freq=1000)
        ch = tim.channel(1, Timer.PWM, pin=Pin('PA6', Pin.OUT_PP))
        ch.pulse_width_percent(50)
    uart_print("PWM on PA6: 1 kHz, 50% duty")
    time.sleep(2)
    uart_print("PWM demo complete")

def demo_rtc():
    try:
        from pyb import RTC
    except:
        from machine import RTC
    rtc = RTC()
    dt = rtc.datetime()
    uart_print("RTC: {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        dt[0], dt[1], dt[2], dt[4], dt[5], dt[6]))

# --- Menu ---

MENU_ITEMS = [
    # (key, label, function)
    # Only include peripherals that PASSED testing
]
# This list will be populated based on test_results.json

def menu():
    uart_print("")
    uart_print("=== MicroPython Demo ===")
    uart_print("Select a peripheral to test:")
    for key, label, _ in MENU_ITEMS:
        uart_print("  {}: {}".format(key, label))
    uart_print("  q: Quit")
    return input("Choice: ")

while True:
    ch = menu()
    if ch == 'q':
        uart_print("Goodbye!")
        break
    matched = False
    for key, label, func in MENU_ITEMS:
        if ch == key:
            matched = True
            try:
                func()
            except KeyboardInterrupt:
                uart_print("\r\nStopped.")
            break
    if not matched:
        uart_print("Invalid choice.")
```

**The agent must populate `MENU_ITEMS`** based on `<PREFIX>_test_results.json`. Example for all-pass:

```python
MENU_ITEMS = [
    ("1", "GPIO - LED blink + button", demo_gpio),
    ("2", "UART - Echo mode", demo_uart_echo),
    ("3", "SPI - Write/Read test", demo_spi),
    ("4", "I2C - Bus scan", demo_i2c),
    ("5", "ADC - Analog read (PA0)", demo_adc),
    ("6", "DAC - Voltage sweep (PA4)", demo_dac),
    ("7", "PWM - 1 kHz on PA6", demo_pwm),
    ("8", "RTC - Read date/time", demo_rtc),
]
```

### 15.4 Upload Files

Before uploading, back up any existing `main.py` on the board. If no `main.py` exists yet (first-time flash), skip the backup.

```bash
# Back up existing main.py if present (ignore error if file doesn't exist)
python scripts/pyboard.py --device <COM_PORT> -c "import os; os.rename('main.py','main_pre_phase1.py')"

# Upload Phase 1 files
python scripts/pyboard.py --device <COM_PORT> -f cp scripts/boot.py :
python scripts/pyboard.py --device <COM_PORT> -f cp scripts/<PREFIX>_main.py :main.py
```

### 15.5 Verify Files on Board

```bash
python scripts/pyboard.py --device <COM_PORT> -f ls :
```

- **Pass**: Both `boot.py` and `main.py` appear in listing (note: `scripts/<PREFIX>_main.py` is uploaded as `main.py` on the board)

### 15.6 Reset and Verify Menu

```bash
python scripts/pyboard.py --device <COM_PORT> -c "import machine; machine.reset()"
```

Wait 3 seconds, then:

```bash
python scripts/pyboard.py --device <COM_PORT> --no-soft-reset -c "print('BOARD_ALIVE')"
```

- **Pass**: `BOARD_ALIVE` appears — board booted successfully with new main.py

### 15.7 Verify Interactive Input

After confirming the board is alive, verify that the menu accepts input without errors. Connect to the board REPL and confirm:
1. The menu displays with no encoding errors (use ASCII only — no Unicode em dashes or special characters in menu strings)
2. The `input()` call blocks and accepts a keystroke
3. Selecting a valid menu item runs the demo
4. Pressing `q` exits cleanly

**Important**: Use `input()` for REPL user input. Never use `sys.stdin.readable()` or `sys.stdin.read()` — these are CPython APIs not available in MicroPython.

### 15.8 Final Report

Print the summary table from `<PREFIX>_test_results.json`:

```
=== MicroPython Peripheral Test Report ===
Board: NUCLEO-G0B1RE (STM32G0B1RET6)
Firmware: MicroPython v1.28.0
Date: 2026-05-06

Module          Status    Attempts  Notes
------          ------    --------  -----
GPIO            PASS      1
UART            PASS      1
SPI             PASS      1
I2C             PASS      1
ADC             PASS      1
DAC             PASS      1
PWM/Timer       PASS      1
RTC             PASS      1
Watchdog        PASS      1
ExtInt          PASS      1
FDCAN           PASS      1

Result: XX/11 PASS, XX FAIL, XX SKIP

main.py uploaded with X peripheral demos.
Board is ready for use.
```

## Verification Criteria

- [ ] `boot.py` and `<PREFIX>_main.py` (as `main.py`) uploaded to board filesystem
- [ ] Board resets and boots without error
- [ ] Menu displays with ASCII-only characters (no encoding errors on serial terminal)
- [ ] `input()` accepts user input without crashing
- [ ] GPIO demo: LED blinks AND button press prints message (both behaviors required)
- [ ] At least one other demo runs without error when selected
- [ ] `q` exits the menu cleanly
- [ ] Final report printed with per-module results
- [ ] `<PREFIX>_test_results.json` contains all module results

### Behavioral verification rules

Each demo must be verified for **correct behavior**, not just **absence of errors**:
- A demo that runs without crashing but produces wrong output is a **FAIL**
- A button test that always prints "pressed" regardless of button state is a **FAIL** (false positive)
- A button test that never prints "pressed" even when button is held is a **FAIL**
- Output that contains garbled characters (Unicode on serial terminal) is a **FAIL**

### Code rules for generated scripts

- Use `input()` for REPL user input — never `sys.stdin.readable()` or `sys.stdin.read()`
- Use ASCII only in all strings — no Unicode em dashes, smart quotes, or special characters
- Use `led.value(1 - led.value())` for LED toggle — never `led.toggle()` (not available on all ports)
- Use IRQ-based button detection with debounce — never bare polling in a slow loop
- Read `button_pull` from `<PREFIX>_board_config.json` — never hardcode `Pin.PULL_UP`

## Output

Development complete. Board is running MicroPython with a menu-driven peripheral demo.
