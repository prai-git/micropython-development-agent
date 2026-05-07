# CLAUDE.md — MicroPython STM32 Development Project

## Project Overview

This project automates MicroPython board bring-up and application development on STM32 Nucleo evaluation boards. It uses a two-phase, prompt-driven workflow with board-specific file prefixes to support multiple boards simultaneously.

- **Phase 1** (Board Bring-Up): Firmware flashing, REPL verification, peripheral-by-peripheral hardware validation. Orchestrated by `docs/prompts/phase1-program.md` with sub-prompts `01` through `15`.
- **Phase 2** (Application Development): Application-specific features built on the verified peripheral foundation. Orchestrated by `docs/prompts/phase2-program.md` with sub-prompts starting at `16`.

## When the User Asks to Run MicroPython on an Eval Board

When the user asks to "start building support for MicroPython", "run MicroPython", or "bring up MicroPython" on a specific STM32 eval board, follow these three steps **in order** before doing anything else:

### Step 1 — Check MicroPython Port Availability

Perform a web search to determine whether an official MicroPython port exists for the requested board:

1. Search `micropython.org/download/<BOARD_NAME>` (e.g., `NUCLEO_H563ZI`).
2. Search the MicroPython GitHub repo (`micropython/micropython`) for a board definition under `ports/stm32/boards/<BOARD_NAME>/`.
3. Search for community ports or forks if no official port is found.

**Report a clear summary** to the user:
- Whether an official port exists (with download link if yes).
- Available firmware versions.
- Known peripheral support and any documented limitations.
- If **no port exists**: stop here, inform the user, and suggest alternatives (e.g., closest supported board, community forks, or bare-metal approach).

### Step 2 — Check If Board Files Already Exist

Determine the board's family prefix from the MCU family name in lowercase (e.g., `NUCLEO_G0B1RE` -> family `G0` -> prefix `g0_`, `NUCLEO_H563ZI` -> family `H5` -> prefix `h5_`).

Check for existing board-specific files using that prefix:

| Location | File Pattern | Example (G4) |
|----------|-------------|---------------|
| Project root | `<PREFIX>_board_config.json` | `g4_board_config.json` |
| Project root | `<PREFIX>_test_results.json` | `g4_test_results.json` |
| `scripts/` | `<PREFIX>_main.py` | `scripts/g4_main.py` |
| `tests/` | `<PREFIX>_test_*.py` | `tests/g4_test_gpio.py` |
| `firmware/` | Board-named firmware files | `NUCLEO_G474RE-*.hex` |

**If files exist:**
1. Read `<PREFIX>_board_config.json` to confirm board identity and configuration.
2. Read `<PREFIX>_test_results.json` to check Phase 1 and Phase 2 completion status.
3. **Validate by running `<PREFIX>_main.py`** on the board:
   ```
   python scripts/pyboard.py --device <COM_PORT> <PREFIX>_main.py
   ```
   Or if already deployed to the board:
   ```
   python scripts/pyboard.py --device <COM_PORT> -c "print('BOARD_OK')"
   ```
4. If validation passes, report to the user: "MicroPython support for `<BOARD>` is already configured and operational. Phase 1: X/Y PASS, Phase 2: [complete/not started]."
5. If validation fails, diagnose the issue (COM port changed, board disconnected, firmware corruption) and attempt to resolve before falling through to Step 3.

**If files do not exist:** proceed to Step 3.

### Step 3 — Start Phase-Wise Development

When no existing files are found (or validation in Step 2 failed and cannot be resolved):

1. **Read the master plan**: `docs/plan/getting-started-micropython.md` — understand the full architecture, supported families, peripheral matrix, and naming conventions.
2. **Read the Phase 1 orchestrator**: `docs/prompts/phase1-program.md` — understand inputs, execution flow, state files, and verification loop.
3. **Begin Phase 1 execution** by following `phase1-program.md` sequentially through sub-prompts `01` through `15`:
   - `01-setup-environment.md` -> `02-flash-firmware.md` -> `03-verify-repl.md` -> ... -> `15-integration-test.md`
   - Each sub-prompt follows the do-verify-retry loop (max 3 attempts per module).
   - All generated files **must** use the board's family prefix (`<PREFIX>_`).
   - Log results to `<PREFIX>_test_results.json` after each module.
4. After Phase 1 completes, report results and ask the user if they want to proceed to **Phase 2** (`docs/prompts/phase2-program.md`) for application development.

## Critical Rules

### Multi-Board Naming Convention

All board-specific files use a family prefix derived from the MCU family in lowercase:

| MCU Family | Prefix | Board Example |
|------------|--------|---------------|
| F0 | `f0_` | NUCLEO_F091RC |
| F4 | `f4_` | NUCLEO_F446RE |
| F7 | `f7_` | NUCLEO_F767ZI |
| G0 | `g0_` | NUCLEO_G0B1RE |
| G4 | `g4_` | NUCLEO_G474RE |
| H5 | `h5_` | NUCLEO_H563ZI |
| H7 | `h7_` | NUCLEO_H743ZI |
| L4 | `l4_` | NUCLEO_L476RG |
| WB | `wb_` | NUCLEO_WB55 |
| WL | `wl_` | NUCLEO_WL55 |

### File Safety

- **NEVER overwrite or delete files belonging to another board's prefix.** Each prefix is an isolated namespace.
- **NEVER restructure existing board files.** Create new prefixed files for new boards.
- Before deploying a new `main.py` to a board, **always back up** the existing one as `main_phase<N>.py`.

### Shared Files (No Prefix)

These files are shared across all boards — do not prefix or duplicate them:
- `scripts/pyboard.py`, `scripts/boot.py`
- Everything under `docs/`
- `requirements.txt`, `README.md`, `LICENSE`

## Currently Configured Boards

| Board | Prefix | Phase 1 | Phase 2 | COM Port |
|-------|--------|---------|---------|----------|
| NUCLEO_G0B1RE | `g0_` | Complete | Complete | COM6 |
| NUCLEO_G474RE | `g4_` | Complete | Not started | COM7 |

## Project Structure

```
ic-mp-dev/
  docs/
    plan/
      getting-started-micropython.md    # Master plan
    prompts/
      phase1-program.md                 # Phase 1 orchestrator
      phase2-program.md                 # Phase 2 orchestrator
      01-setup-environment.md           # Sub-prompts 01-15 (Phase 1)
      ...
      15-integration-test.md
      16-heartbeat-led.md               # Sub-prompts 16+ (Phase 2, G0-specific)
      ...
      changelog.md                      # Deviation log
  firmware/                             # .hex firmware files per board
  scripts/
    pyboard.py                          # Host-to-board utility (shared)
    boot.py                             # MicroPython boot script (shared)
    <PREFIX>_main.py                    # Board-specific application
  tests/
    <PREFIX>_test_<module>.py           # Board-specific test scripts
  <PREFIX>_board_config.json            # Board config (root)
  <PREFIX>_test_results.json            # Test results (root)
```

## Tools and Dependencies

- **Python 3.x** with `pyserial` (`pip install pyserial`)
- **STM32CubeProgrammer** for firmware flashing
- **pyboard.py** (`scripts/pyboard.py`) for uploading scripts and running commands on the board
- Board connected via USB (ST-Link provides SWD + Virtual COM Port)
