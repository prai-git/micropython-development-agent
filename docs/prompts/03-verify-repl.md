# 03 — Verify REPL and Filesystem

## Objective

Confirm the MicroPython REPL is responsive, basic Python execution works, and the filesystem is functional for uploading/downloading scripts.

## Prerequisites

- MicroPython firmware flashed (Step 02 complete)
- Board on `<COM_PORT>`

## Steps

### 3.1 REPL Arithmetic Test

```bash
python scripts/pyboard.py --device <COM_PORT> -c "print(2 + 2)"
```

- **Pass**: Output is `4`
- **Fail**: REPL not responding — check COM port, try `--no-soft-reset`

### 3.2 System Info

```bash
python scripts/pyboard.py --device <COM_PORT> -c "import sys; print(sys.platform); print(sys.implementation)"
```

- **Pass**: Platform is `pyboard` (the STM32 MicroPython port identifies as `pyboard`), implementation is `micropython`

### 3.3 Machine Frequency

```bash
python scripts/pyboard.py --device <COM_PORT> -c "import machine; print('freq:', machine.freq())"
```

- **Pass**: Output contains `64000000`. Note: may return a tuple `(SYSCLK, HCLK, PCLK)` rather than a single int — check that 64000000 appears in the result.
- **Note**: G0 series runs at 64 MHz max

### 3.4 List Filesystem

```bash
python scripts/pyboard.py --device <COM_PORT> -c "import os; print(os.listdir('/'))"
```

- **Pass**: Returns a list (may contain `['flash']` or `['']`)

### 3.5 File Upload Round-Trip

Create a test file:
```bash
echo "print('HELLO_FROM_BOARD')" > tests/<PREFIX>_<PREFIX>_test_hello.py
```

Upload:
```bash
python scripts/pyboard.py --device <COM_PORT> -f cp tests/<PREFIX>_<PREFIX>_test_hello.py :
```

Verify it exists on board:
```bash
python scripts/pyboard.py --device <COM_PORT> -f ls :
```

- **Pass**: `<PREFIX>_test_hello.py` appears in listing

Execute:
```bash
python scripts/pyboard.py --device <COM_PORT> -c "exec(open('<PREFIX>_test_hello.py').read())"
```

- **Pass**: Output contains `HELLO_FROM_BOARD`

Clean up:
```bash
python scripts/pyboard.py --device <COM_PORT> -f rm :<PREFIX>_test_hello.py
```

### 3.6 Update `<PREFIX>_board_config.json`

Set:
```json
{
  "filesystem_ok": true
}
```

## Verification Criteria

- [ ] REPL responds to arithmetic
- [ ] `sys.platform` is `pyboard`
- [ ] `machine.freq()` output contains 64000000
- [ ] Filesystem listing works
- [ ] File upload + execute + delete round-trip succeeds
- [ ] `<PREFIX>_board_config.json` updated with `filesystem_ok: true`

## Output

REPL and filesystem are verified. The board is ready for peripheral testing. Proceed to `04-gpio.md`.
