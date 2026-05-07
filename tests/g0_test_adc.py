from machine import ADC, Pin
import time

# Test 1: ADC on PA0
try:
    adc0 = ADC(Pin('PA0'))
    print("PASS: ADC init on PA0")
except Exception as e:
    print("FAIL: ADC init on PA0: {}".format(e))
    print("ADC_TEST_COMPLETE")
    raise SystemExit

# Test 2: Read raw value
try:
    raw = adc0.read_u16()
    voltage = raw * 3.3 / 65535
    print("ADC PA0: raw={}, voltage={:.3f}V".format(raw, voltage))
    if 0 <= raw <= 65535:
        print("PASS: ADC read_u16 in valid range")
    else:
        print("FAIL: ADC read_u16 out of range: {}".format(raw))
except Exception as e:
    print("FAIL: ADC read_u16: {}".format(e))

# Test 3: Multiple reads for stability
try:
    readings = [adc0.read_u16() for _ in range(10)]
    avg = sum(readings) / len(readings)
    min_r = min(readings)
    max_r = max(readings)
    spread = max_r - min_r
    print("ADC 10 samples: avg={:.0f}, min={}, max={}, spread={}".format(
        avg, min_r, max_r, spread))
    if spread < 5000:
        print("PASS: ADC readings stable (spread={})".format(spread))
    else:
        print("WARN: ADC readings noisy (spread={})".format(spread))
except Exception as e:
    print("FAIL: ADC multi-read: {}".format(e))

# Test 4: Second ADC channel (PA1)
try:
    adc1 = ADC(Pin('PA1'))
    raw1 = adc1.read_u16()
    voltage1 = raw1 * 3.3 / 65535
    print("ADC PA1: raw={}, voltage={:.3f}V".format(raw1, voltage1))
    print("PASS: ADC second channel PA1")
except Exception as e:
    print("WARN: ADC PA1: {}".format(e))

# Test 5: Internal temperature sensor
try:
    adc_temp = ADC(ADC.CORE_TEMP)
    temp_raw = adc_temp.read_u16()
    print("Internal temp ADC raw: {}".format(temp_raw))
    print("PASS: ADC internal temp sensor")
except AttributeError:
    try:
        import pyb
        adc_all = pyb.ADCAll(12)
        temp = adc_all.read_core_temp()
        print("Core temp: {:.1f}C".format(temp))
        print("PASS: ADC internal temp (pyb module)")
    except Exception as e2:
        print("SKIP: Internal temp sensor not accessible: {}".format(e2))
except Exception as e:
    print("SKIP: Internal temp sensor: {}".format(e))

# Test 6: Internal VREF
try:
    adc_vref = ADC(ADC.CORE_VREF)
    vref_raw = adc_vref.read_u16()
    print("Internal VREF ADC raw: {}".format(vref_raw))
    print("PASS: ADC internal VREF")
except:
    print("SKIP: Internal VREF not accessible")

print("ADC_TEST_COMPLETE")
