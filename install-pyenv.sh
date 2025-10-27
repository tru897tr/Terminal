#!/bin/bash
set -e

echo "CÀI pyenv + Python 3.12..."

# Cài pyenv
if [ ! -d "$HOME/.pyenv" ]; then
    curl https://pyenv.run | bash
fi

# Cập nhật PATH
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

# Cài Python 3.12.7
~/.pyenv/bin/pyenv install 3.12.7 -s
~/.pyenv/bin/pyenv global 3.12.7

# Alias
echo 'alias python="python3.12"' >> ~/.bashrc
echo 'alias pip="python3.12 -m pip"' >> ~/.bashrc

echo "Python 3.12 đã cài!"
