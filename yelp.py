import requests
import sqlite3
import json

class Yelp:
    def __init__(self):
        self.database = 'db.sqlite'
        self.data = None
        self.calculation = None 
    
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
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        conn = sqlite3.connect(self.database)
        conn.row_factory = dict_factory
        c = conn.cursor()
        c.execute("SELECT * from yelp;")
        self.data = c.fetchall()
        c.execute("SELECT avg(latitude), avg(longitude) FROM yelp;")
        self.calculation = c.fetchall()
        conn.close()

    def data_to_json(self):
        with open('yelp.json', 'w') as f:
            json.dump(self.data, f)

    def data_to_json_two(self):
        with open('yelp_calc.json', 'w') as f:
            json.dump(self.calculation, f)

if __name__ == '__main__':
    yelp = Yelp()
    yelp.fetch_data()
    yelp.load_data()
    yelp.data_to_json()
    yelp.data_to_json_two()
