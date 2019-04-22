import bs4
import requests
import sqlite3
import json
from collections import defaultdict


class MPrint():
    def __init__(self):
        self.base_url = "https://mprint.umich.edu/api"
        self.headers = {
            'Cookie': "_ga=GA1.2.616053654.1544826362; um_cookie_consent=na; _fbp=fb.1.1550675946885.680571453; gwlob=on; __utma=7269686.616053654.1544826362.1552843507.1552843507.1; __utmc=7269686; __utmz=7269686.1552843507.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); _gid=GA1.2.524913103.1555523731; cosign-mprint=wUWuvQzTuYLzLktNu-+0Eo6quk01m3Al3mzJHoZZVrSZUjWP+vqLJc3TpToFXrM8rTPPBJr6jiz8KdCuR8+KhRZV9UdMMtk7b+zNkhiMiS0V6aXxgh-7hi6V6wdA/1555708502"
        }
        self.database = 'db.sqlite'
        self.data = None

    def fetch_building_data(self):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS mprint_buildings;")
        c.execute(
            """CREATE TABLE IF NOT EXISTS mprint_buildings (
            id text PRIMARY KEY,
            name text NOT NULL,
            address text NOT NULL,
            latitude real NOT NULL,
            longitude real NOT NULL
            );"""
        )
        response = requests.request("GET", self.base_url+"/buildings", headers=self.headers)

        buildings_list = json.loads(response.text)['result']

        for building in buildings_list:
            c.execute(
                "INSERT INTO mprint_buildings (id, name, address, latitude, longitude) "
                "VALUES (?, ?, ?, ?, ?);",
                (building['id'],
                building['name'],
                building['address'],
                building['lat'],
                building['lng'],)
            )
        
        conn.commit()
        conn.close()
    
    def fetch_print_data(self):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS mprint_printers;")
        c.execute(
            """CREATE TABLE IF NOT EXISTS mprint_printers (
            name text PRIMARY KEY,
            class text NOT NULL,
            display_name text NOT NULL,
            location text NOT NULL,
            room text NOT NULL,
            floor_id text NOT NULL,
            building_id text NOT NULL,
            sub_unit text NOT NULL,
            unit text NOT NULL
            );"""
        )
        response = requests.request("GET", self.base_url+"/queues", headers=self.headers)
        
        printers_list = json.loads(response.text)['result']

        for printer in printers_list:
            c.execute(
                "INSERT INTO mprint_printers (name, class, display_name, location, room, floor_id, building_id, sub_unit, unit) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);",
                (printer['name'],
                printer['class'],
                printer['display_name'],
                printer['location'],
                printer['room'],
                printer['floor_id'],
                printer['building_id'],
                printer['sub_unit'],
                printer['unit'],
                )
            )
        
        conn.commit()
        conn.close()
    
    def fetch_floor_data(self):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS mprint_floors;")
        c.execute(
            """CREATE TABLE IF NOT EXISTS mprint_floors (
            id text NOT NULL,
            name text NOT NULL,
            level integer NOT NULL,
            building_id text NOT NULL,
            map_url text NOT NULL,
            PRIMARY KEY(id, level)
            );"""
        )
        response = requests.request("GET", self.base_url+"/floors", headers=self.headers)
        
        floors_list = json.loads(response.text)['result']

        for floor in floors_list:
            c.execute(
                "INSERT INTO mprint_floors (id, name, level, building_id, map_url) "
                "VALUES (?, ?, ?, ?, ?);",
                (floor['id'],
                floor['name'],
                floor['level'],
                floor['building_id'],
                floor['map_url'],
                )
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
        c.execute("""SELECT
                        b.id as building_id,
                        b.name as building_name,
                        b.address as building_address,
                        b.latitude,
                        b.longitude,
                        f.id as floor_id,
                        f.name as floor_name,
                        f.level as floor_level,
                        f.map_url as map_url,
                        p.name as printer_name,
                        p.class as printer_class,
                        p.display_name as printer_display_name,
                        p.location as printer_location,
                        p.room as printer_room,
                        p.sub_unit as printer_sub_unit,
                        p.unit as printer_unit
                    FROM mprint_buildings AS b
                    INNER JOIN mprint_floors AS f
                    INNER JOIN mprint_printers AS p
                    ON b.id = f.building_id AND f.id = p.floor_id;
                    """)
        self.data = c.fetchall()
        conn.close()
    
    def process_data(self):
        if self.data is None:
            self.load_data()
        
        building_printer_count = defaultdict(int)
        for row in self.data:
            building_printer_count[row['building_id']] += 1

        building_data = list()
        for row in self.data:
            building_data.append({
                'id': row['building_id'],
                'name': row['building_name'],
                'address': row['building_address'],
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'printers': building_printer_count[row['building_id']]
            })

        self.data_to_json(building_data)
    
    def data_to_json(self, data=None):
        with open('mprint.json', 'w') as f:
            if data is None:
                json.dump(self.data, f)
            else:
                json.dump(data, f)

if __name__ == '__main__':
    mprint = MPrint()
    # mprint.fetch_building_data()
    # mprint.fetch_print_data()
    # mprint.fetch_floor_data()
    # mprint.load_data()
    mprint.process_data()
    # mprint.data_to_json()