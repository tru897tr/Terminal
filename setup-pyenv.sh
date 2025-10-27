#!/bin/bash
set -e

echo "CÀI pyenv + Python 3.11, 3.12, 3.13..."

if [ ! -d "$HOME/.pyenv" ]; then
    curl https://pyenv.run | bash
fi

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

pyenv install 3.11.9 -s
pyenv install 3.12.7 -s
pyenv install 3.13.0 -s

echo "Python 3.11, 3.12, 3.13 đã sẵn sàng!"
