import requests
import sqlite3
import json

class Yelp:
    def __init__(self):
        self.database = 'db.sqlite'
        self.data = None
    
    def fetch_data(self):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS yelp;")
        c.execute(
            "CREATE TABLE IF NOT EXISTS yelp ("
            " id text PRIMARY KEY,"
            " name text NOT NULL,"
            " review_count integer NOT NULL,"
            " rating real NOT NULL,"
            " latitude real NOT NULL,"
            " longitude real NOT NULL);"
        )
        
        url = "https://api.yelp.com/v3/businesses/search"

        headers = {
            'Authorization': "Bearer wNpy34J4iJq4QgESKC0-BgpPebq7sB8gZcClBeq0a-sMhW-NkrEvdlPK8qyHPk0Si9GXa4f6QBRfFr2mrAlI7hUhoG3kLacxY49VX4Mc7tMKcrlCY2PlRmjWusu3XHYx",
            }
        limit = 20
        offset = 0

        while True:
            querystring = {
                "term": "restaurants",
                "location": "Ann Arbor",
                "limit": limit,
                "offset": offset
            }
            response = requests.request("GET", url, headers=headers, params=querystring)
            
            restaurant_list = json.loads(response.text)['businesses']

            if not restaurant_list:
                break
            print('Processing {} restaurants'.format(len(restaurant_list)))
            for restaurant in restaurant_list:
                c.execute(
                    "INSERT INTO yelp (id, name, review_count, rating, latitude, longitude) "
                    "VALUES (?, ?, ?, ?, ?, ?);",
                    (restaurant['id'],
                    restaurant['name'],
                    restaurant['review_count'],
                    restaurant['rating'],
                    restaurant['coordinates']['latitude'],
                    restaurant['coordinates']['longitude'],)
                )

            offset += limit

        conn.commit()
        conn.close()

    def load_data(self):
        conn = sqlite3.connect(self.database)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * from yelp;")
        self.data = c.fetchall()
        conn.close()

    def data_to_mapbox_json(self):
        coords_list = [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [restaurant["longitude"], restaurant["latitude"]]
                },
                "properties": {
                    "title": restaurant['name'],
                    # "icon": "monument"
                }
            }
            for restaurant in self.data
        ]
        with open('data.json', 'w') as f:
            json.dump(coords_list, f)

if __name__ == '__main__':
    yelp = Yelp()
    yelp.fetch_data()
    yelp.load_data()
    yelp.data_to_mapbox_json()
