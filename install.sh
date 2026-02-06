#!/usr/bin/env bash
# OpenFang installer - https://openfang.ai
# curl -fsSL https://openfang.ai/install.sh | bash
set -euo pipefail

INSTALL_DIR="${OPENFANG_DIR:-$HOME/openfang}"

# Install uv if missing
command -v uv &>/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# Clone or update
if [ -d "$INSTALL_DIR" ]; then
    git -C "$INSTALL_DIR" pull --ff-only
else
    git clone https://github.com/aidiss/openfang.git "$INSTALL_DIR"
fi

# Install as CLI tool
uv tool install "$INSTALL_DIR"

# Setup env
cd "$INSTALL_DIR"
[ ! -f .env ] && [ -f .env.example ] && cp .env.example .env

echo "
Done! Add your API key to $INSTALL_DIR/.env, then:

  openfang chat
"
