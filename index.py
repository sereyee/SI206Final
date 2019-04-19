from flask import Flask, render_template
import json
app = Flask(__name__)

@app.route('/')
def index():
    with open('yelp.json') as f:
        yelp_data = json.load(f)
    with open('dpss.json') as f:
        dpss_data = json.load(f)

    yelp_coords_list = [
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
            for restaurant in yelp_data
        ]
    dpss_coords_list = [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [crime["longitude"], crime["latitude"]]
                },
                "properties": {
                    "description": crime['description']
                    # "rating": int(restaurant["rating"]*2)
                }
            }
            for crime in dpss_data
        ]

    return render_template('index.jinja', yelp_data=yelp_coords_list, dpss_data=dpss_coords_list)
