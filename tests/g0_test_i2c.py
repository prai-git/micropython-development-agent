from machine import I2C, Pin
import time

# Test 1: I2C1 hardware init
try:
    i2c = I2C(1, freq=400000)
    print("PASS: I2C1 init at 400 kHz")
except Exception as e:
    try:
        i2c = I2C(1, scl=Pin('PB8'), sda=Pin('PB9'), freq=400000)
        print("PASS: I2C1 init with explicit pins at 400 kHz")
    except Exception as e2:
        print("FAIL: I2C1 init: {}".format(e2))
        print("I2C_TEST_COMPLETE")
        raise SystemExit

# Test 2: Bus scan
try:
    devices = i2c.scan()
    print("I2C1 scan: {} device(s) found".format(len(devices)))
    if devices:
        for addr in devices:
            print("  Device at 0x{:02X} ({})".format(addr, addr))
        print("PASS: I2C1 scan found devices")
    else:
        print("WARN: I2C1 scan found no devices (none connected)")
        print("PASS: I2C1 scan completed (bus functional)")
except Exception as e:
    print("FAIL: I2C1 scan: {}".format(e))

# Test 3: I2C write to non-existent address (should raise OSError)
try:
    i2c.writeto(0x00, b'\x00')
    print("WARN: I2C1 write to 0x00 did not raise error")
except OSError as e:
    print("PASS: I2C1 write to invalid addr raises OSError (expected)")
except Exception as e:
    print("FAIL: I2C1 unexpected error on write: {}".format(e))

# Test 4: SoftI2C fallback test
try:
    from machine import SoftI2C
    si2c = SoftI2C(scl=Pin('PB8'), sda=Pin('PB9'), freq=100000)
    devices_soft = si2c.scan()
    print("SoftI2C scan: {} device(s)".format(len(devices_soft)))
    print("PASS: SoftI2C init and scan")
except ImportError:
    print("SKIP: SoftI2C not available in this build")
except Exception as e:
    print("FAIL: SoftI2C: {}".format(e))

print("I2C_TEST_COMPLETE")
