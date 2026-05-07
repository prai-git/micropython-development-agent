# Changelog — Prompt Deviations and Updates

This file records deviations encountered during development and any prompt updates required. Keeping this log ensures prompts remain accurate and reusable across boards.

## Format

Each entry follows:
```
### [DATE] Module NN — Short description
- **Deviation**: What happened vs. what the prompt expected
- **Resolution**: What was done to fix it
- **Prompt update**: Whether the prompt was updated (and what changed)
```

---

## Log

### 2026-05-06 Module 01 — STM32CubeProgrammer path deviation
- **Deviation**: Prompt assumed `STM32_Programmer_CLI` in PATH or under `C:\Program Files\...`. Actual location was `C:\Program Files (x86)\STMicroelectronics\STM32Cube\STM32CubeProgrammer\bin\`.
- **Resolution**: Used full path. Stored in `board_config.json` as `programmer_cli`.
- **Prompt update**: `01-setup-environment.md` should include `Program Files (x86)` as an alternate search path. Updated to add both locations.

### 2026-05-06 Module 01 — pyserial not pre-installed
- **Deviation**: Prompt assumed pyserial may already be installed. It was not (`ModuleNotFoundError`).
- **Resolution**: Installed via `python -m pip install pyserial` (note: `pip` bare command was not in PATH, needed `python -m pip`).
- **Prompt update**: `01-setup-environment.md` should use `python -m pip install pyserial` instead of `pip install pyserial` for portability.

### 2026-05-06 Module 03 — sys.platform returns 'pyboard' not 'stm32'
- **Deviation**: Prompt expected `sys.platform` to return `stm32`. Actual value is `pyboard` on all STM32 MicroPython builds.
- **Resolution**: No action needed — `pyboard` is the correct platform identifier for the STM32 MicroPython port.
- **Prompt update**: `03-verify-repl.md` should check for `pyboard` not `stm32`. Updated verification criteria.

### 2026-05-06 Module 03 — machine.freq() returns tuple not int
- **Deviation**: Prompt expected `machine.freq()` to return `64000000` (int). Actual return is `(64000000, 64000000, 64000000)` (tuple of SYSCLK, HCLK, PCLK).
- **Resolution**: No action needed — first element confirms 64 MHz.
- **Prompt update**: `03-verify-repl.md` should check that 64000000 appears in the result, not strict equality. Updated.

### 2026-05-06 Module 04 — Pin.toggle() not available on G0
- **Deviation**: `Pin.toggle()` raised `AttributeError` on the STM32G0 MicroPython port. This method is available on F4/F7/H7 but not on all ports.
- **Resolution**: Added try/except fallback that manually toggles via `led.value(1 - led.value())`.
- **Prompt update**: `04-gpio.md` updated with try/except pattern for Pin.toggle(). All boards should use this defensive pattern.

### 2026-05-06 Module 05 — UART enumeration hangs when touching REPL UART
- **Deviation**: Attempting `UART(2, 9600)` init/deinit during enumeration hung the board because UART2 is the active REPL/VCP channel. pyboard.py session became unresponsive.
- **Resolution**: Skip UART2 in the enumeration loop. Required ST-Link reset to recover board.
- **Prompt update**: `05-uart.md` updated to exclude the REPL UART from enumeration. Generic rule: never re-init the UART that pyboard.py uses for communication.

### 2026-05-06 Module 14 — FDCAN not in G0 MicroPython build
- **Deviation**: Neither `pyb.CAN` nor `machine.CAN` are available in the NUCLEO_G0B1RE v1.28.0 firmware. The STM32G0B1RE hardware has 2 FDCAN interfaces but the MicroPython build does not include CAN support.
- **Resolution**: Marked as SKIP. CAN support would require a custom MicroPython build with FDCAN enabled.
- **Prompt update**: `14-can.md` — no change needed (SKIP path already handled). Added note to `program.md` peripheral availability: G0 firmware may lack CAN despite hardware support.

### 2026-05-06 Module 16 — Timer(1) not available on G0 (hardware timers not exposed)
- **Deviation**: `Timer(1, freq=2, callback=...)` raised `ValueError: Timer doesn't exist`. All hardware timer IDs (1–17) fail on the STM32G0 MicroPython port. Only `Timer(-1)` (virtual/soft timer) is available.
- **Resolution**: Changed to `Timer(-1, freq=2, callback=heartbeat_cb)`. Virtual timer runs from the MicroPython scheduler, sufficient for non-critical periodic tasks like LED heartbeat.
- **Prompt update**: `16-heartbeat-led.md` and `18-app-integration.md` updated to use `Timer(-1)` as default, with a note that some ports only support virtual timers.

