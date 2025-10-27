# .bashrc - Kích hoạt pyenv + python3.12
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv global 3.12.7

# Alias
alias python="python3.12"
alias pip="python3.12 -m pip"
