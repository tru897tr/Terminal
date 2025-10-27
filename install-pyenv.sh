#!/bin/bash
set -e

echo "CÀI pyenv + Python 3.12..."

# Cài pyenv
curl https://pyenv.run | bash

# Thêm vào PATH
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# Cài Python 3.12.7
pyenv install 3.12.7 -s
pyenv global 3.12.7

# Tạo alias
echo 'alias python="python3.12"' >> ~/.bashrc
echo 'alias pip="python3.12 -m pip"' >> ~/.bashrc

echo "Python 3.12 đã sẵn sàng!"
python --version
