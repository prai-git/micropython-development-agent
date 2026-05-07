# 13 — External Interrupt Test

## Objective

Configure an external interrupt on the user button (PC13) and verify the interrupt handler is registered without error.

## Board-Specific Pin Map

| Function | Pin | Notes |
|----------|-----|-------|
| User Button (B1) | PC13 | Active LOW, falling edge triggers |

## Test Script

Generate `tests/<PREFIX>_test_extint.py`:

```python
from machine import Pin
import time

callback_count = 0
callback_line = -1

def button_callback(pin):
    global callback_count, callback_line
    callback_count += 1
    callback_line = pin

# Test 1: Configure ExtInt via machine.Pin.irq
try:
    button = Pin('PC13', Pin.IN, Pin.PULL_UP)
    button.irq(trigger=Pin.IRQ_FALLING, handler=button_callback)
    print("PASS: ExtInt configured on PC13 (IRQ_FALLING)")
except Exception as e:
    # Fallback: try pyb.ExtInt
    try:
        from pyb import ExtInt
        button = Pin('PC13', Pin.IN, Pin.PULL_UP)
        ext = ExtInt(button, ExtInt.IRQ_FALLING, Pin.PULL_UP, button_callback)
        print("PASS: ExtInt configured on PC13 (pyb.ExtInt)")
    except Exception as e2:
        print("FAIL: ExtInt config: machine={}, pyb={}".format(e, e2))
        print("EXTINT_TEST_COMPLETE")
        raise SystemExit

# Test 2: Verify resting value is correct for chosen pull config
resting = button.value()
print("INFO: Button resting value = {}".format(resting))
if resting == 1:
    print("PASS: Button idle HIGH (IRQ_FALLING can trigger)")
else:
    print("FAIL: Button idle LOW — IRQ_FALLING will never fire. Change pull config (try Pin.IN with no pull).")
    print("EXTINT_TEST_COMPLETE")
    raise SystemExit

# Test 3: Verify interrupt doesn't fire spontaneously
time.sleep_ms(500)
if callback_count == 0:
    print("PASS: No spurious interrupts in 500ms")
else:
    print("WARN: {} spurious interrupt(s) detected".format(callback_count))

# Test 4: Verify interrupt DOES fire on button press (5 second window)
callback_count = 0
print("INFO: Press B1 button within 5 seconds...")
detected = False
for _ in range(50):
    time.sleep_ms(100)
    if callback_count > 0:
        detected = True
        print("PASS: ExtInt triggered by button press ({} callback(s))".format(callback_count))
        break
if not detected:
    print("FAIL: No interrupt detected in 5s — button press did not trigger IRQ_FALLING")

# Test 5: Disable interrupt
try:
    button.irq(handler=None)
    print("PASS: ExtInt disabled")
except:
    try:
        ext.disable()
        print("PASS: ExtInt disabled (pyb)")
    except Exception as e:
        print("WARN: ExtInt disable: {}".format(e))

# Test 6: Verify no callbacks after disable
callback_count = 0
time.sleep_ms(500)
if callback_count == 0:
    print("PASS: No callbacks after disable")
else:
    print("FAIL: {} callback(s) after disable".format(callback_count))

print("EXTINT_TEST_COMPLETE")
```

## Execution

```bash
python scripts/pyboard.py --device <COM_PORT> -f cp tests/<PREFIX>_test_extint.py :
python scripts/pyboard.py --device <COM_PORT> tests/<PREFIX>_test_extint.py
```

## Verification

- **Pass**: Output contains `EXTINT_TEST_COMPLETE` AND all of:
  - `PASS: ExtInt configured` — IRQ registration succeeded
  - `PASS: Button idle HIGH` — resting value is correct for IRQ_FALLING to work
  - `PASS: No spurious interrupts` — no false triggers at idle
  - `PASS: ExtInt triggered by button press` — a real press fires the callback
  - `PASS: ExtInt disabled` — cleanup succeeded
  - `PASS: No callbacks after disable` — IRQ is fully removed
- **Fail on idle LOW**: The pull configuration is wrong. IRQ_FALLING requires idle HIGH. Fix: use `Pin(BTN_PIN, Pin.IN)` with no pull if board has external pull-up. Update `button_pull` in `<PREFIX>_board_config.json`.
- **Fail on no trigger**: Either the pull config is masking edges, the pin name is wrong, or the user didn't press in time. Re-run after fixing pull config.
- **Note**: Test 4 requires a physical button press within 5 seconds. The agent must wait for and parse the output, not skip it.

## Result Schema

```json
{ "module": "extint", "status": "PASS|FAIL", "attempts": N, "details": "..." }
```
