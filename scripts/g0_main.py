# main.py — NUCLEO-G0B1RE Application
# Heartbeat LED (PA5, 500ms) + Button Events (PC13 press/release)

from machine import Pin, Timer, UART
import time

uart = UART(2, baudrate=115200)
led = Pin("PA5", Pin.OUT)
button = Pin("PC13", Pin.IN, Pin.PULL_UP)

def heartbeat_cb(timer):
    led.value(1 - led.value())

heartbeat_timer = Timer(-1, freq=2, callback=heartbeat_cb)

last_button_ms = 0

def button_irq(pin):
    global last_button_ms
    now = time.ticks_ms()
    if time.ticks_diff(now, last_button_ms) < 200:
        return
    last_button_ms = now
    if pin.value() == 0:
        uart.write(b"Blue Button Pressed\r\n")

button.irq(trigger=Pin.IRQ_FALLING, handler=button_irq)

uart.write(b"\r\n=== Application Started ===\r\n")
uart.write(b"Heartbeat LED on PA5 (500ms blink)\r\n")
uart.write(b"Press/release B1 to see events\r\n\r\n")
