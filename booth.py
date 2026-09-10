#!/usr/bin/env python3
"""Spot-the-bug booth: six Python puzzles (2 easy, 2 medium, 2 hard).

Staff drive this from the booth laptop; see README.md for the event-day flow.
Standard library only, so any Python 3.8+ runs it with nothing to install.
"""

import argparse
import difflib
import os
import random
import shlex
import shutil
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

ROOT = Path(__file__).resolve().parent
PUZZLE_DIR = ROOT / "puzzles"
SOLUTION_DIR = ROOT / "solutions"
WORKSPACE_DIR = ROOT / "workspace"
LEVELS = ("easy", "medium", "hard")
RUN_TIMEOUT = 10  # seconds; stops a candidate's accidental infinite loop


@dataclass(frozen=True)
class Puzzle:
    id: str
    level: str
    title: str
    filename: str
    expected: str  # what the program should print
    buggy_output: str  # what it prints as written
    bug_lines: Tuple[int, int]  # inclusive range, as numbered on the display
    bug_snippet: str  # text on bug_lines[0]; `verify` fails if line numbers drift
    why: str
    fix: str
    ask: str  # follow-up question for staff, with the answer to listen for

    @property
    def lines_label(self) -> str:
        first, last = self.bug_lines
        return f"Line {first}" if first == last else f"Lines {first} to {last}"

    @property
    def source(self) -> Path:
        return PUZZLE_DIR / self.filename

    @property
    def solution(self) -> Path:
        return SOLUTION_DIR / self.filename

    @property
    def workspace(self) -> Path:
        return WORKSPACE_DIR / self.filename


PUZZLES = [
    Puzzle(
        id="E1",
        level="easy",
        title="Cold weather stations",
        filename="E1_cold_weather_stations.py",
        expected="Stations at risk: 2",
        buggy_output="Stations at risk: 1",
        bug_lines=(6, 6),
        bug_snippet="if temp < -40:",
        why="The code uses <, so Resolute at exactly -40 is not counted and it prints 1.",
        fix="Use <= instead of <.",
        ask="Which station gets missed? (Resolute, sitting exactly on -40.)",
    ),
    Puzzle(
        id="E2",
        level="easy",
        title="Sea ice thickness",
        filename="E2_sea_ice_thickness.py",
        expected="150.0",
        buggy_output="130.0",
        bug_lines=(5, 5),
        bug_snippet="for i in range(1, len(thickness)):",
        why="The loop starts at index 1, so it skips the first reading and prints 130.0.",
        fix="range(len(thickness)), or just sum(thickness).",
        ask="Which reading is skipped? (The first one, 140. It is still counted in"
        " len(), so the average comes out low.)",
    ),
    Puzzle(
        id="M1",
        level="medium",
        title="Patrol logs",
        filename="M1_patrol_logs.py",
        expected="['Cambridge Bay']\n['Inuvik']",
        buggy_output="['Cambridge Bay']\n['Cambridge Bay', 'Inuvik']",
        bug_lines=(5, 5),
        bug_snippet="def log_stop(stop, log=[]):",
        why="Python creates the default list only once, when the function is defined."
        " Every call shares it, so the second line prints ['Cambridge Bay', 'Inuvik'].",
        fix="Use log=None, then inside the function add: if log is None: log = []",
        ask="When is the default value created? (Once, when the def statement runs."
        " It lives on the function object, in log_stop.__defaults__.)",
    ),
    Puzzle(
        id="M2",
        level="medium",
        title="Radar contacts",
        filename="M2_radar_contacts.py",
        expected="['unknown', 'unknown']",
        buggy_output="['unknown', 'friendly', 'unknown']",
        bug_lines=(4, 6),
        bug_snippet="for c in contacts:",
        why="Removing items from a list while looping over it makes the loop skip items."
        " It prints ['unknown', 'friendly', 'unknown'].",
        fix='contacts = [c for c in contacts if c != "friendly"]'
        "  (looping over a copy, for c in contacts[:], also works)",
        ask="Why does exactly one 'friendly' survive? (remove() shifts the later items"
        " left, but the loop's index still moves forward, so the item that slides into"
        " the gap is never checked.)",
    ),
    Puzzle(
        id="H1",
        level="hard",
        title="Surveillance sector grid",
        filename="H1_surveillance_sector_grid.py",
        expected="Scanned sectors: 1",
        buggy_output="Scanned sectors: 3",
        bug_lines=(4, 4),
        bug_snippet="grid = [[0] * 3] * 3",
        why="The outer * 3 makes 3 references to the same inner list, not 3 separate rows."
        " Changing one row changes all of them, so it prints 3.",
        fix="grid = [[0] * 3 for _ in range(3)]",
        ask="The inner [0] * 3 also copies references, so why is that one fine? (Ints"
        " are immutable. grid[0][0] = 1 replaces one slot rather than changing the 0."
        " The rows are all the same list object: grid[0] is grid[1] is True.)",
    ),
    Puzzle(
        id="H2",
        level="hard",
        title="Sensor buoy alerts",
        filename="H2_sensor_buoy_alerts.py",
        expected="Buoy B1 offline\nBuoy B2 offline\nBuoy B3 offline",
        buggy_output="Buoy B3 offline\nBuoy B3 offline\nBuoy B3 offline",
        bug_lines=(8, 8),
        bug_snippet='alerts.append(lambda: f"Buoy {buoy} offline")',
        why="The lambda looks up buoy when it is called, not when it is created. By then"
        ' the loop has finished and buoy is "B3", so it prints Buoy B3 offline three times.',
        fix='lambda buoy=buoy: f"Buoy {buoy} offline"',
        ask="Why does buoy=buoy fix it? (Default values are evaluated when the lambda is"
        " created, so each one keeps its own value. Without it, the closure holds the"
        " variable, not its value.)",
    ),
]


