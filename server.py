# server.py - HỖ TRỢ TẤT CẢ LỆNH + python3.12
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

# === HTML + Ô NHẬP + NÚT GỬI ===
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
        <input type="text" id="cmd" placeholder="ls, python3.12 CTOOL.py, pip install..." autofocus>
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
            write('\\nCTOOL TERMINAL PRO - HỖ TRỢ TẤT CẢ LỆNH!\\n', 'info');
            write('Dùng: python3.12 CTOOL.py | pip install | curl | run webhost | ps | stop\\n', 'info');
            write('LỆNH MẪU:\\n', 'info');
            write('  curl -o CTOOL.py https://raw.githubusercontent.com/C-Dev7929/Tools/refs/heads/main/main-xw.py\\n', 'info');
            write('  python3.12 CTOOL.py\\n', 'info');
            write('  pip install requests\\n', 'info');
            write('  run webhost\\n', 'info');
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

# === SHELL ===
master_fd = None
proc = None

def start_shell():
    global master_fd, proc
    master_fd, slave_fd = pty.openpty()
    # DÙNG bash + source .bashrc để dùng python3.12
    proc = subprocess.Popen(
        ['/bin/bash', '--rcfile', '/opt/render/project/src/.bashrc'],
        stdin=slave_fd, stdout=slave_fd, stderr=slave_fd,
        bufsize=0, preexec_fn=os.setsid, cwd='/opt/render/project/src'
    )

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
            socketio.emit('info', "Web chạy tại: http://localhost:5000")
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
