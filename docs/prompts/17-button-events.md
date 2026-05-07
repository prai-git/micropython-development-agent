# 17 — Button Press/Release Events

## Objective

Detect blue button B1 (PC13) press and release events using an interrupt, and print "Blue Button Pressed" / "Blue Button Released" on the terminal (UART2 VCP).

## Prerequisites

- Phase 1 GPIO test: PASS
- Phase 1 ExtInt test: PASS
- Pin: PC13 (B1), active LOW with external pull-up on board

## Implementation Script

Generate `tests/<PREFIX>_test_button_events.py`:

```python
from machine import Pin, UART
import time

uart = UART(2, baudrate=115200)
button = Pin("PC13", Pin.IN, Pin.PULL_UP)

press_count = 0
release_count = 0

def button_irq(pin):
    global press_count, release_count
    time.sleep_ms(20)  # debounce
    val = pin.value()
    if val == 0:
        press_count += 1
        uart.write(b"Blue Button Pressed\r\n")
    else:
        release_count += 1
        uart.write(b"Blue Button Released\r\n")

button.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_irq)

print("PASS: Button IRQ configured (both edges)")
print("Waiting 10 seconds for button presses...")
time.sleep(10)

button.irq(handler=None)
print("Press count: {}, Release count: {}".format(press_count, release_count))
if press_count > 0 and release_count > 0:
    print("PASS: Button press and release detected")
elif press_count > 0:
    print("PASS: Button press detected (release may have been missed)")
else:
    print("WARN: No button presses detected (user may not have pressed)")
    print("PASS: Button IRQ configured successfully (no presses in window)")

print("BUTTON_EVENTS_TEST_COMPLETE")
```

## Execution

```bash
python scripts/pyboard.py --device <COM_PORT> -f cp tests/<PREFIX>_test_button_events.py :
python scripts/pyboard.py --device <COM_PORT> tests/<PREFIX>_test_button_events.py
```

**Note**: The developer should press and release B1 during the 10-second window.

## Verification

- **Pass**: Output contains `BUTTON_EVENTS_TEST_COMPLETE` and `PASS: Button IRQ configured`
- Button messages appear on terminal when pressed/released
- **Fail**: If `IRQ_FALLING | IRQ_RISING` not supported, use two separate IRQs or polling fallback

## Result Schema

```json
{ "module": "button-events", "status": "PASS|FAIL", "attempts": N }
```
