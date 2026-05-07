# 10 — PWM / Timer Test

## Objective

Generate a PWM signal using a hardware timer and verify duty cycle changes.

## Board-Specific Pin Map

| Function | Pin | Notes |
|----------|-----|-------|
| PWM output | PA6 | Arduino D12, TIM3_CH1 or TIM16_CH1 |
| Alt PWM | PA7 | Arduino D11, TIM3_CH2 |

## Test Script

Generate `tests/<PREFIX>_test_pwm.py`:

```python
from machine import Pin, PWM
import time

# Test 1: PWM init on PA6
try:
    pwm = PWM(Pin('PA6'), freq=1000, duty_u16=0)
    print("PASS: PWM init on PA6 at 1 kHz (machine.PWM)")
except Exception as e:
    # Fallback to pyb.Timer approach
    try:
        from pyb import Timer
        pin = Pin('PA6', Pin.OUT_PP)
        tim = Timer(3, freq=1000)
        ch = tim.channel(1, Timer.PWM, pin=pin)
        ch.pulse_width_percent(0)
        print("PASS: PWM init on PA6 via pyb.Timer(3, ch1)")

        # Use timer-based API for remaining tests
        # Test 2: Duty cycle sweep
        for duty in [0, 25, 50, 75, 100]:
            ch.pulse_width_percent(duty)
            time.sleep_ms(50)
            print("PWM duty={}%".format(duty))
        print("PASS: PWM duty sweep (pyb.Timer)")

        ch.pulse_width_percent(50)
        print("PASS: PWM at 1 kHz, 50% duty")

        # Test 3: Frequency change
        tim.freq(5000)
        ch.pulse_width_percent(50)
        time.sleep_ms(50)
        print("PASS: PWM freq change to 5 kHz")

        tim.deinit()
        print("PASS: Timer deinit")
        print("PWM_TEST_COMPLETE")
        raise SystemExit

    except Exception as e2:
        print("FAIL: PWM init: machine.PWM={}, pyb.Timer={}".format(e, e2))
        print("PWM_TEST_COMPLETE")
        raise SystemExit

# machine.PWM path
# Test 2: Duty cycle sweep
try:
    for duty_pct in [0, 25, 50, 75, 100]:
        duty_val = int(duty_pct * 65535 / 100)
        pwm.duty_u16(duty_val)
        time.sleep_ms(50)
        print("PWM duty={}% (duty_u16={})".format(duty_pct, duty_val))
    print("PASS: PWM duty sweep")
except Exception as e:
    print("FAIL: PWM duty sweep: {}".format(e))

# Test 3: Set 50% duty at 1 kHz
try:
    pwm.duty_u16(32768)
    actual_freq = pwm.freq()
    print("PWM freq={} Hz, duty=50%".format(actual_freq))
    print("PASS: PWM at {} Hz, 50% duty".format(actual_freq))
except Exception as e:
    print("FAIL: PWM read freq: {}".format(e))

# Test 4: Change frequency
try:
    pwm.freq(5000)
    pwm.duty_u16(32768)
    time.sleep_ms(50)
    print("PASS: PWM freq change to 5 kHz")
except Exception as e:
    print("FAIL: PWM freq change: {}".format(e))

# Test 5: Deinit
try:
    pwm.deinit()
    print("PASS: PWM deinit")
except Exception as e:
    print("FAIL: PWM deinit: {}".format(e))

print("PWM_TEST_COMPLETE")
```

## Execution

```bash
python scripts/pyboard.py --device <COM_PORT> -f cp tests/<PREFIX>_test_pwm.py :
python scripts/pyboard.py --device <COM_PORT> tests/<PREFIX>_test_pwm.py
```

## Verification

- **Pass**: Output contains `PWM_TEST_COMPLETE` and at least 3 `PASS:` lines
- **Fail**: Timer/channel mapping may differ. On G0, TIM3_CH1 maps to PA6. Try `Timer(16, freq=1000)` as alternative.
- **Retry strategy**: If PA6 doesn't work with Timer 3, enumerate available timers and channels

## Visual Verification (Optional)

With an oscilloscope or logic analyzer on PA6:
- 1 kHz, 50% duty = 500us HIGH, 500us LOW
- 5 kHz, 50% duty = 100us HIGH, 100us LOW

## Result Schema

```json
{ "module": "pwm", "status": "PASS|FAIL", "attempts": N, "details": "..." }
```
