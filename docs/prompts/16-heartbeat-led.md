# 16 — Heartbeat LED

## Objective

Blink LED LD4 (PA5) every 500ms using a timer callback so it runs non-blocking in the background.

## Prerequisites

- Phase 1 GPIO test: PASS
- Pin: PA5 (LD4), active HIGH

## Implementation Script

Generate `tests/<PREFIX>_test_heartbeat.py`:

```python
from machine import Pin, Timer

led = Pin("PA5", Pin.OUT)

def heartbeat_cb(timer):
    led.value(1 - led.value())

blink_count = 0

def heartbeat_cb(timer):
    global blink_count
    led.value(1 - led.value())
    blink_count += 1

# Timer(-1) = virtual timer (works on all ports; hardware timer IDs may not be available)
tim = Timer(-1, freq=2, callback=heartbeat_cb)

import time
time.sleep(5)
tim.deinit()
led.value(0)

print("Blink toggles in 5s: {}".format(blink_count))
if 8 <= blink_count <= 12:
    print("PASS: Heartbeat LED blinked ~{} times (expected ~10)".format(blink_count))
else:
    print("WARN: Blink count {} outside expected range 8-12".format(blink_count))
print("HEARTBEAT_TEST_COMPLETE")
```

## Execution

```bash
python scripts/pyboard.py --device <COM_PORT> -f cp tests/<PREFIX>_test_heartbeat.py :
python scripts/pyboard.py --device <COM_PORT> tests/<PREFIX>_test_heartbeat.py
```

## Verification

- **Pass**: Output contains `HEARTBEAT_TEST_COMPLETE` and LED was visibly blinking
- **Fail**: If `Timer(-1)` raises an error, try a hardware timer ID (e.g., `Timer(1)`). Some ports only support virtual timers, others only hardware timers.

## Result Schema

```json
{ "module": "heartbeat-led", "status": "PASS|FAIL", "attempts": N }
```
