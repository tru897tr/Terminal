#!/bin/bash
set -e

echo "=== CÀI VÀ KÍCH HOẠT pyenv + Python 3.12 ==="

# === CÀI pyenv NẾU CHƯA CÓ ===
if [ ! -d "$HOME/.pyenv" ]; then
    echo "Cài pyenv..."
    curl https://pyenv.run | bash
fi

# === CẬP NHẬT .bashrc ===
cat > ~/.bashrc << 'EOF'
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv global 3.12.7 2>/dev/null || true
alias python="python3.12"
alias pip="python3.12 -m pip"
EOF

# === KÍCH HOẠT pyenv ===
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# === CÀI Python 3.12.7 NẾU CHƯA CÓ ===
if ! pyenv versions | grep -q "3.12.7"; then
    echo "Cài Python 3.12.7..."
    pyenv install 3.12.7
fi

# === DÙNG Python 3.12.7 ===
pyenv global 3.12.7

# === KIỂM TRA ===
echo "Python version: $(python --version)"
echo "pip version: $(pip --version | head -n1)"

echo "=== pyenv SẴN SÀNG! ==="
