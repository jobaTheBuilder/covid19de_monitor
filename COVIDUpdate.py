import requests
import json
import sys


class COVIDUpdate:
    DEFAULT_REST_URI = 'https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=1%3D1&outFields=OBJECTID,GEN,BEZ,last_update,cases7_per_100k&outSR=4326&f=json'

    def __init__(self, rest_url=DEFAULT_REST_URI):
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
                    dates.add(self.get(feature, 'last_update'))
                    gf = self.get(feature, 'GEN')
                    bf = self.get(feature, 'BEZ')
                    c7p100 = round(self.get(feature, 'cases7_per_100k'), 1)
                    data.append(str(gf) + ' (' + str(bf) + '): ' + str(c7p100))
        data.sort()
        return 'RKI ' + ', '.join(dates) + ': ' + ', '.join(data)

    def in_area(self, feature, areas):
        f_gen = self.get(feature, 'GEN')
        f_bez = self.get(feature, 'BEZ')
        for area in areas:
            gen = area['GEN']
            bez = area['BEZ']
            if gen == f_gen and bez == f_bez:
                return area
        return None

    def get(self, feature, attribute_name):
        return feature['attributes'][attribute_name]


if __name__ == "__main__":
    # a default city, just in case that no city definition can be found in the command line.
    # specify the city definition as json
    areas = [{'GEN': 'Würzburg', 'BEZ': 'Kreisfreie Stadt'}]
    if sys.argv[1:] and sys.argv[1:][0]:
        with open(sys.argv[1:][0]) as json_file:
            areas = json.load(json_file)
    cu = COVIDUpdate()
    result = cu.check(areas)
    print(result)



