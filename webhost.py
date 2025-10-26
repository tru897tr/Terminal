# webhost.py - Host web server bất kỳ
from flask import Flask, jsonify
import threading
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Web Server đang chạy trên Render!</h1><p>Dùng terminal để host nhiều web khác.</p>"

@app.route('/api/status')
def status():
    return jsonify({"status": "OK", "time": time.time()})

def run_web():
    app.run(host='0.0.0.0', port=5000, use_reloader=False)

if __name__ == '__main__':
    run_web()
