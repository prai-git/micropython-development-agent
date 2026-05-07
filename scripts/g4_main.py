# g4_main.py - NUCLEO-G474RE MicroPython Demo
# Auto-generated from Phase 1 test results

from machine import Pin, UART, ADC, I2C, SPI, PWM
import time

led = Pin('LED1', Pin.OUT)
button = Pin('SW', Pin.IN)

def uart_print(msg):
    print(msg)

def demo_gpio():
    pressed = False
    def btn_irq(pin):
        nonlocal pressed
        time.sleep_ms(20)
        if pin.value() == 0:
            pressed = True
    button.irq(trigger=Pin.IRQ_FALLING, handler=btn_irq)
    uart_print("LED blink + button detect. Ctrl+C to stop.")
    try:
        while True:
            led.value(1 - led.value())
            if pressed:
                uart_print("Button pressed!")
                pressed = False
            time.sleep(0.5)
    finally:
        button.irq(handler=None)

def demo_spi():
    spi = SPI(1, baudrate=1000000)
    tx = bytearray(b'\xAA\x55\x00\xFF')
    rx = bytearray(4)
    spi.write_readinto(tx, rx)
    uart_print("SPI1 TX={} RX={}".format(
        [hex(b) for b in tx], [hex(b) for b in rx]))
    spi.deinit()

def demo_i2c():
    i2c = I2C(1, freq=400000)
    devices = i2c.scan()
    uart_print("I2C1 scan: {} device(s)".format(len(devices)))
    for addr in devices:
        uart_print("  0x{:02X}".format(addr))

def demo_adc():
    adc = ADC(Pin('A0'))
    uart_print("ADC continuous read on A0. Ctrl+C to stop.")
    while True:
        raw = adc.read_u16()
        voltage = raw * 3.3 / 65535
        uart_print("ADC: raw={}, V={:.3f}".format(raw, voltage))
        time.sleep(0.5)

def demo_dac():
    try:
        from pyb import DAC
        dac = DAC(Pin('A2'))
    except:
        from machine import DAC
        dac = DAC(Pin('A2'))
    uart_print("DAC sweep on A2/PA4...")
    for val in range(0, 256, 16):
        dac.write(val)
        uart_print("DAC={} (~{:.2f}V)".format(val, val * 3.3 / 255))
        time.sleep(0.2)
    uart_print("DAC sweep complete")

def demo_pwm():
    pwm = PWM(Pin('D12'), freq=1000, duty_u16=32768)
    uart_print("PWM on D12/PA6: 1 kHz, 50% duty")
    time.sleep(2)
    pwm.deinit()
    uart_print("PWM demo complete")

def demo_rtc():
    try:
        from pyb import RTC
    except:
        from machine import RTC
    rtc = RTC()
    dt = rtc.datetime()
    uart_print("RTC: {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        dt[0], dt[1], dt[2], dt[4], dt[5], dt[6]))

def demo_can():
    from pyb import CAN
    can = CAN(1, CAN.LOOPBACK, baudrate=500000)
    can.setfilter(0, CAN.MASK, 0, (0, 0))
    can.send(b'\x01\x02\x03\x04', 0x123)
    time.sleep_ms(100)
    try:
        msg = can.recv(0, timeout=1000)
        uart_print("CAN loopback: id=0x{:03X}".format(msg[0]))
    except:
        uart_print("CAN loopback timeout")
    can.deinit()

MENU_ITEMS = [
    ("1", "GPIO - LED blink + button", demo_gpio),
    ("2", "SPI - Write/Read test", demo_spi),
    ("3", "I2C - Bus scan", demo_i2c),
    ("4", "ADC - Analog read (A0)", demo_adc),
    ("5", "DAC - Voltage sweep (A2)", demo_dac),
    ("6", "PWM - 1 kHz on D12/PA6", demo_pwm),
    ("7", "RTC - Read date/time", demo_rtc),
    ("8", "CAN - FDCAN loopback", demo_can),
]

def menu():
    uart_print("")
    uart_print("=== NUCLEO-G474RE MicroPython Demo ===")
    uart_print("Select a peripheral to test:")
    for key, label, _ in MENU_ITEMS:
        uart_print("  {}: {}".format(key, label))
    uart_print("  q: Quit")
    return input("Choice: ")

while True:
    ch = menu()
    if ch == 'q':
        uart_print("Goodbye!")
        break
    matched = False
    for key, label, func in MENU_ITEMS:
        if ch == key:
            matched = True
            try:
                func()
            except KeyboardInterrupt:
                uart_print("\r\nStopped.")
            break
    if not matched:
        uart_print("Invalid choice.")