### 2026-05-06 Structural — main.py backup convention added
- **Change**: Added a consistent backup rule: before deploying a new `main.py`, rename the existing one to `main_phase<N>.py` on the board.
- **Rationale**: Previously only `18-app-integration.md` had an ad-hoc backup step (`main_phase1_demo.py`). Now the convention is defined in both orchestrators (`phase1-program.md`, `phase2-program.md`) and the relevant sub-prompts (`15-integration-test.md`, `18-app-integration.md`).
- **Files updated**: `phase1-program.md` (added backup convention section), `phase2-program.md` (added backup convention section, updated Step 4), `15-integration-test.md` (added backup before upload in 15.4), `18-app-integration.md` (updated to use `main_phase1.py` naming and reference the convention).

### 2026-05-06 Structural — Two-phase prompt architecture
- **Change**: Renamed `program.md` to `phase1-program.md`. Created `phase2-program.md` for application-specific development.
- **Rationale**: Phase 1 (board bring-up) is generic and reusable across any MicroPython-supported STM32 board. Phase 2 (application development) is user-specific and generates sub-prompts starting at `16-xxx.md`.
- **Files updated**: `phase1-program.md` (header + purpose), `getting-started-micropython.md` (workflow overview, prompt file structure, added Phase 2 section). Created `phase2-program.md`.

### 2026-05-06 Structural — Multi-board naming convention
- **Change**: All board-specific files now use a family prefix: `<PREFIX>_` where PREFIX is the MCU family in lowercase (e.g., `g0_` for G0 family, `g4_` for G4 family).
- **Affected files**: `board_config.json` → `<PREFIX>_board_config.json`, `test_results.json` → `<PREFIX>_test_results.json`, `tests/test_*.py` → `tests/<PREFIX>_test_*.py`, `scripts/main.py` → `scripts/<PREFIX>_main.py`.
- **Rationale**: Project now supports multiple boards simultaneously (NUCLEO-G0B1RE and NUCLEO-G474RE). The prefix prevents board-specific files from being overwritten or deleted when switching between boards.
- **Files updated**: All prompt files (01-18, phase1-program.md, phase2-program.md), `getting-started-micropython.md`, existing G0 files renamed with `g0_` prefix, new G4 files created with `g4_` prefix.

### 2026-05-06 Module 04 (G4) — Pin naming differs on G4 port
- **Deviation**: `Pin('PA5')` raises `ValueError: Pin(PA5) doesn't exist` on the STM32G4 MicroPython port. G4 uses board-level names (`LED1`, `SW`, `D0`-`D15`, `A0`-`A5`, `SPI_*`, `I2C_*`, `LPUART1_*`, `UART1_*`) instead of port-style names (`PA5`, `PC13`).
- **Resolution**: Used `Pin('LED1')` for LED and `Pin('SW')` for button. Discovered via `dir(Pin.board)`.
- **Prompt update**: `04-gpio.md` should note this deviation. Generic fix: try board-level names if port-style names fail.

### 2026-05-06 Module 05 (G4) — VCP is LPUART1 not UART2
- **Deviation**: On NUCLEO-G474RE, the ST-Link Virtual COM Port is connected to LPUART1 (PA2/PA3), not UART2 as on G0B1RE. `UART(2)` doesn't exist in the G4 build. Available UARTs: 1 (PC4/PC5) and 3.
- **Resolution**: Used `print()` for VCP TX verification (LPUART1 is the REPL channel). Tested UART1 independently.
- **Prompt update**: `05-uart.md` should detect the VCP UART from `board_config.json` rather than hardcoding UART2.

### 2026-05-06 Module 04 (G4) — Pin.toggle() not available on G4
- **Deviation**: Same as G0 — `Pin.toggle()` raises `AttributeError`. Manual toggle fallback works.
- **Resolution**: Same try/except pattern as G0.
- **Prompt update**: Already documented for G0. Confirmed this is a cross-family issue.

