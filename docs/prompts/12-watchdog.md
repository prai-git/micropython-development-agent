# 12 — Watchdog Timer Test

## Objective

Verify the independent watchdog timer (IWDG) can be initialized and fed to prevent reset.

## Important

**Do NOT test watchdog expiry in an automated script.** A WDT timeout resets the MCU, which disconnects the pyboard.py session and may require re-entering the REPL. Only test the "feed" path.

## Test Script

Generate `tests/<PREFIX>_test_wdt.py`:

```python
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

# Test 3: Feed again after longer delay (but within timeout)
try:
    time.sleep(3)
    wdt.feed()
    print("PASS: WDT feed after 3s delay (within 5s timeout)")
except Exception as e:
    print("FAIL: WDT feed after delay: {}".format(e))

# NOTE: WDT cannot be stopped once started on STM32.
# The board will reset if no feed occurs within 5 seconds from here.
# Remaining script execution should complete well within that window.

print("WDT_TEST_COMPLETE")
```

## Execution

```bash
python scripts/pyboard.py --device <COM_PORT> -f cp tests/<PREFIX>_test_wdt.py :
python scripts/pyboard.py --device <COM_PORT> tests/<PREFIX>_test_wdt.py
```

## Verification

- **Pass**: Output contains `WDT_TEST_COMPLETE` and `PASS: WDT feed`
- **Fail**: If `machine.WDT` is not available, mark as SKIP
- **Warning**: After this test, the WDT is active and cannot be disabled. The board will reset if idle for >5 seconds. A power cycle or reset clears it.

## Post-Test Cleanup

After the WDT test completes, the agent should immediately proceed or reset the board:
```bash
python scripts/pyboard.py --device <COM_PORT> -c "import machine; machine.reset()"
```

Wait 3 seconds for reboot, then continue.

## Result Schema

```json
{ "module": "watchdog", "status": "PASS|FAIL|SKIP", "attempts": N, "details": "..." }
```
