#!/bin/bash
set -e

echo "=== CÀI pyenv VÀO $HOME/.pyenv ==="

if [ ! -d "$HOME/.pyenv" ]; then
    echo "Cài pyenv..."
    curl https://pyenv.run | bash
fi

if ! "$HOME/.pyenv/bin/pyenv" versions | grep -q "3.12.7"; then
    echo "Cài Python 3.12.7..."
    "$HOME/.pyenv/bin/pyenv" install 3.12.7
fi

"$HOME/.pyenv/bin/pyenv" global 3.12.7

cat > ~/.bashrc << 'EOF'
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv global 3.12.7

alias python3.12="$PYENV_ROOT/versions/3.12.7/bin/python"
alias python3.11="$PYENV_ROOT/versions/3.11.9/bin/python"
alias python="python3.12"
alias pip="python3.12 -m pip"
EOF

echo "Python 3.12.7 đã sẵn sàng: $(python3.12 --version)"
