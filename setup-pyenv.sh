#!/bin/bash
set -e

echo "KÍCH HOẠT pyenv + python3.12..."

# Load pyenv
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# Dùng Python 3.12
pyenv global 3.12.7

# Alias
export PYTHON=python3.12
export PIP="python3.12 -m pip"

echo "python = $(python --version)"
