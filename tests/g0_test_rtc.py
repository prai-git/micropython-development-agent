import time

# Test 1: RTC init
use_pyb = False
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
    except Exception as e:
        print("FAIL: RTC init: {}".format(e))
        print("RTC_TEST_COMPLETE")
        raise SystemExit

# Test 2: Set date/time
try:
    # pyb.RTC.datetime((year, month, day, weekday, hour, minute, second, subsecond))
    rtc.datetime((2026, 5, 6, 1, 14, 30, 0, 0))
    print("PASS: RTC datetime set to 2026-05-06 14:30:00")
except Exception as e:
    print("FAIL: RTC set: {}".format(e))

# Test 3: Read back immediately
try:
    dt = rtc.datetime()
    print("RTC read: {}".format(dt))
    year = dt[0]
    month = dt[1]
    day = dt[2]
    if year == 2026 and month == 5 and day == 6:
        print("PASS: RTC readback matches set date")
    else:
        print("FAIL: RTC readback mismatch: expected 2026-05-06, got {}-{}-{}".format(
            year, month, day))
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
    print("RTC before: sec={}, after: sec={}, elapsed={}".format(
        sec_before, sec_after, elapsed))
    if 2 <= elapsed <= 5:
        print("PASS: RTC advanced {} seconds (expected ~3)".format(elapsed))
    else:
        print("FAIL: RTC elapsed {} seconds (expected ~3)".format(elapsed))
except Exception as e:
    print("FAIL: RTC advance test: {}".format(e))

print("RTC_TEST_COMPLETE")
