# server.py - Terminal Web + Multi-tool + Host Web
from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
import pty
import subprocess
import select
import os
import threading
import requests
import time
import signal
from shell import manager

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# === KEEP ALIVE ===
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

# === HTML TERMINAL ===
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>CTOOL TERMINAL PRO</title>
    <meta charset="utf-8">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body, html { height:100%; background:#000; color:#0f0; font-family:'Courier New', monospace; }
        #term { width:100%; height:100%; padding:15px; overflow-y:auto; line-height:1.5; font-size:14px; }
        .cmd { color: #0ff; }
        .output { color: #fff; }
        .error { color: #f55; }
        .info { color: #ff5; }
    </style>
</head>
<body>
    <div id="term"></div>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <script>
        const socket = io();
        const term = document.getElementById('term');
        let buffer = '';

        const write = (text, type = 'output') => {
            const div = document.createElement('div');
            div.className = type;
            div.innerHTML = text.replace(/\\n/g, '<br>').replace(/ /g, '&nbsp;');
            term.appendChild(div);
            term.scrollTop = term.scrollHeight;
        };

        socket.on('output', (data) => write(data, 'output'));
        socket.on('error', (data) => write(data, 'error'));
        socket.on('info', (data) => write(data, 'info'));
        socket.on('cmd', (data) => write(data, 'cmd'));

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                write('> ' + buffer, 'cmd');
                socket.emit('command', buffer.trim());
                buffer = '';
                e.preventDefault();
            } else if (e.key === 'Backspace') {
                buffer = buffer.slice(0, -1);
            } else if (e.key.length === 1) {
                buffer += e.key;
            }
            e.preventDefault();
        });

        socket.on('connect', () => {
            write('\\nCTOOL TERMINAL PRO - SIÊU MẠNH!\\n', 'info');
            write('HỖ TRỢ: pip, npm, curl, wget, python, node, host web, v.v.\\n', 'info');
            write('LỆNH MẪU:\\n', 'info');
            write('  curl -o tool.py https://...\\n', 'info');
            write('  python tool.py\\n', 'info');
            write('  run webhost\\n', 'info');
            write('  ps\\n', 'info');
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

# === SHELL + COMMAND ===
master_fd = None
proc = None

def start_shell():
    global master_fd, proc
    master_fd, slave_fd = pty.openpty()
    proc = subprocess.Popen(
        ['/bin/bash'],
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        bufsize=0,
        preexec_fn=os.setsid,
        cwd='/opt/render/project/src'
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
        socketio.emit('info', '\\n[SYSTEM] Shell dừng. Tải lại trang để khởi động lại.\\n')

    threading.Thread(target=read, daemon=True).start()

@socketio.on('command')
def handle_command(cmd):
    cmd = cmd.strip()
    if not cmd:
        return

    # === LỆNH ĐẶC BIỆT ===
    if cmd == "ps":
        socketio.emit('info', manager.list())
        return
    elif cmd.startswith("run "):
        name = cmd[4:].strip()
        if name == "webhost":
            msg = manager.start("Flask Web", "python webhost.py")
            socketio.emit('info', msg)
            socketio.emit('info', "Truy cập: https://your-app.onrender.com:5000 (dùng ngrok nếu cần)")
        else:
            socketio.emit('error', "Tool chưa định nghĩa. Tạo file và dùng: python file.py")
        return
    elif cmd.startswith("stop "):
        name = cmd[5:].strip()
        msg = manager.stop(name)
        socketio.emit('info', msg)
        return

    # === LỆNH THÔNG THƯỜNG ===
    if master_fd:
        try:
            os.write(master_fd, (cmd + '\n').encode('utf-8'))
        except:
            socketio.emit('error', "[ERROR] Không thể gửi lệnh")

@socketio.on('connect')
def on_connect():
    global master_fd
    if master_fd is None:
        threading.Thread(target=start_shell).start()
    # Khởi động web mẫu
    threading.Thread(target=lambda: manager.start("Flask Web", "python webhost.py")).start()

# === RUN ===
if __name__ == '__main__':
    keep_alive()
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
