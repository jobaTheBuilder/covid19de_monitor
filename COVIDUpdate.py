import requests
import json
import argparse


class COVIDResultData:
    def __init__(self, data, dates):
        self.data = data
        self.dates = dates
        self.str = None

    def __str__(self):
        if not self.str:
            self.str = 'RKI ' + ', '.join(self.dates) + ': ' + ', '.join(key + ': ' + str(self.data[key]) for key in sorted(self.data))

        return self.str


class COVIDUpdate:
    DEFAULT_REST_URI = 'https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=1%3D1&outFields=OBJECTID,GEN,BEZ,last_update,cases7_per_100k&outSR=4326&f=json'

    def __init__(self, rest_url=DEFAULT_REST_URI):
        self.rest_url = rest_url

    def check(self, area_list):
        data = {}
        dates = set()
        response = requests.get(self.rest_url, verify=True)
        if response.ok:
            response_data = json.loads(response.content)
            features = response_data['features']
            for feature in features:
                if self.in_area(feature, area_list):
                    dates.add(self.get(feature, 'last_update'))
                    gf = str(self.get(feature, 'GEN'))
                    bf = str(self.get(feature, 'BEZ'))
                    c7p100 = round(self.get(feature, 'cases7_per_100k'), 1)
                    data['{0} ({1})'.format(gf, bf)] = c7p100
        return COVIDResultData(data, dates)

    def find_areas(self, filter_string=None):
        area_list = []
        response = requests.get(self.rest_url, verify=True)
        if response.ok:
            response_data = json.loads(response.content)
            features = response_data['features']
            for feature in features:
                gf = self.get(feature, 'GEN')
                bf = self.get(feature, 'BEZ')
                if not filter_string:
                    area_list.append({'GEN': gf, 'BEZ': bf})
                elif filter_string in gf or filter_string in bf:
                    area_list.append({'GEN': gf, 'BEZ': bf})
        return area_list

    def list_areas(self):
        return self.find_areas()

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

    def print_me(self, json_strct):
        if json_strct:
            print(json.dumps(json_strct, indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list", help="Lists the available areas of interest as config JSON.", action="store_true")
    parser.add_argument("-f", "--find", help="Find & filters the available areas of interest according to the given string (case sensitive!).")
    parser.add_argument("-a", "--areas", help="Receives JSON file with defined areas of interest.")
    parser.add_argument("-i", "--incidence", help="Find all areas with names including the given string and return the 100k-7 incidence.")
    args = parser.parse_args()
    cu = COVIDUpdate()
    if args.list:
        cu.print_me(cu.list_areas())
    elif args.find:
        cu.print_me(cu.find_areas(args.find))
    elif args.areas:
        with open(args.areas) as json_file:
            example_area = json.load(json_file)
        result = cu.check(example_area)
        print(result)
    elif args.incidence:
        areas = cu.find_areas(args.incidence)
        result = cu.check(areas)
        print(result)
    else:
        print("Please use help to see your options (--help).\nHere is an example...")
        example_area = [{'GEN': 'Würzburg', 'BEZ': 'Kreisfreie Stadt'}]
        result = cu.check(example_area)
        print(str(result))
