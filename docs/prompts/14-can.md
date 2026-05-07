# 14 — FDCAN Test

## Objective

Initialize FDCAN in loopback mode and verify message send/receive without requiring an external CAN transceiver or bus.

## Board-Specific Pin Map

| Function | Pin | Notes |
|----------|-----|-------|
| FDCAN1 TX | PA12 | Morpho connector (shared with I2C2 SDA) |
| FDCAN1 RX | PA11 | Morpho connector (shared with I2C2 SCL) |
| FDCAN2 TX | PB1 | Morpho connector |
| FDCAN2 RX | PB0 | Morpho connector (shared with SPI1 NSS) |

The STM32G0B1RE has 2 FDCAN interfaces supporting CAN 2.0 and CAN FD protocols.

## Test Script

Generate `tests/<PREFIX>_test_can.py`:

```python
import time

# Test 1: CAN init — try pyb.CAN first, then machine-level
can = None
use_pyb = False

try:
    from pyb import CAN
    can = CAN(1, CAN.LOOPBACK, baudrate=500000)
    print("PASS: CAN1 init in LOOPBACK mode at 500 kbps (pyb.CAN)")
    use_pyb = True
except ImportError:
    print("INFO: pyb.CAN not available, trying fdcan...")
    try:
        from machine import CAN
        can = CAN(0, mode=CAN.LOOPBACK, baudrate=500000)
        print("PASS: CAN init in LOOPBACK mode (machine.CAN)")
    except ImportError:
        print("SKIP: CAN/FDCAN not available in this MicroPython build")
        print("CAN_TEST_COMPLETE")
        raise SystemExit
    except Exception as e:
        print("FAIL: CAN init: {}".format(e))
        print("CAN_TEST_COMPLETE")
        raise SystemExit
except Exception as e:
    print("FAIL: CAN1 init: {}".format(e))
    print("CAN_TEST_COMPLETE")
    raise SystemExit

# Test 2: Send a message
try:
    test_id = 0x123
    test_data = b'\x01\x02\x03\x04\x05\x06\x07\x08'

    if use_pyb:
        can.send(test_data, test_id)
    else:
        can.send(test_id, test_data)

    print("PASS: CAN TX id=0x{:03X}, {} bytes".format(test_id, len(test_data)))
except Exception as e:
    print("FAIL: CAN TX: {}".format(e))

# Test 3: Receive the loopback message
try:
    time.sleep_ms(100)

    if use_pyb:
        # pyb.CAN.recv returns (id, rtr, fmi, data)
        msg = can.recv(0, timeout=1000)
        rx_id = msg[0]
        rx_data = msg[3]
    else:
        msg = can.recv(timeout=1000)
        rx_id = msg[0] if msg else None
        rx_data = msg[1] if msg else None

    if rx_id == test_id and rx_data == test_data:
        print("PASS: CAN loopback verified (id=0x{:03X}, data={})".format(rx_id, rx_data))
    elif rx_id == test_id:
        print("WARN: CAN loopback id match, data mismatch: {}".format(rx_data))
    else:
        print("FAIL: CAN loopback mismatch: rx_id=0x{:03X}, rx_data={}".format(
            rx_id if rx_id else 0, rx_data))
except Exception as e:
    print("FAIL: CAN RX: {}".format(e))

# Test 4: Send multiple messages
try:
    for i in range(5):
        if use_pyb:
            can.send(bytes([i]), 0x200 + i)
        else:
            can.send(0x200 + i, bytes([i]))
    print("PASS: CAN sent 5 messages (0x200-0x204)")

    # Receive them
    received = 0
    for i in range(5):
        try:
            if use_pyb:
                msg = can.recv(0, timeout=500)
            else:
                msg = can.recv(timeout=500)
            if msg:
                received += 1
        except:
            break
    print("CAN received {}/5 loopback messages".format(received))
    if received == 5:
        print("PASS: CAN multi-message loopback")
    else:
        print("WARN: CAN received only {}/5 messages".format(received))
except Exception as e:
    print("FAIL: CAN multi-message: {}".format(e))

# Cleanup
try:
    can.deinit()
    print("PASS: CAN deinit")
except:
    pass

print("CAN_TEST_COMPLETE")
```

## Execution

```bash
python scripts/pyboard.py --device <COM_PORT> -f cp tests/<PREFIX>_test_can.py :
python scripts/pyboard.py --device <COM_PORT> tests/<PREFIX>_test_can.py
```

## Verification

- **Pass**: Output contains `CAN_TEST_COMPLETE` and `PASS: CAN loopback verified`
- **Fail**: FDCAN support may require a specific MicroPython build. If `pyb.CAN` is not in the firmware, mark as SKIP.
- **Note**: Loopback mode does not require a CAN transceiver or external bus. The MCU's internal loopback routes TX back to RX.

## Result Schema

```json
{ "module": "can", "status": "PASS|FAIL|SKIP", "attempts": N, "details": "..." }
```
