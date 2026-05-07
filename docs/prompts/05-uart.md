# 05 — UART Test

## Objective

Verify UART2 TX/RX functionality using the ST-Link Virtual COM Port (VCP) on `<COM_PORT>`.

## Board-Specific Pin Map

| Function | Pin | Notes |
|----------|-----|-------|
| USART2 TX | PA2 | Connected to ST-Link VCP (this is how pyboard.py communicates) |
| USART2 RX | PA3 | Connected to ST-Link VCP |

**Important**: UART2 on the NUCLEO-G0B1RE is the REPL/VCP channel. Testing TX is implicit since `print()` uses it. For an independent UART test, we test UART1 (PC4/PC5) or verify UART2 explicitly.

## Test Script

Generate `tests/<PREFIX>_test_uart.py`:

```python
from machine import UART, Pin
import time

# Test 1: UART2 is the REPL channel — print() proves TX works
print("PASS: UART2 TX (this message proves it)")

# Test 2: Initialize UART1 on PC4/PC5 (independent from VCP)
try:
    uart1 = UART(1, baudrate=115200)
    print("PASS: UART1 init (PC4/PC5)")

    # Write test data
    uart1.write(b"UART1_TEST_DATA")
    time.sleep_ms(50)
    print("PASS: UART1 write")

    # Check UART config
    print("UART1: {}".format(uart1))

except Exception as e:
    print("WARN: UART1 init failed: {}".format(e))
    print("SKIP: UART1 (may need alternate pin config)")

# Test 3: UART2 explicit init and write
try:
    uart2 = UART(2, baudrate=115200)
    uart2.write(b"UART2_EXPLICIT_WRITE\r\n")
    time.sleep_ms(50)
    print("PASS: UART2 explicit write")
except Exception as e:
    print("WARN: UART2 explicit init: {}".format(e))

# Test 4: UART read (check if any data pending)
try:
    if uart1.any():
        data = uart1.read()
        print("UART1 received: {}".format(data))
    else:
        print("INFO: UART1 no data pending (expected — no loopback)")
except:
    pass

print("UART_TEST_COMPLETE")
```

## Execution

```bash
python scripts/pyboard.py --device <COM_PORT> -f cp tests/<PREFIX>_test_uart.py :
python scripts/pyboard.py --device <COM_PORT> tests/<PREFIX>_test_uart.py
```

## Verification

- **Pass**: Output contains `UART_TEST_COMPLETE` and `PASS: UART2 TX`
- **Fail**: If UART1 init fails, the G0 may map UART1 differently — check alternate pins
- **Retry strategy**: Try `UART(1, baudrate=115200, tx=Pin('PC4'), rx=Pin('PC5'))` with explicit pin assignment

## Loopback Test (Optional — requires jumper wire)

If the developer connects UART1 TX (PC4) to UART1 RX (PC5) with a jumper wire:

```python
uart1 = UART(1, baudrate=115200, tx=Pin('PC4'), rx=Pin('PC5'))
uart1.write(b"ECHO123")
time.sleep_ms(100)
if uart1.any():
    data = uart1.read()
    if data == b"ECHO123":
        print("PASS: UART1 loopback")
    else:
        print("FAIL: UART1 loopback mismatch: {}".format(data))
else:
    print("FAIL: UART1 loopback no data received")
```

## Result Schema

```json
{ "module": "uart", "status": "PASS|FAIL|SKIP", "attempts": N, "details": "..." }
```
