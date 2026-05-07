import time

can = None
use_pyb = False

# Test 1: CAN init
try:
    from pyb import CAN
    can = CAN(1, CAN.LOOPBACK, baudrate=500000)
    can.setfilter(0, CAN.MASK, 0, (0, 0))
    print("PASS: CAN1 init in LOOPBACK mode at 500 kbps (pyb.CAN + FDCAN filter)")
    use_pyb = True
except ImportError:
    print("SKIP: CAN/FDCAN not available in this MicroPython build")
    print("CAN_TEST_COMPLETE")
    raise SystemExit
except Exception as e:
    print("FAIL: CAN1 init: {}".format(e))
    print("CAN_TEST_COMPLETE")
    raise SystemExit

# Test 2: Send a message
try:
    test_id = 0x123
    test_data = b'\x01\x02\x03\x04'
    can.send(test_data, test_id)
    print("PASS: CAN TX id=0x{:03X}, {} bytes".format(test_id, len(test_data)))
except Exception as e:
    print("FAIL: CAN TX: {}".format(e))

# Test 3: Receive the loopback message
try:
    time.sleep_ms(100)
    msg = can.recv(0, timeout=1000)
    rx_id = msg[0]
    print("CAN RX: id=0x{:03X}, rtr={}, fmi={}, data={}".format(msg[0], msg[1], msg[2], msg[3]))
    if rx_id == test_id:
        print("PASS: CAN loopback verified (id=0x{:03X})".format(rx_id))
    else:
        print("FAIL: CAN loopback id mismatch: expected 0x{:03X}, got 0x{:03X}".format(test_id, rx_id))
except Exception as e:
    print("FAIL: CAN RX: {}".format(e))

# Test 4: Multi-message loopback
try:
    for i in range(5):
        can.send(bytes([i]), 0x200 + i)
    print("PASS: CAN sent 5 messages (0x200-0x204)")

    received = 0
    for i in range(5):
        try:
            msg = can.recv(0, timeout=500)
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

try:
    can.deinit()
    print("PASS: CAN deinit")
except:
    pass

print("CAN_TEST_COMPLETE")
