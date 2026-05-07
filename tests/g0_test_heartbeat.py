from machine import Pin, Timer

led = Pin("PA5", Pin.OUT)

blink_count = 0

def heartbeat_cb(timer):
    global blink_count
    led.value(1 - led.value())
    blink_count += 1

tim = Timer(-1, freq=2, callback=heartbeat_cb)

import time
time.sleep(5)
tim.deinit()
led.value(0)

print("Blink toggles in 5s: {}".format(blink_count))
if 8 <= blink_count <= 12:
    print("PASS: Heartbeat LED blinked ~{} times (expected ~10)".format(blink_count))
else:
    print("WARN: Blink count {} outside expected range 8-12".format(blink_count))
print("HEARTBEAT_TEST_COMPLETE")