# --- terminal output -------------------------------------------------------


def _color_enabled() -> bool:
    if os.environ.get("NO_COLOR") or not sys.stdout.isatty():
        return False
    if os.name == "nt":
        os.system("")  # turns on ANSI escape handling in the Windows console
    return True


COLOR = _color_enabled()


def paint(text: str, *codes: str) -> str:
    if not COLOR or not codes:
        return text
    return "\033[" + ";".join(codes) + "m" + text + "\033[0m"


BOLD, DIM, RED, GREEN, YELLOW, CYAN = "1", "2", "31", "32", "33", "36"
LEVEL_COLOR = {"easy": GREEN, "medium": YELLOW, "hard": RED}


def header(p: Puzzle) -> str:
    level = paint(p.level.upper(), BOLD, LEVEL_COLOR[p.level])
    return f"{paint(p.id, BOLD)}  {level}  {paint(p.title, BOLD)}"


def rule() -> str:
    return paint("-" * 64, DIM)


def print_code(source: str, mark: Optional[Tuple[int, int]] = None) -> None:
    for number, line in enumerate(source.splitlines(), 1):
        marked = mark is not None and mark[0] <= number <= mark[1]
        gutter = paint(">", BOLD, RED) if marked else " "
        num = paint(f"{number:>2}", BOLD, RED) if marked else paint(f"{number:>2}", DIM)
        body = paint(line, CYAN) if line.lstrip().startswith("#") else line
        print(f" {gutter}{num}  {body}")


def print_block(label: str, text: str, *codes: str) -> None:
    print(paint(label, BOLD))
    for line in text.splitlines() or [""]:
        print("    " + paint(line, *codes))


def print_field(label: str, text: str) -> None:
    indent = " " * 12
    wrapped = textwrap.fill(text, width=76, initial_indent=indent, subsequent_indent=indent)
    print(paint(f"{label:<12}", BOLD) + wrapped[len(indent):])


# --- running code ----------------------------------------------------------


