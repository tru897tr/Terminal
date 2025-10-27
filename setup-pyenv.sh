#!/bin/bash
set -e

echo "=== CÀI pyenv VÀO $HOME/.pyenv ==="

# Cài pyenv nếu chưa có
if [ ! -d "$HOME/.pyenv" ]; then
    echo "Cài pyenv..."
    curl https://pyenv.run | bash
fi

# Cài Python 3.12.7 nếu chưa có
if ! "$HOME/.pyenv/bin/pyenv" versions | grep -q "3.12.7"; then
    echo "Cài Python 3.12.7..."
    "$HOME/.pyenv/bin/pyenv" install 3.12.7
fi

# Dùng Python 3.12.7
"$HOME/.pyenv/bin/pyenv" global 3.12.7

echo "Python 3.12.7 đã sẵn sàng tại $HOME/.pyenv/versions/3.12.7/bin/python"
