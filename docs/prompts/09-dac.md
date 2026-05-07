# 09 — DAC Test

## Objective

Output a known voltage via DAC1 on PA4 and optionally cross-verify using ADC.

## Board-Specific Pin Map

| Function | Pin | Notes |
|----------|-----|-------|
| DAC1 OUT1 | PA4 | Arduino A2, CN8 pin 3 |

The STM32G0B1RE has 2 DAC channels (12-bit).

## Test Script

Generate `tests/<PREFIX>_test_dac.py`:

```python
from machine import Pin, ADC
import time

# Test 1: DAC init via pyb module
try:
    from pyb import DAC
    dac = DAC(Pin('PA4'))
    print("PASS: DAC init on PA4 (pyb.DAC)")
except ImportError:
    # pyb.DAC may not be available on G0 — try machine.DAC
    try:
        from machine import DAC
        dac = DAC(Pin('PA4'))
        print("PASS: DAC init on PA4 (machine.DAC)")
    except ImportError:
        print("FAIL: DAC not available in this MicroPython build")
        print("DAC_TEST_COMPLETE")
        raise SystemExit
    except Exception as e:
        print("FAIL: DAC init: {}".format(e))
        print("DAC_TEST_COMPLETE")
        raise SystemExit
except Exception as e:
    print("FAIL: DAC init: {}".format(e))
    print("DAC_TEST_COMPLETE")
    raise SystemExit

# Test 2: Write mid-scale value
try:
    dac.write(128)  # 8-bit mode: 0-255
    time.sleep_ms(100)
    print("PASS: DAC write 128 (mid-scale, ~1.65V expected)")
except Exception as e:
    print("FAIL: DAC write: {}".format(e))

# Test 3: Write min and max
try:
    dac.write(0)
    time.sleep_ms(50)
    print("DAC write 0 (0V)")

    dac.write(255)
    time.sleep_ms(50)
    print("DAC write 255 (~3.3V)")

    dac.write(128)
    time.sleep_ms(50)
    print("PASS: DAC min/mid/max sweep")
except Exception as e:
    print("FAIL: DAC sweep: {}".format(e))

# Test 4: Cross-verify with ADC (requires jumper wire from PA4 to PA0)
# Only run if both are available
try:
    adc = ADC(Pin('PA0'))

    # Set DAC to ~0V
    dac.write(0)
    time.sleep_ms(100)
    v_low = adc.read_u16() * 3.3 / 65535

    # Set DAC to ~1.65V
    dac.write(128)
    time.sleep_ms(100)
    v_mid = adc.read_u16() * 3.3 / 65535

    # Set DAC to ~3.3V
    dac.write(255)
    time.sleep_ms(100)
    v_high = adc.read_u16() * 3.3 / 65535

    print("DAC->ADC cross-verify: low={:.2f}V, mid={:.2f}V, high={:.2f}V".format(
        v_low, v_mid, v_high))

    if v_high > v_mid > v_low:
        print("PASS: DAC-ADC cross-verify (monotonic increase)")
    else:
        print("WARN: DAC-ADC values not monotonic (no jumper wire?)")
except Exception as e:
    print("SKIP: DAC-ADC cross-verify: {}".format(e))

print("DAC_TEST_COMPLETE")
```

## Execution

```bash
python scripts/pyboard.py --device <COM_PORT> -f cp tests/<PREFIX>_test_dac.py :
python scripts/pyboard.py --device <COM_PORT> tests/<PREFIX>_test_dac.py
```

## Verification

- **Pass**: Output contains `DAC_TEST_COMPLETE` and `PASS: DAC init`
- **Fail**: `pyb.DAC` may not be available on G0 builds. If both `pyb.DAC` and `machine.DAC` fail, mark as SKIP with note.
- **Note**: DAC-ADC cross-verify requires a jumper wire from PA4 to PA0. Without it, the cross-verify will show `WARN` — this is acceptable.

## Result Schema

```json
{ "module": "dac", "status": "PASS|FAIL|SKIP", "attempts": N, "details": "..." }
```
