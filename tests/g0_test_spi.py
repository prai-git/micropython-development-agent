from machine import Pin, SPI
import time

# Test 1: SPI2 init
try:
    spi = SPI(2, baudrate=1000000, polarity=0, phase=0)
    print("PASS: SPI2 init at 1 MHz")
except Exception as e:
    try:
        spi = SPI(2, baudrate=1000000, sck=Pin('PB13'), mosi=Pin('PB15'), miso=Pin('PB14'))
        print("PASS: SPI2 init with explicit pins at 1 MHz")
    except Exception as e2:
        print("FAIL: SPI2 init: {}".format(e2))
        print("SPI_TEST_COMPLETE")
        raise SystemExit

# Test 2: SPI write
try:
    spi.write(b'\xAA\x55\x00\xFF')
    print("PASS: SPI2 write 4 bytes")
except Exception as e:
    print("FAIL: SPI2 write: {}".format(e))

# Test 3: SPI read
try:
    data = spi.read(4)
    print("SPI2 read: [{}]".format(", ".join("0x{:02X}".format(b) for b in data)))
    print("PASS: SPI2 read 4 bytes")
except Exception as e:
    print("FAIL: SPI2 read: {}".format(e))

# Test 4: SPI write_readinto (full duplex)
try:
    tx = bytearray(b'\x01\x02\x03\x04')
    rx = bytearray(4)
    spi.write_readinto(tx, rx)
    print("SPI2 write_readinto TX={} RX={}".format(
        [hex(b) for b in tx], [hex(b) for b in rx]))
    print("PASS: SPI2 full-duplex")
except Exception as e:
    print("FAIL: SPI2 full-duplex: {}".format(e))

# Test 5: Change baudrate
try:
    spi.init(baudrate=4000000, polarity=1, phase=1)
    spi.write(b'\xFF')
    print("PASS: SPI2 reinit at 4 MHz, CPOL=1 CPHA=1")
except Exception as e:
    print("FAIL: SPI2 reinit: {}".format(e))

spi.deinit()
print("PASS: SPI2 deinit")

print("SPI_TEST_COMPLETE")
