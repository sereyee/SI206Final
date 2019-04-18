from flask import Flask, render_template
import json
app = Flask(__name__)

@app.route('/')
def index():
    with open('data.json') as f:
        data = json.load(f)
    return render_template('index.jinja', data=data)

if __name__ == '__main__':
    app.run()
