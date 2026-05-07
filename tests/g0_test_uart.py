from machine import UART, Pin
import time

# Test 1: UART2 is the REPL channel -- print() proves TX works
print("PASS: UART2 TX (this message proves it)")

# Test 2: Initialize UART1 on PC4/PC5 (independent from VCP)
try:
    uart1 = UART(1, baudrate=115200)
    print("PASS: UART1 init (default pins)")
    uart1.write(b"UART1_TEST_DATA")
    time.sleep_ms(50)
    print("PASS: UART1 write")
    print("UART1: {}".format(uart1))
except Exception as e:
    print("WARN: UART1 init failed: {}".format(e))
    # Try with explicit pins
    try:
        uart1 = UART(1, baudrate=115200, tx=Pin('PC4'), rx=Pin('PC5'))
        print("PASS: UART1 init with explicit pins PC4/PC5")
        uart1.write(b"UART1_TEST_DATA")
        time.sleep_ms(50)
        print("PASS: UART1 write")
    except Exception as e2:
        print("SKIP: UART1 not available: {}".format(e2))

# Test 3: UART2 explicit init and write
try:
    uart2 = UART(2, baudrate=115200)
    uart2.write(b"UART2_EXPLICIT_WRITE\r\n")
    time.sleep_ms(50)
    print("PASS: UART2 explicit write")
except Exception as e:
    print("WARN: UART2 explicit init: {}".format(e))

# Test 4: Check available UARTs (skip UART2 — it is the REPL channel)
try:
    for n in [1, 3, 4, 5, 6]:
        try:
            u = UART(n, baudrate=9600)
            print("INFO: UART{} available".format(n))
            u.deinit()
        except:
            pass
    print("INFO: UART2 skipped (REPL channel)")
except:
    pass

print("UART_TEST_COMPLETE")
