from machine import Pin
import time

led = Pin("PA5", Pin.OUT)
button = Pin("PC13", Pin.IN, Pin.PULL_UP)

# Test 1: LED output HIGH
led.value(1)
time.sleep_ms(50)
state = led.value()
if state == 1:
    print("PASS: GPIO output HIGH")
else:
    print("FAIL: GPIO output HIGH (got {})".format(state))

# Test 2: LED output LOW
led.value(0)
time.sleep_ms(50)
state = led.value()
if state == 0:
    print("PASS: GPIO output LOW")
else:
    print("FAIL: GPIO output LOW (got {})".format(state))

# Test 3: LED toggle (manual toggle if Pin.toggle not available)
try:
    led.toggle()
    time.sleep_ms(50)
    if led.value() == 1:
        print("PASS: GPIO toggle")
    else:
        print("FAIL: GPIO toggle")
    led.value(0)
except AttributeError:
    # Pin.toggle() not available on this port — toggle manually
    led.value(0)
    time.sleep_ms(50)
    new_val = 1 - led.value()
    led.value(new_val)
    time.sleep_ms(50)
    if led.value() == new_val:
        print("PASS: GPIO manual toggle (Pin.toggle not available)")
    else:
        print("FAIL: GPIO manual toggle")
    led.value(0)

# Test 4: Button input (not pressed = HIGH due to pull-up)
val = button.value()
if val == 1:
    print("PASS: GPIO input (button not pressed = HIGH)")
else:
    print("WARN: GPIO input reads LOW - button may be pressed or wiring issue")

# Test 5: Pin info
print("LED pin: {}".format(led))
print("Button pin: {}".format(button))

print("GPIO_TEST_COMPLETE")
