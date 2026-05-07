from machine import Pin, SPI
import time

# Test 1: SPI init — try SPI(1) first, then with explicit pins
spi = None
try:
    spi = SPI(1, baudrate=1000000, polarity=0, phase=0)
    print("PASS: SPI1 init at 1 MHz")
except Exception as e:
    try:
        spi = SPI(1, baudrate=1000000, sck=Pin('SPI_SCK'), mosi=Pin('SPI_MOSI'), miso=Pin('SPI_MISO'))
        print("PASS: SPI1 init with explicit pins at 1 MHz")
    except Exception as e2:
        print("FAIL: SPI1 init: {}".format(e2))
        print("SPI_TEST_COMPLETE")
        raise SystemExit

# Test 2: SPI write
try:
    spi.write(b'\xAA\x55\x00\xFF')
    print("PASS: SPI1 write 4 bytes")
except Exception as e:
    print("FAIL: SPI1 write: {}".format(e))

# Test 3: SPI read
try:
    data = spi.read(4)
    print("SPI1 read: [{}]".format(", ".join("0x{:02X}".format(b) for b in data)))
    print("PASS: SPI1 read 4 bytes")
except Exception as e:
    print("FAIL: SPI1 read: {}".format(e))

# Test 4: SPI write_readinto (full duplex)
try:
    tx = bytearray(b'\x01\x02\x03\x04')
    rx = bytearray(4)
    spi.write_readinto(tx, rx)
    print("SPI1 write_readinto TX={} RX={}".format(
        [hex(b) for b in tx], [hex(b) for b in rx]))
    print("PASS: SPI1 full-duplex")
except Exception as e:
    print("FAIL: SPI1 full-duplex: {}".format(e))

# Test 5: Change baudrate
try:
    spi.init(baudrate=4000000, polarity=1, phase=1)
    spi.write(b'\xFF')
    print("PASS: SPI1 reinit at 4 MHz, CPOL=1 CPHA=1")
except Exception as e:
    print("FAIL: SPI1 reinit: {}".format(e))

spi.deinit()
print("PASS: SPI1 deinit")

print("SPI_TEST_COMPLETE")
