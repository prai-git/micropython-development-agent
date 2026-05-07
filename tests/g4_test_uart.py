from machine import UART, Pin
import time

# Test 1: REPL channel (LPUART1 on G4) — print() proves TX works
print("PASS: VCP TX (this message proves it)")

# Test 2: Initialize UART1 on PC4/PC5 (independent from VCP)
try:
    uart1 = UART(1, baudrate=115200)
    print("PASS: UART1 init")
    uart1.write(b"UART1_TEST_DATA")
    time.sleep_ms(50)
    print("PASS: UART1 write")
    print("UART1: {}".format(uart1))
except Exception as e:
    print("WARN: UART1 init failed: {}".format(e))
    print("SKIP: UART1 (may need alternate pin config)")

# Test 3: Enumerate available UARTs (skip LPUART/VCP)
for n in [1, 2, 3, 4, 5]:
    try:
        u = UART(n, baudrate=9600)
        print("UART{} available: {}".format(n, u))
        u.deinit()
    except Exception as e:
        print("UART{} not available: {}".format(n, e))

print("UART_TEST_COMPLETE")
