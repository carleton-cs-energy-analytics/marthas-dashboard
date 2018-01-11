import pandas as pd
import requests


class API:
    datecolumns = ['pointtimestamp']

    def __init__(self, url='http://energycomps.its.carleton.edu/api/index.php/'):
        self.base_url = url

    def buildings(self):
        """
        :return: pd.Series [name, buildingid]
        """
        return self.query_url(['buildings'])

    def building(self, name):
        """
        :param name: eg, 'LDC'
        :return: pd.Series [name, id]
        """
        return self.query_url(['building', name])

    def building_rooms(self, building_id):
        """
        :param building_id:
        :return: pd.DataFrame [buildingid, id, name]
        """
        return self.query_url(['building', building_id, 'rooms'])

    def building_points(self, building_id):
        """
        :param building_id:
        :return: pd.DataFrame [description, id, name, pointsourceid, pointtypeid, roomid]
        """
        return self.query_url(['building', building_id, 'points'])

    def building_points_by_type(self, building_id, point_type):
        """
        :param building_id: eg, '4'
        :param point_type: ??
        :return:
        """
        return self.query_url(['building', building_id, 'points', point_type])

    def point_values(self, point_id, start, end):
        """
        :param point_id: eg, '528'
        :param start: eg, '2016-08-18'
        :param end: eg, '2017-08-19'
        :return: pd.DataFrame [factor, id, name, pointid, pointtimestamp, pointvalue, returntype, units]
        """
        return self.query_url(['values', 'point', point_id, start, end])

    def point_value(self, point_id, timestamp):
        """
        :param point_id: eg, '528'
        :param timestamp: ??
        :return:
        """
        return self.query_url(['value', 'point', point_id, timestamp])

    def building_values_in_range(self, building_id, start, end):
        """
        :param building_id:
        :param start:
        :param end:
        :return: pd.DataFrame [factor, id, name, pointid, pointtimestamp, pointvalue, returntype, units]
        """
        return self.query_url(['values', 'building', building_id, start, end])

    def building_values_in_range_by_type(self, building_id, start, end, point_type):
        """
        :param building_id: eg, '4'
        :param start: eg, '2016-08-18'
        :param end: eg, '2017-08-19'
        :param point_type: ??
        :return:
        """
        return self.query_url(['values', 'building', building_id, start, end, point_type])

    def query_url(self, route_params):
        endpoint = "/".join(route_params)
        url = self.base_url + endpoint
        r = requests.get(url)

        try:
            df = pd.read_json(r.text)
        except ValueError:
            df = pd.read_json(r.text, typ='series')

        for col in self.datecolumns:
            if col in df:
                df[col] = pd.to_datetime(df[col])
        return df

# Just for experimenting!
if __name__ == "__main__":
    api = API()

    build = api.buildings()
    print(build)

    pts = api.building_points('4')
    print(pts)

    data = api.point_values('511', '2016-08-18', '2017-08-19')
    print(data)
