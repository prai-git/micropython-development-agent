import time

# Test 1: RTC init
try:
    from pyb import RTC
    rtc = RTC()
    print("PASS: RTC init (pyb.RTC)")
    use_pyb = True
except ImportError:
    try:
        from machine import RTC
        rtc = RTC()
        print("PASS: RTC init (machine.RTC)")
        use_pyb = False
    except Exception as e:
        print("FAIL: RTC init: {}".format(e))
        print("RTC_TEST_COMPLETE")
        raise SystemExit

# Test 2: Set date/time
try:
    rtc.datetime((2026, 5, 6, 1, 14, 30, 0, 0))
    print("PASS: RTC datetime set to 2026-05-06 14:30:00")
except Exception as e:
    print("FAIL: RTC set: {}".format(e))

# Test 3: Read back
try:
    dt = rtc.datetime()
    print("RTC read: {}".format(dt))
    if dt[0] == 2026 and dt[1] == 5 and dt[2] == 6:
        print("PASS: RTC readback matches set date")
    else:
        print("FAIL: RTC readback mismatch: {}-{}-{}".format(dt[0], dt[1], dt[2]))
except Exception as e:
    print("FAIL: RTC read: {}".format(e))

# Test 4: Verify RTC advances (wait 3 seconds)
try:
    dt_before = rtc.datetime()
    sec_before = dt_before[6] if len(dt_before) > 6 else dt_before[5]
    time.sleep(3)
    dt_after = rtc.datetime()
    sec_after = dt_after[6] if len(dt_after) > 6 else dt_after[5]
    elapsed = sec_after - sec_before
    if elapsed < 0:
        elapsed += 60
    print("RTC elapsed: {} seconds (expected ~3)".format(elapsed))
    if 2 <= elapsed <= 5:
        print("PASS: RTC advanced {} seconds".format(elapsed))
    else:
        print("FAIL: RTC elapsed {} seconds".format(elapsed))
except Exception as e:
    print("FAIL: RTC advance: {}".format(e))

print("RTC_TEST_COMPLETE")
