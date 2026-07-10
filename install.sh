#!/bin/sh
# MysticAgent installer — curl -fsSL https://raw.githubusercontent.com/terlikk/mystic-agent/main/install.sh | sh
# Installs into ~/.mystic-agent/venv and links the CLI into ~/.local/bin.
set -eu

REPO="https://github.com/terlikk/mystic-agent.git"
APP_DIR="${MYSTIC_HOME:-$HOME/.mystic-agent}"
VENV="$APP_DIR/venv"
BIN_DIR="$HOME/.local/bin"

say() { printf '%s\n' "$*"; }

say ""
say "  MysticAgent — instalacja"
say "  ------------------------"

# 1. find python >= 3.11
PY=""
for cand in python3.13 python3.12 python3.11 python3; do
    if command -v "$cand" >/dev/null 2>&1; then
        if "$cand" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
            PY="$cand"
            break
        fi
    fi
done
if [ -z "$PY" ]; then
    say "✗ Potrzebny Python 3.11+ (np. brew install python / apt install python3)"
    exit 1
fi
say "✓ python: $($PY --version 2>&1)"

# 2. venv + install from the repo (core/ subdirectory)
say "→ instaluję do $VENV …"
"$PY" -m venv "$VENV"
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet "mystic-agent @ git+$REPO#subdirectory=core"

# 3. link the CLI
mkdir -p "$BIN_DIR"
ln -sf "$VENV/bin/mystic-agent" "$BIN_DIR/mystic-agent"
say "✓ zainstalowano: $BIN_DIR/mystic-agent"

case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *)
        say ""
        say "⚠  $BIN_DIR nie jest w PATH — dodaj do ~/.zshrc lub ~/.bashrc:"
        say "   export PATH=\"\$HOME/.local/bin:\$PATH\""
        ;;
esac

say ""
say "Gotowe. Wystartuj agenta:"
say ""
say "   mystic-agent start"
say ""
say "Przy pierwszym starcie agent poprosi o klucz API i token bota Telegram —"
say "wszystko zostaje w szyfrowanym sejfie na tej maszynie."
