from flask import Flask, render_template
import json
app = Flask(__name__)

@app.route('/')
def index():
    with open('data.json') as f:
        data = json.load(f)

    coords_list = [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [restaurant["longitude"], restaurant["latitude"]]
                },
                "properties": {
                    "title": restaurant['name'],
                    "rating": int(restaurant["rating"]*2)
                }
            }
            for restaurant in data
        ]

    return render_template('index.jinja', restaurant_data=coords_list)

if __name__ == '__main__':
    app.run()
