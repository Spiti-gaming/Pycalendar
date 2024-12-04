import json

from flask import Flask, send_file
import subprocess

app = Flask(__name__)

with open("config/config.json") as f:
    configs = json.load(f)
    config = configs[0]

@app.route('/ical', methods=['GET'])
def get_ical():
    return send_file("ical/"+config['icsfile'], mimetype='text/calendar')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)