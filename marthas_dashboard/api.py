import pandas as pd
import requests
class API:
    datecolumns = ['pointtimestamp']
    def __init__(self, url = 'http://energycomps.its.carleton.edu/api/index.php/'):
        self.base_url = url

    def buildings(self):
        return self.query_url(['buildings'])

    def building(self, name):
        return self.query_url(['building', name])

    def building_rooms(self, building_id):
        return self.query_url(['building', building_id, 'rooms'])

    def building_points(self, building_id):
        return self.query_url(['building', building_id, 'points'])

    def building_points_by_type(self, building_id, point_type):
        return self.query_url(['building', building_id, 'points', point_type])

    def point_values(self, point_id, start, end):
        return self.query_url(['values', 'point', point_id, start, end])

    def point_value(self, point_id, timestamp):
        return self.query_url(['value', 'point', point_id, timestamp])

    def building_values_in_range(self, building_id, start, end):
        return self.query_url(['values', 'building', building_id, start, end])

    def building_values_in_range_by_type(self, building_id, start, end, point_type):
        return self.query_url(['values', 'building', building_id, start, end, point_type])

    def query_url(self, route_params):
        endpoint = "/".join(route_params);
        url = self.base_url + endpoint
        r = requests.get(url)
        df =  pd.read_json(r.text)
        for col in self.datecolumns:
            if col in df:
                df[col] = pd.to_datetime(df[col])
        return df
