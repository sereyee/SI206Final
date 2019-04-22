import requests
import sqlite3
import json
from datetime import timedelta, date
from collections import defaultdict


def date_range(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

class DPSS:
    def __init__(self):
        self.url = "https://dpss.umich.edu/api/GetCrimeLogCache"
        self.database = 'db.sqlite'
        self.data = None
        self.start_date = date(2019, 1, 1)
        self.end_date = date(2019, 4, 20)

    def fetch_data(self):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS dpss;")
        c.execute(
            """CREATE TABLE IF NOT EXISTS dpss (
            id text PRIMARY KEY,
            date text NOT NULL,
            description text NOT NULL,
            location text NOT NULL,
            address text NOT NULL,
            latitude real NOT NULL,
            longitude real NOT NULL);"""
        )

        for single_date in date_range(self.start_date, self.end_date):
            params = {
                'date': single_date.strftime("%m/%d/%Y")
            }
            response = requests.request("GET", self.url, params=params)
            
            crime_list = json.loads(response.text)['data']

            if not crime_list:
                continue

            print('Processing {} crimes on {}'.format(len(crime_list), single_date.strftime("%m/%d/%Y")))
            for crime in crime_list:
                if c.execute("SELECT EXISTS( SELECT 1 FROM dpss WHERE id = ? );", (crime['id'],)).fetchone()[0]:
                    continue

                if 'latitude' not in crime or 'longitude' not in crime:
                    continue

                c.execute(
                    "INSERT INTO dpss (id, date, description, location, address, latitude, longitude) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?);",
                    (crime['id'],
                    crime['date'],
                    crime['description'],
                    crime['location'],
                    crime['address'],
                    crime['latitude'],
                    crime['longitude'],)
                )

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
        c.execute("SELECT address, latitude, longitude, count(*) AS `count` FROM dpss GROUP BY address;")
        self.data = c.fetchall()
        conn.close()
    
    def data_to_json(self, data=None):
        with open('dpss.json', 'w') as f:
            if data is None:
                json.dump(self.data, f)
            else:
                json.dump(data, f)

if __name__ == '__main__':
    dpss = DPSS()
    dpss.fetch_data()
    dpss.load_data()
    dpss.data_to_json()
