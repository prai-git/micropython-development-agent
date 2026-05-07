from machine import WDT
import time

# Test 1: WDT init with 5-second timeout
try:
    wdt = WDT(timeout=5000)
    print("PASS: WDT init (timeout=5000ms)")
except Exception as e:
    print("FAIL: WDT init: {}".format(e))
    print("WDT_TEST_COMPLETE")
    raise SystemExit

# Test 2: Feed the watchdog multiple times
try:
    for i in range(5):
        wdt.feed()
        time.sleep_ms(500)
        print("WDT feed #{} OK".format(i + 1))
    print("PASS: WDT feed (5 feeds over 2.5 seconds, no reset)")
except Exception as e:
    print("FAIL: WDT feed: {}".format(e))

# Test 3: Feed after longer delay (within timeout)
try:
    time.sleep(3)
    wdt.feed()
    print("PASS: WDT feed after 3s delay (within 5s timeout)")
except Exception as e:
    print("FAIL: WDT feed after delay: {}".format(e))

print("WDT_TEST_COMPLETE")
