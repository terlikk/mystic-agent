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
say "  MysticAgent — instaluję, chwilkę…"

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

# 2. venv + install from the repo (core/ subdirectory), quietly.
# --no-cache-dir + --upgrade --force-reinstall: always build the latest
# source, never serve a stale wheel cached under the same version.
"$PY" -m venv "$VENV"
"$VENV/bin/pip" install --quiet --disable-pip-version-check --upgrade pip >/dev/null 2>&1
"$VENV/bin/pip" install --quiet --disable-pip-version-check --upgrade \
    --force-reinstall --no-cache-dir \
    "mystic-agent @ git+$REPO#subdirectory=core" >/dev/null 2>&1

# 3. link the CLI
mkdir -p "$BIN_DIR"
ln -sf "$VENV/bin/mystic-agent" "$BIN_DIR/mystic-agent"

case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *)
        say ""
        say "⚠  $BIN_DIR nie jest w PATH — dodaj do ~/.zshrc lub ~/.bashrc:"
        say "   export PATH=\"\$HOME/.local/bin:\$PATH\""
        ;;
esac

say ""
say "  ✓ Gotowe. Odpal agenta:"
say ""
say "      mystic-agent start"
say ""
say "  Zobaczysz duży napis MYSTIC AGENT, a przy pierwszym uruchomieniu"
say "  krótką konfigurację: klucz AI · bot Telegram · osobowość · imię."
say "  Potem panel sterowania czeka w przeglądarce: http://127.0.0.1:7700"
say ""
