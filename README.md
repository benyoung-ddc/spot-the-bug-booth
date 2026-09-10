# Spot the Bug: Python booth puzzles

Six short Python programs, each with exactly one bug and a clear expected output:
2 easy, 2 medium, 2 hard. With two puzzles per level you can rotate them during
the event so answers don't spread.

| ID | Level  | Puzzle                   | Concept                              |
|----|--------|--------------------------|--------------------------------------|
| E1 | easy   | Cold weather stations    | `<` vs `<=` boundary                 |
| E2 | easy   | Sea ice thickness        | off-by-one `range` start             |
| M1 | medium | Patrol logs              | mutable default argument             |
| M2 | medium | Radar contacts           | mutating a list while iterating      |
| H1 | hard   | Surveillance sector grid | `[[0] * 3] * 3` aliases one row      |
| H2 | hard   | Sensor buoy alerts       | late-binding closures in a loop      |

## Setup on a new machine

Needs **Python 3.8 or newer** and nothing else: everything uses the standard
library, so there is nothing to `pip install`. Copy this folder over (you can
skip `.venv/` and `workspace/`), then:

**macOS / Linux**

```sh
./setup.sh
```

**Windows**: double-click `setup.bat` (or run it from a terminal).

Setup finds a suitable Python, pins it in `.venv/`, gets the candidate
workspace ready, and runs a self-test. You're ready when it prints
`All 6 puzzles verified. This machine is ready.`

If the machine has no Python, setup offers to install one: through
[uv](https://docs.astral.sh/uv/) on macOS/Linux (no admin rights needed) or
`winget` on Windows. Setup is safe to re-run at any time.

## Running a puzzle on its own

Every puzzle is a plain Python script with no booth tooling, so it runs
directly and prints exactly what the buggy code prints. From this folder:

```sh
.venv/bin/python puzzles/E1_cold_weather_stations.py      # macOS / Linux
.venv\Scripts\python puzzles\E1_cold_weather_stations.py  # Windows
```

Setup prints this command for all six puzzles. To skip the `.venv/...` prefix,
activate the environment once per terminal (`source .venv/bin/activate`, or
`.venv\Scripts\activate` on Windows), then run `python puzzles/<file>.py`. Any
Python 3.8+ works too, e.g. `python3 puzzles/E1_cold_weather_stations.py`.
A candidate's edited copy runs the same way, from `workspace/`.

## Running the booth

Use `./booth <command>` on macOS/Linux, or `booth <command>` on Windows.

| Command            | What it does                                                         |
|--------------------|----------------------------------------------------------------------|
| `booth`            | List puzzles and commands                                            |
| `booth show E1`    | Clear the screen and show the puzzle with line numbers (for the display) |
| `booth show hard`  | Same, but picks a random puzzle from that level                      |
| `booth run E1`     | Run the puzzle as written: what it prints vs. what it should print   |
| `booth answer E1`  | Staff answer: bug line highlighted, why, fix, and a follow-up question |
| `booth edit E1`    | Open an editable copy (in `workspace/`) for a candidate to fix       |
| `booth check E1`   | Show the candidate's changes and whether it now prints the right output |
| `booth reset`      | Restore fresh copies for the next candidate                          |
| `booth key`        | Full answer key for every puzzle. `booth key > answers.txt` to print it |
| `booth verify`     | Self-test: every bug reproduces and every reference fix works        |

A typical round:

1. `booth show medium`: the candidate reads the code on screen.
2. They name the line and explain the bug. Check with `booth answer M2` on a
   second terminal, or a printed `booth key`.
3. Optional: `booth edit M2` to let them type the fix, then `booth check M2`.
4. `booth reset` before the next person.

`check` compares output only, so read the diff it shows. A hardcoded
`print("150.0")`, or E1 changed to `< -39`, "passes" without being a real fix.

## Tips for running these

- **Accept any correct fix.** Many bugs have more than one valid solution. If
  the candidate finds the right line and explains why it is wrong, give them
  the shirt.
- **Ask "why?" on the hard ones.** Anyone can guess a line number. Their
  explanation is where you learn who really understands Python, and it starts
  a good conversation. `booth answer` gives you a follow-up question for each
  puzzle, with the answer to listen for.
- **Give a bonus for hard puzzles**, for example a sticker pack or a direct
  chat with an engineer on top of the shirt.
- **Line numbers are only on the display.** The files in `puzzles/` have no
  line numbers, so they run as-is. `booth show` adds the numbers, and they
  match the answer key.

## Layout

```
puzzles/     the six buggy programs (never edited; the pristine originals)
solutions/   one reference fix each, used by `booth verify`
workspace/   candidates' editable copies (created by setup / `booth reset`)
booth.py     the runner, and the answer key (the PUZZLES list at the top)
booth, booth.bat     launchers that use .venv when it exists
setup.sh, setup.bat  one-time setup
```

If you edit a puzzle, update its entry in `booth.py` and its file in
`solutions/`, then run `booth verify`. It fails if the documented bug line,
the buggy output, or the fixed output no longer match.
