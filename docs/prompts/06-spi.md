# 06 — SPI Test

## Objective

Initialize an SPI bus and verify write functionality. Uses SPI2 to avoid conflict with the LED on PA5 (which is shared with SPI1 SCK).

## Board-Specific Pin Map

| Function | Pin | Notes |
|----------|-----|-------|
| SPI2 SCK | PB13 | Morpho CN10 pin 30 |
| SPI2 MISO | PB14 | Morpho CN10 pin 28 |
| SPI2 MOSI | PB15 | Morpho CN10 pin 26 |
| SPI2 NSS | PB12 | Morpho CN10 pin 16 |

**Note**: SPI1 (PA5/PA6/PA7) shares PA5 with the user LED — use SPI2 for conflict-free testing.

## Test Script

Generate `tests/<PREFIX>_test_spi.py`:

```python
from machine import Pin, SPI
import time

# Test 1: SPI2 init with explicit pins
try:
    spi = SPI(2, baudrate=1000000, polarity=0, phase=0)
    print("PASS: SPI2 init at 1 MHz")
except Exception as e:
    print("FAIL: SPI2 init: {}".format(e))
    print("SPI_TEST_COMPLETE")
    raise SystemExit

# Test 2: SPI write (no target device needed — just confirm no crash)
try:
    spi.write(b'\xAA\x55\x00\xFF')
    print("PASS: SPI2 write 4 bytes")
except Exception as e:
    print("FAIL: SPI2 write: {}".format(e))

# Test 3: SPI read (will read whatever is on MISO — likely 0x00 or 0xFF with no device)
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
```

## Execution

```bash
python scripts/pyboard.py --device <COM_PORT> -f cp tests/<PREFIX>_test_spi.py :
python scripts/pyboard.py --device <COM_PORT> tests/<PREFIX>_test_spi.py
```

## Verification

- **Pass**: Output contains `SPI_TEST_COMPLETE` and at least 4 `PASS:` lines
- **Fail**: If `SPI(2, ...)` fails, try with explicit pin assignment:
  ```python
  spi = SPI(2, baudrate=1000000, sck=Pin('PB13'), mosi=Pin('PB15'), miso=Pin('PB14'))
  ```
- **Retry strategy**: Fall back to SPI1 if SPI2 is not available in the MicroPython build

## Result Schema

```json
{ "module": "spi", "status": "PASS|FAIL", "attempts": N, "details": "..." }
```
