import requests
import json


class COVIDUpdate:
    def __init__(self, rest_url):
        self.rest_url = rest_url

    def check(self, areas):
        data = []
        dates = set()
        response = requests.get(self.rest_url, verify=True)
        if response.ok:
            response_data = json.loads(response.content)
            features = response_data['features']
            for feature in features:
                if self.in_area(feature, areas):
                    dates.add(self.LAST_UPDATE(feature))
                    gf = self.GEN(feature)
                    bf = self.BEZ(feature)
                    c7p100 = round(self.cases7_per_100k(feature), 1)
                    data.append(str(gf) + ' (' + str(bf) + '): ' + str(c7p100))
        data.sort()
        return ', '.join(dates) + ': ' + ', '.join(data)

    def cases7_per_100k(self, feature):
        return feature['attributes']['cases7_per_100k']

    def in_area(self, feature, areas):
        f_gen = feature['attributes']['GEN']
        f_bez = feature['attributes']['BEZ']
        for area in areas:
            gen = area['GEN']
            bez = area['BEZ']
            if gen == f_gen and bez == f_bez:
                return area
        return None

    def GEN(self, feature):
        return feature['attributes']['GEN']

    def BEZ(self, feature):
        return feature['attributes']['BEZ']

    def LAST_UPDATE(self, feature):
        return feature['attributes']['last_update']


if __name__ == "__main__":
    target_areas = [{'GEN': 'Würzburg', 'BEZ': 'Kreisfreie Stadt'},
                    {'GEN': 'Waldeck-Frankenberg', 'BEZ': 'Landkreis'}]
    rest_api = 'https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=1%3D1&outFields=OBJECTID,GEN,BEZ,last_update,cases7_per_100k&outSR=4326&f=json'
    cu = COVIDUpdate(rest_api)
    result = cu.check(target_areas)
    print(result)
