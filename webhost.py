from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Web Server đang chạy!</h1><p>Port: 5000</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