### 2026-05-06 Module 14 (G4) — FDCAN requires filter configuration
- **Deviation**: `pyb.CAN` on G4 uses FDCAN, which requires `can.setfilter(0, CAN.MASK, 0, (0, 0))` before `recv()` will work. Without the filter, recv times out. Also, `CAN.MASK16` doesn't exist — FDCAN uses `CAN.MASK`.
- **Resolution**: Added `setfilter()` call after init. Single-message loopback verified. Multi-message loopback has FIFO timing issues.
- **Prompt update**: `14-can.md` should add filter setup for FDCAN-equipped boards (G4, H7).

### 2026-05-06 Module 12 (G4) — WDT causes COM port lockup
- **Deviation**: After WDT test + `machine.reset()`, a hung `pyboard.py` process held COM7 open. The board was alive but inaccessible until the orphaned Python process was killed.
- **Resolution**: Used `Stop-Process` to kill the hung process, then reconnected. ST-Link SWD reset also works as recovery.
- **Prompt update**: `12-watchdog.md` post-test cleanup should note that the reset may leave a hung serial process on Windows, requiring `taskkill` or process manager.

### 2026-05-06 Module 15 (G4) — sys.stdin.readable() not available in MicroPython
- **Deviation**: `g4_main.py` menu used `sys.stdin.readable()` to poll for input. This is a CPython API — MicroPython's `TextIOWrapper` does not have a `readable()` method. The menu displayed correctly but crashed with `AttributeError` before accepting any input. This was missed during the Phase 1 integration verify step.
- **Resolution**: Replaced `sys.stdin.readable()` / `sys.stdin.read(1)` polling loop with `input("Choice: ")`, which blocks and works correctly in MicroPython's REPL.
- **Prompt update**: `15-integration-test.md` verification must include an interactive input test after board reset — confirming the menu displays is not sufficient. `18-app-integration.md` should mandate `input()` for REPL user input, never `sys.stdin.readable()`.

### 2026-05-06 Module 15 (G4) — GPIO demo button polling misses quick presses
- **Deviation**: `demo_gpio()` used `if not button.value()` polling inside the 500ms LED blink loop. Quick button presses were missed entirely because the check only runs twice per second. The prompt template in `15-integration-test.md` also used `led.toggle()` (known broken on G0/G4 from Module 04) and the same polling pattern.
- **Resolution**: Replaced polling with `Pin.IRQ_FALLING` interrupt + 20ms debounce. IRQ sets a flag; the main loop prints and clears it. IRQ handler is cleaned up on Ctrl+C via `finally` block. Also replaced `led.toggle()` with `led.value(1 - led.value())` in the prompt template.
- **Prompt update**: `15-integration-test.md` demo_gpio template updated to use IRQ-based button detection and manual LED toggle. Pin names parameterized as `LED_PIN`/`BTN_PIN` (read from `<PREFIX>_board_config.json`).

### 2026-05-06 Module 15 (G4) — Unicode em dashes render as garbage on serial terminal
- **Deviation**: Menu item labels used Unicode em dash (`—`) which displayed as `â` on the serial console. Serial terminals use ASCII/Latin-1, not UTF-8.
- **Resolution**: Replaced all `—` with ASCII `-` in `g4_main.py`.
- **Prompt update**: `15-integration-test.md` and `18-app-integration.md` updated with ASCII-only rule for all strings sent to serial terminal.

### 2026-05-06 Module 04/15 (G4) — Pin.PULL_UP conflicts with B1 external circuit on NUCLEO-G474RE
- **Deviation**: `Pin('SW', Pin.IN, Pin.PULL_UP)` gives a resting value of 0 on the NUCLEO-G474RE, making `IRQ_FALLING` never trigger. Without any pull (`Pin('SW', Pin.IN)`), resting value is 1 and button presses correctly produce falling edges. The board's external pull-up circuit on B1/PC13 conflicts with the internal pull-up on the G4 port.
- **Resolution**: Changed button init to `Pin('SW', Pin.IN)` with no pull resistor. Added `button_pull` and `button_active` fields to `g4_board_config.json`.
- **Prompt update**: `04-gpio.md` and `15-integration-test.md` should read `button_pull` from `<PREFIX>_board_config.json` rather than hardcoding `Pin.PULL_UP`. Generic rule: always test the button's resting value before assuming pull configuration.
