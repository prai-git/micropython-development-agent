# micropython-development-agent

MicroPython development environment for STM32 Nucleo evaluation boards. Provides a prompt-driven, two-phase workflow for board bring-up and application development.

## Supported Boards

| Board | MCU | Family Prefix | COM Port | Status |
|-------|-----|---------------|----------|--------|
| NUCLEO-G0B1RE | STM32G0B1RET6 | `g0_` | COM3 | Phase 1 + Phase 2 complete |
| NUCLEO-G474RE | STM32G474RET6 | `g4_` | COM7 | Phase 1 complete |

## Project Structure

```
ic-mp-dev/
├── docs/
│   ├── plan/                  # Getting started guide
│   └── prompts/               # Orchestrator and module prompts (01-18)
├── firmware/                  # MicroPython .hex files per board
├── scripts/
│   ├── pyboard.py             # Host-to-board communication utility
│   ├── boot.py                # Shared boot script (uploaded to all boards)
│   ├── g0_main.py             # NUCLEO-G0B1RE application
│   └── g4_main.py             # NUCLEO-G474RE application
├── tests/
│   ├── g0_test_*.py           # NUCLEO-G0B1RE peripheral test scripts
│   └── g4_test_*.py           # NUCLEO-G474RE peripheral test scripts
├── g0_board_config.json       # G0 board configuration and pin map
├── g0_test_results.json       # G0 Phase 1 + Phase 2 test results
├── g4_board_config.json       # G4 board configuration and pin map
└── g4_test_results.json       # G4 Phase 1 test results
```

## Naming Convention

All board-specific files use an MCU family prefix (`g0_`, `g4_`, etc.) to prevent overwrites when switching between boards. Shared files (`pyboard.py`, `boot.py`) have no prefix.

## Prerequisites

- Python 3.8+
- STM32CubeProgrammer (for firmware flashing via ST-Link SWD)
- A supported Nucleo board connected via USB

## Setup

```bash
pip install -r requirements.txt
```

## Workflow

### Phase 1 - Board Bring-Up

Orchestrated by `docs/prompts/phase1-program.md`. Runs modules 01-15 in a do-verify-retry loop:

1. Environment setup and firmware flash
2. REPL verification
3. Peripheral tests (GPIO, UART, SPI, I2C, ADC, DAC, PWM, RTC, WDT, ExtInt, CAN)
4. Integration test with menu-driven demo deployed as `main.py`

### Phase 2 - Application Development

Orchestrated by `docs/prompts/phase2-program.md`. Builds on Phase 1 results to develop board-specific applications (modules 16+).

## Usage

Communicate with a board using `pyboard.py`:

```bash
# List files on board
python scripts/pyboard.py -d COM7 -f ls :

# Run a test script
python scripts/pyboard.py -d COM7 tests/g4_test_gpio.py

# Upload a file to the board
python scripts/pyboard.py -d COM7 -f cp scripts/g4_main.py :main.py

# Execute a command on the board
python scripts/pyboard.py -d COM7 -c "import machine; print(machine.freq())"
```

## Adding a New Board

1. Create `<prefix>_board_config.json` with the board's pin map and peripherals
2. Run Phase 1 using `docs/prompts/phase1-program.md`
3. All test scripts and results are created with the board's family prefix
4. Deviations are logged in `docs/prompts/changelog.md`

## License

[MIT](LICENSE)
