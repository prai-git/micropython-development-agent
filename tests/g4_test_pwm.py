from machine import Pin, PWM
import time

# Test 1: PWM init on D12/PA6
try:
    pwm = PWM(Pin('D12'), freq=1000, duty_u16=0)
    print("PASS: PWM init on D12/PA6 at 1 kHz (machine.PWM)")
except Exception as e:
    try:
        from pyb import Timer
        pin = Pin('D12', Pin.OUT_PP)
        tim = Timer(3, freq=1000)
        ch = tim.channel(1, Timer.PWM, pin=pin)
        ch.pulse_width_percent(0)
        print("PASS: PWM init on D12 via pyb.Timer(3, ch1)")

        for duty in [0, 25, 50, 75, 100]:
            ch.pulse_width_percent(duty)
            time.sleep_ms(50)
            print("PWM duty={}%".format(duty))
        print("PASS: PWM duty sweep (pyb.Timer)")

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
try:
    for duty_pct in [0, 25, 50, 75, 100]:
        duty_val = int(duty_pct * 65535 / 100)
        pwm.duty_u16(duty_val)
        time.sleep_ms(50)
        print("PWM duty={}%".format(duty_pct))
    print("PASS: PWM duty sweep")
except Exception as e:
    print("FAIL: PWM duty sweep: {}".format(e))

try:
    pwm.duty_u16(32768)
    print("PASS: PWM at 1 kHz, 50% duty")
except Exception as e:
    print("FAIL: PWM read: {}".format(e))

try:
    pwm.freq(5000)
    pwm.duty_u16(32768)
    time.sleep_ms(50)
    print("PASS: PWM freq change to 5 kHz")
except Exception as e:
    print("FAIL: PWM freq change: {}".format(e))

try:
    pwm.deinit()
    print("PASS: PWM deinit")
except Exception as e:
    print("FAIL: PWM deinit: {}".format(e))

print("PWM_TEST_COMPLETE")
