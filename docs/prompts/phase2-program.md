# phase2-program.md — Phase 2: Application Development Orchestrator

## Purpose

This is the **Phase 2** entry-point prompt. After Phase 1 has validated the board and peripherals, Phase 2 builds application-specific functionality on top of that verified foundation.

The developer provides an application specification, and this prompt decomposes it into numbered sub-prompts that follow the same do-verify-retry pattern as Phase 1.

## Prerequisites

Before starting Phase 2, verify:

1. **Phase 1 is complete**: `<PREFIX>_test_results.json` exists in the project root with Phase 1 results.
2. **Board is operational**: `<PREFIX>_board_config.json` has `micropython_version` set and `filesystem_ok: true`.
3. **Peripherals are verified**: The peripherals needed by the application have `"status": "PASS"` in Phase 1 results.

> **Naming convention**: `<PREFIX>` is derived from the MCU family in lowercase (G0 -> `g0_`, G4 -> `g4_`, F4 -> `f4_`, etc.). All board-specific files use this prefix: `<PREFIX>_board_config.json`, `<PREFIX>_test_results.json`, `scripts/<PREFIX>_main.py`, `tests/<PREFIX>_test_<module>.py`. See `phase1-program.md` for the full convention.

### Verification Check

```bash
python scripts/pyboard.py --device <COM_PORT> -c "print('PHASE2_READY')"
```

If this fails, re-run Phase 1 first (`phase1-program.md`).

## Inputs

The developer provides **one** of the following:

| Input | Format | Example |
|-------|--------|---------|
| **Inline prompt** | Text describing the application | "Build a temperature logger that reads BME280 every 5s and logs to flash" |
| **Spec file** | Path to an `.md` file with detailed requirements | `docs/app-spec.md` |

The spec should include:
- **Functional requirements**: What the application does
- **Peripherals used**: Which interfaces (UART, SPI, I2C, ADC, etc.) and specific pins if known
- **External hardware**: Sensors, actuators, displays, or other devices connected to the board
- **Communication**: Protocols, data formats, baud rates
- **Timing**: Sampling rates, intervals, real-time constraints
- **Success criteria**: How to verify each feature works

## Execution Flow

### Step 1: Parse Application Specification

Read the developer's specification and extract:
- List of discrete features/modules to implement
- Peripheral dependencies for each module
- External hardware requirements
- Verification criteria per module

Cross-reference with `<PREFIX>_test_results.json` to confirm all required peripherals passed Phase 1. If a required peripheral has `"status": "FAIL"` or `"status": "SKIP"`, warn the developer before proceeding.

### Step 2: Generate Sub-Prompt Files

For each identified feature/module, create a numbered sub-prompt file under `docs/prompts/`:

```
docs/prompts/
  16-<first-module>.md
  17-<second-module>.md
  ...
  NN-app-integration.md
```

Numbering starts at **16** (continuing from Phase 1's `15-integration-test.md`).

Each sub-prompt file follows this template:

```markdown
# NN — <Module Name>

## Objective
<What this module implements>

## Prerequisites
- Phase 1 peripherals required: <list>
- External hardware: <if any>
- Previous Phase 2 modules required: <if any>

## Board-Specific Configuration
<Pin assignments from <PREFIX>_board_config.json>

## Implementation Script
<The MicroPython script to generate, with board-specific pin mappings>

## Execution
<pyboard.py commands to upload and run>

## Verification
<Expected output, PASS/FAIL criteria>

## Troubleshooting
<Common failure modes and fixes>

## Result Schema
{ "module": "<name>", "status": "PASS|FAIL|SKIP", "attempts": N }
```

### Step 3: Execute Sub-Prompts Sequentially

Run each generated sub-prompt using the same do-verify-retry loop:

```
for each module NN-<name>.md:
    attempt = 0
    while attempt < 3:
        execute module prompt
        generate script -> upload -> run -> parse output
        if all checks PASS:
            log to <PREFIX>_test_results.json under phase2_results
            break
        else:
            attempt += 1
            diagnose and adjust
    if attempt == 3:
        log FAIL and continue
```

### main.py Backup Convention

Before deploying any new `main.py`, the agent **must** back up the existing one on the board using the naming pattern `main_phase<N>.py`, where `N` is the phase that produced it. This applies at every phase transition:

```bash
python scripts/pyboard.py --device <COM_PORT> -c "import os; os.rename('main.py','main_phase<N>.py')"
```

For example, before Phase 2 deploys its application `main.py`, the Phase 1 demo `main.py` is renamed to `main_phase1.py`. If a Phase 3 is added later, Phase 2's `main.py` becomes `main_phase2.py`, and so on.

The agent should verify the backup exists before uploading the replacement:
```bash
python scripts/pyboard.py --device <COM_PORT> -f ls :
```

### Step 4: Application Integration

The final sub-prompt (`NN-app-integration.md`) must:

1. **Back up the current `main.py`** as `main_phase<N>.py` on the board (see backup convention above).
2. Combine all passing Phase 2 modules into a unified application `scripts/<PREFIX>_main.py`.
3. Replace the previous `main.py` on the board with the application `scripts/<PREFIX>_main.py`.
4. Preserve `boot.py` unless the application requires changes to it.
5. Upload to the board and verify the application runs end-to-end.
6. Verify both the backup file and the new `main.py` exist on the board filesystem.

### Step 5: Final Report

Print a combined Phase 1 + Phase 2 report:

```
=== MicroPython Development Report ===
Board: <BOARD_NAME> (<MCU>)
Firmware: MicroPython <VERSION>

--- Phase 1: Board Bring-Up ---
Module          Status    Attempts
------          ------    --------
GPIO            PASS      1
UART            PASS      1
...

--- Phase 2: Application (<APP_NAME>) ---
Module          Status    Attempts
------          ------    --------
<module-1>      PASS      1
<module-2>      PASS      2
...
app-integration PASS      1

Result: Phase 1: XX/YY PASS | Phase 2: XX/YY PASS
Application deployed successfully.
```

## State File Updates

### `<PREFIX>_test_results.json`

Phase 2 appends to the existing file:

```json
{
  "board": "NUCLEO_G0B1RE",
  "results": [ "... Phase 1 ..." ],
  "phase2_results": [
    { "module": "<name>", "status": "PASS", "attempts": 1, "notes": "..." }
  ],
  "application": {
    "name": "<app-name>",
    "spec_source": "<inline or file path>",
    "modules_generated": ["16-xxx.md", "17-xxx.md", "..."]
  }
}
```

### changelog.md

Log any deviations encountered during Phase 2 execution, following the same format as Phase 1 entries.

## How to Run

After Phase 1 is complete, the developer triggers Phase 2:

```
> @docs/prompts/phase2-program.md — I want to build <application description>
```

Or with a spec file:

```
> @docs/prompts/phase2-program.md — Application spec is in docs/app-spec.md
```

The agent reads this file, parses the application specification, generates sub-prompts, and executes them sequentially.
