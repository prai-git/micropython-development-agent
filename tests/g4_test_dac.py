from machine import Pin, ADC
import time

# Test 1: DAC init — G4 has full DAC support
try:
    from pyb import DAC
    dac = DAC(Pin('A2'))
    print("PASS: DAC init on A2/PA4 (pyb.DAC)")
except ImportError:
    try:
        from machine import DAC
        dac = DAC(Pin('A2'))
        print("PASS: DAC init on A2/PA4 (machine.DAC)")
    except Exception as e:
        print("FAIL: DAC not available: {}".format(e))
        print("DAC_TEST_COMPLETE")
        raise SystemExit
except Exception as e:
    print("FAIL: DAC init: {}".format(e))
    print("DAC_TEST_COMPLETE")
    raise SystemExit

# Test 2: Write mid-scale value
try:
    dac.write(128)
    time.sleep_ms(100)
    print("PASS: DAC write 128 (mid-scale, ~1.65V expected)")
except Exception as e:
    print("FAIL: DAC write: {}".format(e))

# Test 3: Sweep min/mid/max
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

# Test 4: Cross-verify with ADC (DAC on A2/PA4, ADC on A0/PA0 — needs jumper)
try:
    adc = ADC(Pin('A0'))
    dac.write(0)
    time.sleep_ms(100)
    v_low = adc.read_u16() * 3.3 / 65535
    dac.write(128)
    time.sleep_ms(100)
    v_mid = adc.read_u16() * 3.3 / 65535
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
