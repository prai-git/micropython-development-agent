# 02 — Flash MicroPython Firmware

## Objective

Download the MicroPython v1.28.0 firmware for the NUCLEO-G0B1RE and flash it via the on-board ST-Link.

## Prerequisites

- `<PREFIX>_board_config.json` exists with firmware URL
- STM32_Programmer_CLI is accessible
- Board connected on `<COM_PORT>`

## Steps

### 2.1 Download Firmware

```bash
curl -L -o firmware/NUCLEO_G0B1RE-20260406-v1.28.0.hex "https://micropython.org/resources/firmware/NUCLEO_G0B1RE-20260406-v1.28.0.hex"
```

Create `firmware/` directory first if it does not exist.

**Verification**:
```bash
ls -la firmware/NUCLEO_G0B1RE-20260406-v1.28.0.hex
```
- **Pass**: File exists and size > 100 KB
- **Fail**: Check URL, retry download

### 2.2 Erase Flash

```bash
STM32_Programmer_CLI -c port=SWD -e all
```

- **Pass**: Output contains `Mass erase successfully achieved`
- **Fail**: Check ST-Link connection, try board reset (press black reset button)

### 2.3 Flash Firmware

```bash
STM32_Programmer_CLI -c port=SWD -w firmware/NUCLEO_G0B1RE-20260406-v1.28.0.hex -v -rst
```

Flags:
- `-w`: Write
- `-v`: Verify after write
- `-rst`: Reset board after flashing

- **Pass**: Output contains `File download complete` and `Verification...OK`
- **Fail**: 
  - If verification fails: re-flash
  - If connection fails: check ST-Link, try unplugging/replugging USB
  - If file format error: ensure `.hex` file is not corrupted (re-download)

### 2.4 Wait for Board Reset

After the `-rst` flag resets the board, wait 3 seconds for MicroPython to boot and initialize the filesystem.

### 2.5 Verify Firmware via Serial

```bash
python scripts/pyboard.py --device <COM_PORT> -c "import sys; print(sys.implementation)"
```

- **Pass**: Output contains `name='micropython'` and `version=(1, 28, 0)`
- **Fail**:
  - No response: Check `<COM_PORT>` is available (close any other serial terminal)
  - Garbled output: Verify baud rate is 115200
  - `could not enter raw repl`: Board may still be booting — wait 5 seconds and retry

### 2.6 Update `<PREFIX>_board_config.json`

Set:
```json
{
  "micropython_version": "1.28.0"
}
```

## Verification Criteria

- [ ] Firmware file downloaded (size > 100 KB)
- [ ] Flash erase succeeded
- [ ] Firmware written and verified
- [ ] `sys.implementation` confirms MicroPython v1.28.0
- [ ] `<PREFIX>_board_config.json` updated with micropython_version

## Output

Board is running MicroPython v1.28.0. Proceed to `03-verify-repl.md`.
