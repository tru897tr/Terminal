# server.py - CÀI pyenv TRONG SHELL → CHẠY python CTOOL.py
from flask import Flask, render_template_string
from flask_socketio import SocketIO
import pty
import subprocess
import select
import os
import threading
import requests
import time
from shell import manager

app = Flask(__name__)
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    logger=True,
    engineio_logger=True
)

def keep_alive():
    url = os.environ.get('RENDER_EXTERNAL_URL')
    if url:
        def ping():
            while True:
                try:
                    requests.get(url, timeout=5)
                except:
                    pass
                time.sleep(300)
        threading.Thread(target=ping, daemon=True).start()

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>CTOOL TERMINAL PRO</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body, html { height:100%; background:#000; color:#0f0; font-family:'Courier New', monospace; }
        #output { width:100%; height:calc(100% - 60px); padding:15px; overflow-y:auto; font-size:16px; }
        #input-area { position:fixed; bottom:0; width:100%; background:#111; padding:10px; display:flex; gap:10px; }
        #cmd { flex:1; background:#000; color:#0f0; border:1px solid #0f0; padding:10px; font-size:16px; outline:none; }
        #send { background:#0f0; color:#000; border:none; padding:0 20px; font-weight:bold; cursor:pointer; }
        .cmd { color: #0ff; }
        .output { color: #fff; }
        .error { color: #f55; }
        .info { color: #ff5; }
    </style>
</head>
<body>
    <div id="output"></div>
    <div id="input-area">
        <input type="text" id="cmd" placeholder="python CTOOL.py, pip install..." autofocus>
        <button id="send">GỬI</button>
    </div>

    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <script>
        const socket = io({ transports: ['websocket'] });
        const output = document.getElementById('output');
        const input = document.getElementById('cmd');
        const sendBtn = document.getElementById('send');

        const write = (text, type = 'output') => {
            const div = document.createElement('div');
            div.className = type;
            div.innerHTML = text.replace(/\\n/g, '<br>').replace(/ /g, '&nbsp;');
            output.appendChild(div);
            output.scrollTop = output.scrollHeight;
        };

        const sendCommand = () => {
            const cmd = input.value.trim();
            if (!cmd) return;
            write('> ' + cmd, 'cmd');
            socket.emit('command', cmd);
            input.value = '';
        };

        sendBtn.onclick = sendCommand;
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') sendCommand();
        });

        socket.on('connect', () => {
            write('\\nCTOOL TERMINAL PRO - CHẠY MỌI TOOL!\\n', 'info');
            write('DÙNG: python CTOOL.py | pip install | curl | run webhost\\n', 'info');
            write('LỆNH MẪU:\\n', 'info');
            write('  curl -o CTOOL.py https://raw.githubusercontent.com/C-Dev7929/Tools/refs/heads/main/main-xw.py\\n', 'info');
            write('  python CTOOL.py\\n', 'info');
            input.focus();
        });

        socket.on('output', (data) => write(data, 'output'));
        socket.on('error', (data) => write(data, 'error'));
        socket.on('info', (data) => write(data, 'info'));
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

master_fd = None
proc = None

def start_shell():
    global master_fd, proc
    master_fd, slave_fd = pty.openpty()

    # === CÀI pyenv + python3.12 TRỰC TIẾP TRONG SHELL ===
    init_commands = [
        'export PYENV_ROOT="$HOME/.pyenv"',
        'export PATH="$PYENV_ROOT/bin:$PATH"',
        'eval "$(pyenv init -)"',
        'eval "$(pyenv virtualenv-init -)"',
        'if ! pyenv versions | grep -q "3.12.7"; then pyenv install 3.12.7; fi',
        'pyenv global 3.12.7',
        'alias python="python3.12"',
        'alias pip="python3.12 -m pip"',
        'echo "Python 3.12.7 đã sẵn sàng!"',
        'python --version'
    ]

    # Tạo shell với lệnh khởi tạo
    shell_cmd = '/bin/bash'
    proc = subprocess.Popen(
        [shell_cmd], stdin=slave_fd, stdout=slave_fd, stderr=slave_fd,
        bufsize=0, preexec_fn=os.setsid, cwd='/opt/render/project/src'
    )

    # Gửi lệnh khởi tạo
    for cmd in init_commands:
        os.write(master_fd, (cmd + '\n').encode('utf-8'))
        time.sleep(0.5)

    # Đọc output
    def read():
        while True:
            try:
                r, _, _ = select.select([master_fd], [], [], 1)
                if r:
                    data = os.read(master_fd, 1024).decode('utf-8', errors='ignore')
                    if data:
                        socketio.emit('output', data)
            except:
                break
        socketio.emit('info', '\\n[SYSTEM] Shell dừng. Tải lại trang!\\n')

    threading.Thread(target=read, daemon=True).start()

@socketio.on('command')
def handle_command(cmd):
    cmd = cmd.strip()
    if not cmd: return

    if cmd == "ps":
        socketio.emit('info', manager.list())
    elif cmd.startswith("run "):
        name = cmd[4:].strip()
        if name == "webhost":
            msg = manager.start("WebHost", "python webhost.py")
            socketio.emit('info', msg)
        else:
            socketio.emit('error', "Tool chưa có!")
    elif cmd.startswith("stop "):
        name = cmd[5:].strip()
        msg = manager.stop(name)
        socketio.emit('info', msg)
    else:
        if master_fd:
            try:
                os.write(master_fd, (cmd + '\n').encode('utf-8'))
            except:
                socketio.emit('error', "[ERROR] Lỗi gửi lệnh")

@socketio.on('connect')
def on_connect():
    global master_fd
    if master_fd is None:
        threading.Thread(target=start_shell).start()

if __name__ == '__main__':
    keep_alive()
    socketio.run(
        app,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 10000)),
        allow_unsafe_werkzeug=True
    )
