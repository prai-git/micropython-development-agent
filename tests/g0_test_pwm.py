from machine import Pin
import time

# Try machine.PWM first, then pyb.Timer
pwm = None

try:
    from machine import PWM
    pwm = PWM(Pin('PA6'), freq=1000, duty_u16=0)
    print("PASS: PWM init on PA6 at 1 kHz (machine.PWM)")

    # Duty cycle sweep
    for duty_pct in [0, 25, 50, 75, 100]:
        duty_val = int(duty_pct * 65535 / 100)
        pwm.duty_u16(duty_val)
        time.sleep_ms(50)
        print("PWM duty={}% (duty_u16={})".format(duty_pct, duty_val))
    print("PASS: PWM duty sweep")

    # Set 50% at 1 kHz
    pwm.duty_u16(32768)
    print("PASS: PWM at 1 kHz, 50% duty")

    # Change frequency
    pwm.freq(5000)
    pwm.duty_u16(32768)
    time.sleep_ms(50)
    print("PASS: PWM freq change to 5 kHz")

    pwm.deinit()
    print("PASS: PWM deinit")

except Exception as e:
    print("INFO: machine.PWM failed ({}), trying pyb.Timer...".format(e))
    try:
        from pyb import Timer
        pin = Pin('PA6', Pin.OUT_PP)
        tim = Timer(3, freq=1000)
        ch = tim.channel(1, Timer.PWM, pin=pin)
        ch.pulse_width_percent(0)
        print("PASS: PWM init on PA6 via pyb.Timer(3, ch1)")

        for duty in [0, 25, 50, 75, 100]:
            ch.pulse_width_percent(duty)
            time.sleep_ms(50)
            print("PWM duty={}%".format(duty))
        print("PASS: PWM duty sweep (pyb.Timer)")

        ch.pulse_width_percent(50)
        print("PASS: PWM at 1 kHz, 50% duty")

        tim.freq(5000)
        ch.pulse_width_percent(50)
        time.sleep_ms(50)
        print("PASS: PWM freq change to 5 kHz")

        tim.deinit()
        print("PASS: Timer deinit")
    except Exception as e2:
        print("FAIL: PWM init: machine.PWM={}, pyb.Timer={}".format(e, e2))

print("PWM_TEST_COMPLETE")
