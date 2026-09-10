#!/bin/sh
# One-time setup for macOS / Linux:  ./setup.sh
#
# The puzzles need only the Python standard library, so there is nothing to
# pip install. This script finds (or installs) Python 3.8+, pins it in .venv,
# prepares the candidate workspace, runs the self-test, and prints the command
# to run each puzzle on its own.
set -eu
cd "$(dirname "$0")"

py_ok() {
    "$1" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' >/dev/null 2>&1
}

PY=""
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 && py_ok "$candidate"; then
        PY="$(command -v "$candidate")"
        break
    fi
done

if [ -z "$PY" ]; then
    echo "No Python 3.8+ found on this machine."
    if ! command -v uv >/dev/null 2>&1; then
        printf "Install uv (standalone Python installer from astral.sh, no admin needed)? [y/N] "
        read -r reply
        case "$reply" in
            y|Y|yes|YES) ;;
            *)
                echo "Install Python 3.8+ yourself, then re-run ./setup.sh:"
                echo "  macOS:   brew install python   (or https://www.python.org/downloads/)"
                echo "  Ubuntu:  sudo apt install python3"
                exit 1
                ;;
        esac
        if command -v curl >/dev/null 2>&1; then
            curl -LsSf https://astral.sh/uv/install.sh | sh
        else
            wget -qO- https://astral.sh/uv/install.sh | sh
        fi
        PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
    fi
    uv python install 3.12
    PY="$(uv python find 3.12)"
fi

echo "Using $("$PY" -c 'import sys; print(sys.version.split()[0])') at $PY"

# A .venv copied over from another machine won't run here; rebuild it.
if [ -e .venv ] && ! .venv/bin/python -c 'pass' >/dev/null 2>&1; then
    rm -rf .venv
fi
# --without-pip: nothing to install, and it works on Debian/Ubuntu even when
# the python3-venv package is missing.
if [ ! -d .venv ]; then
    "$PY" -m venv --without-pip .venv
fi

chmod +x booth
./booth reset
./booth verify

echo
echo "Setup complete."
echo
echo "Run any puzzle on its own as a plain Python script (from this folder):"
for level in E M H; do
    for f in puzzles/"$level"*.py; do
        echo "  .venv/bin/python $f"
    done
done
echo "  Tip: run 'source .venv/bin/activate' once, then just: python puzzles/<file>.py"
echo "  A candidate's edited copy runs the same way: .venv/bin/python workspace/<file>.py"
echo
echo "Or use the booth tool:"
echo "  ./booth            list puzzles and commands"
echo "  ./booth show easy  put a random easy puzzle on screen"
echo "  ./booth key        staff answer key"