def normalize(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def run_file(path: Path) -> Tuple[str, str]:
    """Run a Python file with this interpreter. Returns (stdout, error text)."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    try:
        proc = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=RUN_TIMEOUT,
            env=env,
            cwd=str(path.parent),
        )
    except subprocess.TimeoutExpired:
        return "", f"Stopped after {RUN_TIMEOUT} seconds (infinite loop?)"
    error = proc.stderr.strip() if proc.returncode != 0 else ""
    return normalize(proc.stdout), error


# --- lookup ----------------------------------------------------------------


def find(key: str) -> Puzzle:
    """Look up a puzzle by id (E1), or pick a random one for a level name (easy)."""
    key = key.lower()
    if key in LEVELS:
        return random.choice([p for p in PUZZLES if p.level == key])
    for p in PUZZLES:
        if p.id.lower() == key:
            return p
    ids = ", ".join(p.id for p in PUZZLES)
    raise SystemExit(f"Unknown puzzle '{key}'. Use one of {ids}, or easy/medium/hard.")


def ensure_workspace(p: Puzzle, fresh: bool = False) -> Path:
    WORKSPACE_DIR.mkdir(exist_ok=True)
    if fresh or not p.workspace.exists():
        shutil.copyfile(p.source, p.workspace)
    return p.workspace


# --- commands --------------------------------------------------------------


def cmd_list(args: argparse.Namespace) -> int:
    print(paint("Spot the bug: Python puzzles", BOLD))
    print()
    for level in LEVELS:
        for p in (p for p in PUZZLES if p.level == level):
            print(f"  {header(p)}")
    print()
    print(paint("Commands", BOLD) + "  (IDs or easy/medium/hard; a level picks one at random)")
    commands = [
        ("show E1", "put the puzzle on the display, with line numbers"),
        ("run E1", "run the puzzle as written and compare to the expected output"),
        ("answer E1", "staff answer key: bug line, why, fix, follow-up question"),
        ("edit E1", "open an editable copy for a candidate to fix"),
        ("check E1", "run the candidate's copy: does it print the right thing?"),
        ("reset", "wipe all candidate copies before the next person"),
        ("key", "print every answer (e.g. `key > answers.txt` to print it out)"),
        ("verify", "self-test: confirms this machine is ready for the event"),
    ]
    for cmd, desc in commands:
        print(f"  {cmd:<11} {paint(desc, DIM)}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    p = find(args.puzzle)
    if COLOR and not args.no_clear:
        print("\033[2J\033[H", end="")
    print()
    print("  " + header(p))
    print(rule())
    print_code(p.source.read_text(encoding="utf-8"))
    print(rule())
    print(paint("  Which line has the bug, and why?", BOLD))
    print()
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    p = find(args.puzzle)
    print(header(p))
    output, error = run_file(p.source)
    print_block("Prints:", output or "(nothing)", YELLOW)
    if error:
        print_block("Error:", error, RED)
    print_block("Should print:", p.expected, GREEN)
    if output == p.expected and not error:
        print(paint("Matches. (Unexpected for the original puzzle; run `verify`.)", YELLOW))
    else:
        print(paint("Does not match. There's a bug in there somewhere.", BOLD, RED))
    return 0


def print_answer(p: Puzzle, with_code: bool = True) -> None:
    print(header(p))
    if with_code:
        print(rule())
        print_code(p.source.read_text(encoding="utf-8"), mark=p.bug_lines)
        print(rule())
    print_field("Bug", p.lines_label)
    print_field("Prints", p.buggy_output.replace("\n", " | "))
    print_field("Expected", p.expected.replace("\n", " | "))
    print_field("Why", p.why)
    print_field("Fix", p.fix)
    print_field("Ask why", p.ask)
    if p.level == "hard":
        print_field("Bonus", "Hard puzzle: bonus prize on top of the shirt if they explain it.")


def cmd_answer(args: argparse.Namespace) -> int:
    print_answer(find(args.puzzle))
    print()
    print(paint("Accept any correct fix. Right line + a real explanation = shirt.", DIM))
    return 0


def cmd_key(args: argparse.Namespace) -> int:
    for p in PUZZLES:
        print_answer(p, with_code=args.code)
        print()
    print("Accept any correct fix: many bugs have more than one valid solution.")
    print("Right line + an explanation of why it is wrong = shirt.")
    print('On hard puzzles, always ask "why?" and give the bonus for a real explanation.')
    return 0


def cmd_edit(args: argparse.Namespace) -> int:
    p = find(args.puzzle)
    path = ensure_workspace(p, fresh=args.fresh)
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")
    try:
        if editor:
            subprocess.Popen(shlex.split(editor) + [str(path)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-t", str(path)])
        elif os.name == "nt":
            subprocess.Popen(["notepad", str(path)])
        elif shutil.which("xdg-open"):
            subprocess.Popen(["xdg-open", str(path)])
        else:
            raise OSError("no editor found")
        print(f"Opened {path}")
    except OSError:
        print(f"Couldn't open an editor. Edit this file by hand:\n  {path}")
    print(f"When they're done, run:  check {p.id}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    p = find(args.puzzle)
    path = Path(args.file) if args.file else p.workspace
    if not path.exists():
        print(f"No edited copy of {p.id} yet. Start one with:  edit {p.id}")
        return 1
    print(header(p))
    print(paint(f"Checking {path}", DIM))

    original = p.source.read_text(encoding="utf-8").splitlines()
    edited = path.read_text(encoding="utf-8").splitlines()
    diff = list(difflib.unified_diff(original, edited, "original", "edited", lineterm="", n=0))
    print(paint("Changes:", BOLD))
    if not diff:
        print("    (none, the file is unchanged)")
    for line in diff[2:]:
        if line.startswith("+"):
            print("    " + paint(line, GREEN))
        elif line.startswith("-"):
            print("    " + paint(line, RED))
        else:
            print("    " + paint(line, DIM))

    output, error = run_file(path)
    print_block("Prints:", output or "(nothing)", YELLOW)
    if error:
        print_block("Error:", error, RED)
    if output == p.expected and not error:
        print(paint("PASS: correct output.", BOLD, GREEN))
        print(paint("Make sure it's a real fix (not a hardcoded print) and ask them why.", DIM))
        return 0
    print_block("Should print:", p.expected, GREEN)
    print(paint("Not yet: output doesn't match.", BOLD, RED))
    return 1


def cmd_reset(args: argparse.Namespace) -> int:
    targets = [find(key) for key in args.puzzles] if args.puzzles else PUZZLES
    for p in targets:
        ensure_workspace(p, fresh=True)
    names = ", ".join(p.id for p in targets)
    print(f"Fresh copies ready in {WORKSPACE_DIR} ({names}).")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    version = ".".join(str(n) for n in sys.version_info[:3])
    print(f"Python {version} at {sys.executable}")
    if sys.version_info < (3, 8):
        print(paint("Python 3.8 or newer is required.", BOLD, RED))
        return 1

    failures = 0
    for p in PUZZLES:
        problems: List[str] = []
        lines = p.source.read_text(encoding="utf-8").splitlines()
        first = p.bug_lines[0]
        if first > len(lines) or p.bug_snippet not in lines[first - 1]:
            problems.append(f"line {first} no longer contains {p.bug_snippet!r}")

        output, error = run_file(p.source)
        if error:
            problems.append(f"puzzle crashed: {error.splitlines()[-1]}")
        elif output != p.buggy_output:
            problems.append(f"puzzle printed {output!r}, answer key says {p.buggy_output!r}")

        output, error = run_file(p.solution)
        if error:
            problems.append(f"reference fix crashed: {error.splitlines()[-1]}")
        elif output != p.expected:
            problems.append(f"reference fix printed {output!r}, expected {p.expected!r}")

        status = paint("ok  ", BOLD, GREEN) if not problems else paint("FAIL", BOLD, RED)
        print(f"  {status}  {header(p)}")
        for problem in problems:
            print(f"        {paint(problem, RED)}")
        failures += bool(problems)

    if failures:
        print(paint(f"{failures} puzzle(s) failed verification.", BOLD, RED))
        return 1
    print(paint("All 6 puzzles verified. This machine is ready.", BOLD, GREEN))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="booth", description="Spot-the-bug Python puzzles for the event booth."
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="list puzzles and commands").set_defaults(func=cmd_list)

    show = sub.add_parser("show", help="display a puzzle with line numbers")
    show.add_argument("puzzle", help="E1..H2, or easy/medium/hard for a random pick")
    show.add_argument("--no-clear", action="store_true", help="don't clear the screen first")
    show.set_defaults(func=cmd_show)

    run = sub.add_parser("run", help="run a puzzle as written")
    run.add_argument("puzzle")
    run.set_defaults(func=cmd_run)

    answer = sub.add_parser("answer", help="show the answer for one puzzle")
    answer.add_argument("puzzle")
    answer.set_defaults(func=cmd_answer)

    key = sub.add_parser("key", help="print the full answer key")
    key.add_argument("--code", action="store_true", help="include each puzzle's code")
    key.set_defaults(func=cmd_key)

    edit = sub.add_parser("edit", help="open an editable copy of a puzzle")
    edit.add_argument("puzzle")
    edit.add_argument("--fresh", action="store_true", help="discard previous edits first")
    edit.set_defaults(func=cmd_edit)

    check = sub.add_parser("check", help="check an edited copy against the expected output")
    check.add_argument("puzzle")
    check.add_argument("file", nargs="?", help="file to check (default: the edit copy)")
    check.set_defaults(func=cmd_check)

    reset = sub.add_parser("reset", help="restore fresh copies for the next candidate")
    reset.add_argument("puzzles", nargs="*", help="puzzle IDs (default: all)")
    reset.set_defaults(func=cmd_reset)

    sub.add_parser("verify", help="self-test every puzzle").set_defaults(func=cmd_verify)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.command:
        return cmd_list(args)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
