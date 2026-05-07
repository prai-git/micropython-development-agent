from machine import Pin
import time

callback_count = 0

def button_callback(pin):
    global callback_count
    callback_count += 1

# Test 1: Configure ExtInt via machine.Pin.irq
try:
    button = Pin('PC13', Pin.IN, Pin.PULL_UP)
    button.irq(trigger=Pin.IRQ_FALLING, handler=button_callback)
    print("PASS: ExtInt configured on PC13 (IRQ_FALLING)")
except Exception as e:
    try:
        from pyb import ExtInt
        button = Pin('PC13', Pin.IN, Pin.PULL_UP)
        ext = ExtInt(button, ExtInt.IRQ_FALLING, Pin.PULL_UP, button_callback)
        print("PASS: ExtInt configured on PC13 (pyb.ExtInt)")
    except Exception as e2:
        print("FAIL: ExtInt config: machine={}, pyb={}".format(e, e2))
        print("EXTINT_TEST_COMPLETE")
        raise SystemExit

# Test 2: Verify interrupt doesn't fire spontaneously
time.sleep_ms(500)
if callback_count == 0:
    print("PASS: No spurious interrupts in 500ms")
else:
    print("WARN: {} spurious interrupt(s) detected".format(callback_count))

# Test 3: Disable interrupt
try:
    button.irq(handler=None)
    print("PASS: ExtInt disabled")
except:
    try:
        ext.disable()
        print("PASS: ExtInt disabled (pyb)")
    except Exception as e:
        print("WARN: ExtInt disable: {}".format(e))

print("INFO: Physical button press test requires manual verification")
print("EXTINT_TEST_COMPLETE")
