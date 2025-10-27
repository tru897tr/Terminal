# shell.py - Quản lý tiến trình chạy ngầm
import subprocess
import os
import signal
import psutil
import json
import time

STATE_FILE = "/opt/render/project/src/process_state.json"

class ProcessManager:
    def __init__(self):
        self.processes = {}
        self.load_state()

    def start(self, name, cmd):
        if name in [p["name"] for p in self.processes.values()]:
            return f"[ERROR] '{name}' đã tồn tại!"
        try:
            # Dùng nohup + & để chạy ngầm
            full_cmd = f"nohup {cmd} > {name}.log 2>&1 & echo $!"
            proc = subprocess.Popen(full_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd='/opt/render/project/src')
            time.sleep(1)
            pid = int(proc.stdout.read().decode().strip())
            self.processes[pid] = {"proc": None, "name": name, "cmd": cmd, "pid": pid}
            self.save_state()
            return f"[OK] Đã chạy ngầm '{name}' (PID: {pid})"
        except Exception as e:
            return f"[ERROR] {e}"

    def stop(self, name):
        for pid, info in list(self.processes.items()):
            if info["name"] == name:
                try:
                    os.kill(pid, signal.SIGTERM)
                    del self.processes[pid]
                    self.save_state()
                    return f"[OK] Đã dừng '{name}'"
                except:
                    return f"[ERROR] Không dừng được"
        return f"[WARN] Không tìm thấy '{name}'"

    def stop_all(self):
        for pid in list(self.processes.keys()):
            try:
                os.kill(pid, signal.SIGTERM)
            except:
                pass
        self.processes.clear()
        self.save_state()
        # Xóa log
        for f in os.listdir('/opt/render/project/src'):
            if f.endswith('.log'):
                os.remove(f)
        return "[OK] Đã dừng tất cả & xóa dữ liệu!"

    def list(self):
        if not self.processes:
            return "[INFO] Không có tiến trình nào."
        lines = ["[DANH SÁCH TIẾN TRÌNH NGẦM]"]
        for pid, info in self.processes.items():
            try:
                p = psutil.Process(pid)
                cpu = p.cpu_percent()
                mem = p.memory_info().rss / 1024 / 1024
                lines.append(f"  • {info['name']} (PID: {pid}) | CPU: {cpu:.1f}% | RAM: {mem:.1f}MB")
            except:
                lines.append(f"  • {info['name']} (PID: {pid}) | [đã chết]")
        return "\n".join(lines)

    def save_state(self):
        state = {str(pid): {"name": info["name"], "cmd": info["cmd"]} for pid, info in self.processes.items()}
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)

    def load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    state = json.load(f)
                for pid_str, info in state.items():
                    pid = int(pid_str)
                    if psutil.pid_exists(pid):
                        self.processes[pid] = {"proc": None, "name": info["name"], "cmd": info["cmd"], "pid": pid}
            except:
                pass

manager = ProcessManager()
