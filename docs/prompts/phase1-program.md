# phase1-program.md — Phase 1: Board Bring-Up Orchestrator

## Purpose

This is the **Phase 1** entry-point prompt for automating MicroPython board bring-up on a supported STM32 board. An AI agent (Claude Code, Copilot, etc.) executes this prompt to bring a board from bare metal to a fully tested MicroPython environment with peripheral verification.

Phase 1 focuses exclusively on **board bring-up**: firmware flashing, REPL verification, and peripheral-by-peripheral hardware validation. Once Phase 1 completes successfully, the developer can proceed to **Phase 2** (`phase2-program.md`) for application-specific development.

## Multi-Board Naming Convention

This project supports multiple boards simultaneously. To avoid collisions, every board-specific file is prefixed with a tag derived from the MCU family in **lowercase**:

| MCU Family | Prefix |
|------------|--------|
| G0 | `g0_` |
| G4 | `g4_` |
| F4 | `f4_` |
| H7 | `h7_` |
| L4 | `l4_` |

Naming rules:

- **Config files**: `<PREFIX>_board_config.json`, `<PREFIX>_test_results.json` (e.g., `g0_board_config.json`, `g4_test_results.json`)
- **Test scripts**: `tests/<PREFIX>_test_<module>.py` (e.g., `tests/g0_test_gpio.py`, `tests/g4_test_gpio.py`)
- **Application scripts**: `scripts/<PREFIX>_main.py` (e.g., `scripts/g0_main.py`, `scripts/g4_main.py`)
- **Never** overwrite or delete files belonging to another board's prefix. Each prefix is an isolated namespace.

## Inputs (provided by the developer)

| Input | Description | Example |
|-------|-------------|---------|
| **Board** | Nucleo/Discovery board name | NUCLEO-G0B1RE, NUCLEO-G474RE |
| **COM port** | Serial port the board is connected on | `<COM_PORT>` (e.g., COM6, COM7) |
| **Datasheet** | Path to board/MCU datasheet (PDF) or URL | (optional — agent can web-search) |
| **pyboard.py path** | Path to the pyboard.py utility | `../ic-python-tools/pyboard.py` |

## Board Configuration — NUCLEO-G0B1RE

This project targets the **NUCLEO-G0B1RE** evaluation board:

| Parameter | Value |
|-----------|-------|
| MCU | STM32G0B1RET6 |
| Family | G0 |
| Core | ARM Cortex-M0+ @ 64 MHz |
| Flash | 512 KB |
| RAM | 144 KB SRAM |
| Package | LQFP64 |
| COM Port | COM6 |
| ST-Link | On-board ST-LINK/V2-1 (SWD + VCP) |
| MicroPython firmware | NUCLEO_G0B1RE v1.28.0 (.hex) |

### Pin Map

| Function | Pin | Notes |
|----------|-----|-------|
| User LED (LD4) | PA5 | Active HIGH |
| User Button (B1) | PC13 | Active LOW, external pull-up |
| UART2 TX (VCP) | PA2 | Connected to ST-Link Virtual COM |
| UART2 RX (VCP) | PA3 | Connected to ST-Link Virtual COM |
| SPI1 SCK | PA5 | Arduino D13 (shared with LED) |
| SPI1 MISO | PA6 | Arduino D12 |
| SPI1 MOSI | PA7 | Arduino D11 |
| SPI1 NSS | PB0 | Arduino D10 |
| SPI2 SCK | PB13 | Morpho connector |
| SPI2 MISO | PB14 | Morpho connector |
| SPI2 MOSI | PB15 | Morpho connector |
| SPI2 NSS | PB12 | Morpho connector |
| I2C1 SCL | PB8 | Arduino D15 |
| I2C1 SDA | PB9 | Arduino D14 |
| I2C2 SCL | PA11 | Morpho connector |
| I2C2 SDA | PA12 | Morpho connector |
| ADC1 IN0 | PA0 | Arduino A0 |
| ADC1 IN1 | PA1 | Arduino A1 |
| DAC1 OUT1 | PA4 | Arduino A2 |
| FDCAN1 TX | PA12 | Shared with I2C2 SDA |
| FDCAN1 RX | PA11 | Shared with I2C2 SCL |
| FDCAN2 TX | PB1 | Morpho connector |
| FDCAN2 RX | PB0 | Shared with SPI1 NSS |

### Available Peripherals

GPIO, UART (6x USART + 2x LPUART), SPI (3x), I2C (3x), ADC (12-bit, 16ch), DAC (2ch), PWM/Timer, RTC, WDT, ExtInt, FDCAN (2x), USB 2.0 FS.

## Board Configuration — NUCLEO-G474RE

| Parameter | Value |
|-----------|-------|
| MCU | STM32G474RET6 |
| Family | G4 |
| Core | ARM Cortex-M4F @ 170 MHz |
| Flash | 512 KB |
| RAM | 128 KB SRAM |
| Package | LQFP64 |
| COM Port | COM7 |
| ST-Link | On-board ST-LINK/V3E (SWD + VCP) |
| MicroPython firmware | NUCLEO_G474RE v1.28.0 (.hex) |

### Pin Map

