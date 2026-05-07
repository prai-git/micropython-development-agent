# 18 — Application Integration

## Objective

Combine the heartbeat LED and button event detection into a unified `main.py` that runs on boot. Back up the Phase 1 demo `main.py` before replacing.

## Prerequisites

- Module 16 (heartbeat-led): PASS
- Module 17 (button-events): PASS

## Steps

1. Back up the current `main.py` on the board as `main_phase1.py` (see backup convention in `phase2-program.md`).
2. Generate application `scripts/<PREFIX>_main.py` combining heartbeat + button events.
3. Upload and reset.
4. Verify both `main_phase1.py` (backup) and `main.py` (application) exist on the board.
5. Verify heartbeat blinks and button events print on terminal.

## Application main.py

```python
from machine import Pin, Timer, UART
import time

uart = UART(2, baudrate=115200)
led = Pin("PA5", Pin.OUT)
button = Pin("PC13", Pin.IN, Pin.PULL_UP)

# Heartbeat LED — blink every 500ms via timer callback
def heartbeat_cb(timer):
    led.value(1 - led.value())

# Timer(-1) = virtual timer (works on all ports; hardware timer IDs may not be available)
heartbeat_timer = Timer(-1, freq=2, callback=heartbeat_cb)

# Button press/release detection via interrupt
def button_irq(pin):
    time.sleep_ms(20)  # debounce
    if pin.value() == 0:
        uart.write(b"Blue Button Pressed\r\n")
    else:
        uart.write(b"Blue Button Released\r\n")

button.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_irq)

uart.write(b"\r\n=== Application Started ===\r\n")
uart.write(b"Heartbeat LED on PA5 (500ms blink)\r\n")
uart.write(b"Press/release B1 to see events\r\n\r\n")
```

## Execution

```bash
# Back up Phase 1 main.py (naming convention: main_phase<N>.py)
python scripts/pyboard.py --device <COM_PORT> -c "import os; os.rename('main.py','main_phase1.py')"

# Upload new main.py
python scripts/pyboard.py --device <COM_PORT> -f cp scripts/<PREFIX>_main.py :main.py

# Reset board
STM32_Programmer_CLI -c port=SWD -rst

# Verify
python scripts/pyboard.py --device <COM_PORT> --no-soft-reset -c "print('APP_ALIVE')"
```

## Verification

- **Pass**: Board boots, LED blinks at ~500ms, pressing B1 prints "Blue Button Pressed", releasing prints "Blue Button Released"
- **Fail**: If timer or IRQ conflicts, adjust timer number or use polling loop

## Code Rules for Board Scripts

- Use `input()` for REPL user input. Never use `sys.stdin.readable()` or `sys.stdin.read()` — these are CPython APIs not available in MicroPython.
- Use ASCII only in all strings sent to the serial terminal. No Unicode characters (em dashes, smart quotes, etc.) — they render as garbage on serial consoles.

## Result Schema

```json
{ "module": "app-integration", "status": "PASS|FAIL", "attempts": N }
```
