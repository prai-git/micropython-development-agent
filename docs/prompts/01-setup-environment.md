# 01 — Setup Environment

## Objective

Verify all host-side tools are installed, the board is detected on `<COM_PORT>`, and create the `<PREFIX>_board_config.json` state file.

**Naming convention**: `<PREFIX>` is derived from the MCU family in lowercase. For NUCLEO-G0B1RE (G0 family) the prefix is `g0_`. For NUCLEO-G474RE (G4 family) the prefix is `g4_`.

## Prerequisites

- Python 3.x installed on the host
- Target board connected via USB (provides ST-Link SWD + Virtual COM Port)
- STM32CubeProgrammer installed (provides `STM32_Programmer_CLI`)

## Steps

### 1.1 Verify Python

```bash
python --version
```
- **Pass**: Python 3.8+
- **Fail**: Install Python 3.x

### 1.2 Install pyserial

```bash
python -m pip install pyserial
```

Verify:
```bash
python -c "import serial; print(serial.VERSION)"
```
- **Pass**: Version string printed (e.g., `3.5`)

### 1.3 Locate pyboard.py

Check if `pyboard.py` exists at the expected path. If not, download from the MicroPython repository:

```bash
# Option A: Copy from sibling repo
cp ../ic-python-tools/pyboard.py scripts/pyboard.py

# Option B: Download
curl -o scripts/pyboard.py https://raw.githubusercontent.com/micropython/micropython/master/tools/pyboard.py
```

Verify:
```bash
python scripts/pyboard.py --help
```
- **Pass**: Help text displayed

### 1.4 Detect COM Port

```bash
python -c "import serial.tools.list_ports; [print(p) for p in serial.tools.list_ports.comports()]"
```

Look for `<COM_PORT>` with description containing `STMicroelectronics` or `ST-Link`.

- **Pass**: `<COM_PORT>` listed with ST-Link identifier
- **Fail**: Check USB cable, install ST-Link driver

### 1.5 Verify STM32CubeProgrammer CLI

```bash
STM32_Programmer_CLI --version
```

If not in PATH, locate it (typical Windows paths):
```
"C:\Program Files\STMicroelectronics\STM32Cube\STM32CubeProgrammer\bin\STM32_Programmer_CLI.exe" --version
"C:\Program Files (x86)\STMicroelectronics\STM32Cube\STM32CubeProgrammer\bin\STM32_Programmer_CLI.exe" --version
```

- **Pass**: Version string printed
- **Fail**: Ensure STM32CubeProgrammer is installed and `bin` folder is in PATH

### 1.6 Test Board Connection via ST-Link

```bash
STM32_Programmer_CLI -c port=SWD -l
```

- **Pass**: Device info displayed (STM32G0B1xx, 512KB flash)
- **Fail**: Check USB connection, ensure board is powered, try reset

### 1.7 Create `<PREFIX>_board_config.json`

Write the board configuration to `<PREFIX>_board_config.json` in the project root (e.g., `g0_board_config.json` for the G0 family).

The JSON structure must include `board`, `mcu`, `family`, `core`, `clock_mhz`, `flash_kb`, `ram_kb`, `package`, `com_port`, `baudrate`, `stlink`, `firmware` (with `version`, `file`, `url`), `peripherals`, `pin_map`, `micropython_version`, and `filesystem_ok` fields populated for the target board.

Example for NUCLEO-G0B1RE (`g0_board_config.json`):

```json
{
  "board": "NUCLEO_G0B1RE",
  "mcu": "STM32G0B1RET6",
  "family": "G0",
  "core": "Cortex-M0+",
  "clock_mhz": 64,
  "flash_kb": 512,
  "ram_kb": 144,
  "package": "LQFP64",
  "com_port": "COM6",
  "baudrate": 115200,
  "stlink": "on-board ST-LINK/V2-1",
  "firmware": {
    "version": "v1.28.0",
    "file": "NUCLEO_G0B1RE-20260406-v1.28.0.hex",
    "url": "https://micropython.org/resources/firmware/NUCLEO_G0B1RE-20260406-v1.28.0.hex"
  },
  "peripherals": [
    "GPIO", "UART", "SPI", "I2C", "ADC", "DAC",
    "PWM", "RTC", "WDT", "ExtInt", "FDCAN", "USB"
  ],
  "pin_map": {
    "led": "PA5",
    "button": "PC13",
    "uart_num": 2,
    "uart_tx": "PA2",
    "uart_rx": "PA3",
    "spi_num": 2,
    "spi_sck": "PB13",
    "spi_miso": "PB14",
    "spi_mosi": "PB15",
    "spi_nss": "PB12",
    "i2c_num": 1,
    "i2c_scl": "PB8",
    "i2c_sda": "PB9",
    "adc_pin": "PA0",
    "adc_pin2": "PA1",
    "dac_pin": "PA4",
    "pwm_pin": "PA6",
    "fdcan_num": 1,
    "fdcan_tx": "PA12",
    "fdcan_rx": "PA11"
  },
  "micropython_version": null,
  "filesystem_ok": false
}
```

## Verification Criteria

All of the following must be true:
- [ ] Python 3.x available
- [ ] pyserial installed
- [ ] pyboard.py accessible at `scripts/pyboard.py`
- [ ] `<COM_PORT>` detected with ST-Link identifier
- [ ] STM32_Programmer_CLI responds with version
- [ ] ST-Link connects to board and reads device info
- [ ] `<PREFIX>_board_config.json` created in project root

## Output

`<PREFIX>_board_config.json` written to project root. Proceed to `02-flash-firmware.md`.
