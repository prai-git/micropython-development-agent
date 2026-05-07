import time

can = None
use_pyb = False

# Test 1: CAN init
try:
    from pyb import CAN
    can = CAN(1, CAN.LOOPBACK, baudrate=500000)
    print("PASS: CAN1 init in LOOPBACK mode at 500 kbps (pyb.CAN)")
    use_pyb = True
except ImportError:
    print("INFO: pyb.CAN not available, trying alternatives...")
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
        print("FAIL: CAN loopback mismatch: rx_id={}, rx_data={}".format(rx_id, rx_data))
except Exception as e:
    print("FAIL: CAN RX: {}".format(e))

# Cleanup
try:
    can.deinit()
    print("PASS: CAN deinit")
except:
    pass

print("CAN_TEST_COMPLETE")
