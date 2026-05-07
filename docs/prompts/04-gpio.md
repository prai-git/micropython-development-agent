# 04 — GPIO Test

## Objective

Verify digital output (LED on PA5) and digital input (user button on PC13).

## Board-Specific Pin Map

| Function | Pin | Config |
|----------|-----|--------|
| User LED (LD4) | PA5 | Output, push-pull, active HIGH |
| User Button (B1) | PC13 | Input, active LOW, external pull-up on board |

## Test Script

Generate `tests/<PREFIX>_test_gpio.py`:

```python
from machine import Pin
import time

led = Pin("PA5", Pin.OUT)
button = Pin("PC13", Pin.IN, Pin.PULL_UP)

# Test 1: LED output HIGH
led.value(1)
time.sleep_ms(50)
state = led.value()
if state == 1:
    print("PASS: GPIO output HIGH")
else:
    print("FAIL: GPIO output HIGH (got {})".format(state))

# Test 2: LED output LOW
led.value(0)
time.sleep_ms(50)
state = led.value()
if state == 0:
    print("PASS: GPIO output LOW")
else:
    print("FAIL: GPIO output LOW (got {})".format(state))

# Test 3: LED toggle (handle ports where Pin.toggle is missing)
try:
    led.toggle()
    time.sleep_ms(50)
    if led.value() == 1:
        print("PASS: GPIO toggle")
    else:
        print("FAIL: GPIO toggle")
    led.value(0)
except AttributeError:
    led.value(0)
    time.sleep_ms(50)
    new_val = 1 - led.value()
    led.value(new_val)
    time.sleep_ms(50)
    if led.value() == new_val:
        print("PASS: GPIO manual toggle (Pin.toggle not available)")
    else:
        print("FAIL: GPIO manual toggle")
    led.value(0)

# Test 4: Button resting value sanity check
# The expected resting value depends on the board's pull configuration.
# Read button_pull and button_active from <PREFIX>_board_config.json.
# If button_pull is "none", use Pin.IN with no pull (board has external bias).
# If button_pull is "up", use Pin.IN with Pin.PULL_UP.
# Verify: resting value must be the OPPOSITE of button_active level.
# For active-low buttons: resting value must be 1.
# For active-high buttons: resting value must be 0.
val = button.value()
print("INFO: Button resting value = {}".format(val))

# Test 4a: Verify resting value is stable (read 5 times over 250ms)
stable = True
for _ in range(5):
    time.sleep_ms(50)
    if button.value() != val:
        stable = False
        break

if stable:
    print("PASS: Button resting value stable at {}".format(val))
else:
    print("FAIL: Button resting value unstable — check pull config")

# Test 4b: Verify resting value matches expected idle state
# For active-low button (pressed=0), idle must be 1
# For active-high button (pressed=1), idle must be 0
# If resting value is wrong, the pull config conflicts with board circuitry.
# Fix: try Pin.IN with no pull, or the opposite pull.
if val == 1:
    print("PASS: Button idle HIGH (consistent with active-low / external pull-up)")
elif val == 0:
    print("WARN: Button idle LOW — PULL_UP may conflict with board circuit. Try Pin.IN with no pull.")

# Test 4c: Verify button press changes value (requires user press within 5 seconds)
print("INFO: Press and HOLD B1 button within 5 seconds...")
detected = False
for _ in range(50):
    time.sleep_ms(100)
    if button.value() != val:
        detected = True
        print("PASS: Button press detected (value changed to {})".format(button.value()))
        break
if not detected:
    print("WARN: No button press detected in 5s — verify pin/pull config or press harder")

# Test 5: Pin info
print("LED pin: {}".format(led))
print("Button pin: {}".format(button))

print("GPIO_TEST_COMPLETE")
```

## Execution

```bash
python scripts/pyboard.py --device <COM_PORT> -f cp tests/<PREFIX>_test_gpio.py :
python scripts/pyboard.py --device <COM_PORT> tests/<PREFIX>_test_gpio.py
```

## Verification

- **Pass**: Output contains `GPIO_TEST_COMPLETE` AND all of:
  - At least 3 lines with `PASS:` for LED tests (HIGH, LOW, toggle)
  - `PASS: Button resting value stable` — confirms idle state is consistent
  - `PASS: Button idle HIGH` — confirms pull config matches board circuit (for active-low buttons)
  - `PASS: Button press detected` — confirms a physical press changes the pin value
- **Fail on button idle LOW**: The pull configuration conflicts with the board's external circuit. Fix: change to `Pin(BTN_PIN, Pin.IN)` with no pull. Update `button_pull` in `<PREFIX>_board_config.json` to `"none"`.
- **Fail on no press detected**: Either the pin name is wrong, the pull config is wrong, or the button is wired differently. Check `dir(Pin.board)` for correct pin names.
- **Retry strategy**: If pin name fails, try board-level names (`LED1`, `SW`) via `dir(Pin.board)`. If button idle is wrong, try no pull or opposite pull.

## Troubleshooting

- `ValueError: Pin(...) doesn't exist`: Pin name format varies by port. G0 uses `"PA5"` format, G4 uses board-level names (`"LED1"`, `"SW"`). Run `dir(Pin.board)` to discover.
- LED doesn't visually light: PA5 is shared with SPI1_SCK on Arduino header. Ensure no shield is connected.
- Button reads LOW constantly with PULL_UP: Board may have external pull-up that conflicts with internal PULL_UP on some ports. Try `Pin(BTN_PIN, Pin.IN)` with no pull.
- Button press never detected: Verify the correct pin name and that the button is active-low vs active-high for this board.

## Result Schema

```json
{ "module": "gpio", "status": "PASS|FAIL", "attempts": N, "details": "..." }
```
