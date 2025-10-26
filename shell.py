# shell.py - Quản lý nhiều tiến trình + shell
import subprocess
import os
import signal
import psutil
from threading import Thread
import time

class ProcessManager:
    def __init__(self):
        self.processes = {}  # {pid: {"proc": proc, "name": name, "cmd": cmd}}

    def start(self, name, cmd):
        if name in [p["name"] for p in self.processes.values()]:
            return f"[ERROR] Tiến trình '{name}' đã tồn tại!"

        try:
            proc = subprocess.Popen(
                cmd,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid,
                cwd='/opt/render/project/src'
            )
            self.processes[proc.pid] = {"proc": proc, "name": name, "cmd": cmd}
            return f"[OK] Đã chạy '{name}': {cmd}"
        except Exception as e:
            return f"[ERROR] {e}"

    def stop(self, name):
        for pid, info in list(self.processes.items()):
            if info["name"] == name:
                try:
                    os.killpg(os.getpgid(pid), signal.SIGTERM)
                    del self.processes[pid]
                    return f"[OK] Đã dừng '{name}'"
                except:
                    return f"[ERROR] Không thể dừng '{name}'"
        return f"[WARN] Không tìm thấy '{name}'"

    def list(self):
        if not self.processes:
            return "[INFO] Chưa có tiến trình nào chạy."
        lines = ["[RUNNING PROCESSES]"]
        for pid, info in self.processes.items():
            cpu = psutil.Process(pid).cpu_percent()
            mem = psutil.Process(pid).memory_info().rss / 1024 / 1024
            lines.append(f"  • {info['name']} (PID: {pid}) | CPU: {cpu:.1f}% | RAM: {mem:.1f}MB")
        return "\n".join(lines)

    def output_reader(self, proc, callback):
        for line in iter(proc.stdout.readline, b''):
            if line:
                callback(line.decode('utf-8', errors='ignore'))
        proc.stdout.close()

    def error_reader(self, proc, callback):
        for line in iter(proc.stderr.readline, b''):
            if line:
                callback("[ERR] " + line.decode('utf-8', errors='ignore'))
        proc.stderr.close()

manager = ProcessManager()
