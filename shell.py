import subprocess
import os
import signal
import psutil

class ProcessManager:
    def __init__(self):
        self.processes = {}

    def start(self, name, cmd):
        if name in [p["name"] for p in self.processes.values()]:
            return f"[ERROR] '{name}' đã tồn tại!"
        try:
            proc = subprocess.Popen(
                cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, preexec_fn=os.setsid,
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
                    return f"[ERROR] Không dừng được"
        return f"[WARN] Không tìm thấy '{name}'"

    def list(self):
        if not self.processes:
            return "[INFO] Không có tiến trình nào."
        lines = ["[DANH SÁCH TIẾN TRÌNH]"]
        for pid, info in self.processes.items():
            try:
                p = psutil.Process(pid)
                cpu = p.cpu_percent()
                mem = p.memory_info().rss / 1024 / 1024
                lines.append(f"  • {info['name']} (PID: {pid}) | CPU: {cpu:.1f}% | RAM: {mem:.1f}MB")
            except:
                lines.append(f"  • {info['name']} (PID: {pid}) | [đã chết]")
        return "\n".join(lines)

manager = ProcessManager()