| Function | Pin | Notes |
|----------|-----|-------|
| User LED (LD2) | PA5 | Active HIGH |
| User Button (B1) | PC13 | Active LOW, external pull-up |
| UART2 TX (VCP) | PA2 | Connected to ST-Link Virtual COM |
| UART2 RX (VCP) | PA3 | Connected to ST-Link Virtual COM |
| I2C1 SCL | PB8 | Arduino D15 |
| I2C1 SDA | PB9 | Arduino D14 |
| ADC1 IN1 | PA0 | Arduino A0 |
| ADC1 IN2 | PA1 | Arduino A1 |
| DAC1 OUT1 | PA4 | Arduino A2 |
| PWM | PA6 | Timer output |
| FDCAN1 TX | PA11 | CAN bus transmit |
| FDCAN1 RX | PA12 | CAN bus receive |

### Available Peripherals

GPIO, UART (5x USART + 1x LPUART), SPI (4x), I2C (4x), ADC (12-bit, 5 ADCs), DAC (4ch), PWM/Timer, RTC, WDT, ExtInt, FDCAN (1x), CORDIC, FMAC, OPAMP (6x), COMP (7x), USB 2.0 FS.

**Notable differences from G0B1RE**: DAC (4 channels vs 2), hardware math accelerators (CORDIC, FMAC), operational amplifiers (OPAMP), single FDCAN (vs 2 on G0), Cortex-M4F with FPU and DSP instructions.

## Execution Flow

The agent executes each sub-prompt in sequence. Each module follows a **do-verify-retry loop**: run the step, verify the result, retry up to 3 times on failure, then move on.

```
Step 1:  01-setup-environment.md   -> Verify tools, detect board, create <PREFIX>_board_config.json
Step 2:  02-flash-firmware.md      -> Download & flash MicroPython v1.28.0
Step 3:  03-verify-repl.md         -> Confirm REPL and filesystem access
Step 4:  04-gpio.md                -> Test LED (PA5) and button (PC13)
Step 5:  05-uart.md                -> Test UART2 TX/RX via ST-Link VCP
Step 6:  06-spi.md                 -> Initialize SPI2 (PB13-PB15), write test
Step 7:  07-i2c.md                 -> Initialize I2C1 (PB8/PB9), bus scan
Step 8:  08-adc.md                 -> Read PA0, internal temp sensor
Step 9:  09-dac.md                 -> Output voltage on PA4, cross-verify with ADC
Step 10: 10-pwm-timer.md           -> PWM output on PA6 via Timer
Step 11: 11-rtc.md                 -> Set/read RTC
Step 12: 12-watchdog.md            -> WDT feed test
Step 13: 13-extint.md              -> External interrupt on PC13 (button)
Step 14: 14-can.md                 -> FDCAN loopback test
Step 15: 15-integration-test.md    -> Generate unified <PREFIX>_main.py, upload, verify menu
```

## main.py Backup Convention

Before deploying a new `main.py` to the board, the agent **must** back up the existing one using the naming convention `main_phase<N>.py` (e.g., `main_phase1.py`). This ensures each phase's application can be restored.

At the end of Phase 1 (Step 15), the integration test prompt uploads the Phase 1 demo `main.py`. Before Phase 2 replaces it, the Phase 2 integration step renames it to `main_phase1.py` on the board. If additional phases are added, the pattern continues (`main_phase2.py`, etc.).

To back up on the board:
```bash
python scripts/pyboard.py --device <COM_PORT> -c "import os; os.rename('main.py','main_phase1.py')"
```

## State Files

The agent maintains two JSON files in the project root:

- **`<PREFIX>_board_config.json`** — MCU info, pin map, detected peripherals (created at Step 1, updated as needed)
- **`<PREFIX>_test_results.json`** — Per-module PASS/FAIL/SKIP results (appended at each step)

## Verification Loop (per module)

```
for each module NN-<name>.md:
    attempt = 0
    while attempt < 3:
        execute module prompt
        upload test script via: python pyboard.py --device <COM_PORT> -f cp <PREFIX>_test_<name>.py :
        run test via: python pyboard.py --device <COM_PORT> <PREFIX>_test_<name>.py
        parse stdout for PASS / FAIL / SKIP markers
        if all checks PASS:
            log to <PREFIX>_test_results.json: { "module": "<name>", "status": "PASS", "attempts": attempt+1 }
            break
        else:
            attempt += 1
            diagnose failure from output
            adjust pin map or init parameters in test script
    if attempt == 3:
        log to <PREFIX>_test_results.json: { "module": "<name>", "status": "FAIL", "attempts": 3, "error": "<last error>" }
        continue to next module
```

## Final Report

After all modules complete, print a summary:

```
=== MicroPython Peripheral Test Report ===
Board: NUCLEO-G0B1RE (STM32G0B1RET6)
Firmware: MicroPython v1.28.0

Module          Status    Attempts
------          ------    --------
GPIO            PASS      1
UART            PASS      1
SPI             PASS      1
I2C             PASS      1
ADC             PASS      1
DAC             PASS      1
PWM/Timer       PASS      1
RTC             PASS      1
Watchdog        PASS      1
ExtInt          PASS      1
FDCAN           PASS      1

Result: 11/11 PASS
```

## How to Run

Point the AI agent at this file:

```
> @docs/prompts/phase1-program.md — Start MicroPython development on NUCLEO-G0B1RE (COM6)
> @docs/prompts/phase1-program.md — Start MicroPython development on NUCLEO-G474RE (COM7)
```

The agent reads this file, then sequentially invokes each sub-prompt from `docs/prompts/01-*.md` through `docs/prompts/15-*.md`.
