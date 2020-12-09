import requests
import json
import argparse
import datetime

API = 'https://www.intensivregister.de/api/public/reporting/laendertabelle'
BL_DICT = {'BW': 'BADEN_WUERTTEMBERG','BY' : 'BAYERN','BE': 'BERLIN','BB': 'BRANDENBURG','HB': 'BREMEN','HH': 'HAMBURG','HE': 'HESSEN','MV': 'MECKLENBURG_VORPOMMERN','NI': 'NIEDERSACHSEN','NW': 'NORDRHEIN_WESTFALEN','RP': 'RHEINLAND_PFALZ','SL': 'SAARLAND','SN': 'SACHSEN','ST': 'SACHSEN_ANHALT','SH': 'SCHLESWIG_HOLSTEIN','TH': 'THUERINGEN'}

class IntensivregisterUpdate:


    def __init__(self):
        self.data = self.get_data_as_json()

    def get_data_as_json(self):
        response = requests.get(API)
        return response.json()["data"]


    def get_occupancy_by_bl_in_percent(self,bl):
        bl_full = BL_DICT[bl]
        for item in self.data:
            if item['bundesland'] == bl_full:
                return item['bettenBelegtToBettenGesamtPercent']

    def get_occupancy_by_bl_in_percent_with_7d_emgergancy_beds_in_percent(self,bl):
        return self.get_all_occupied_beds_by_bl(bl)/(self.get_all_beds_by_bl(bl)+self.get_all_emergency_beds_7d_by_bl(bl)) * 100

    def get_all_beds_by_bl(self,bl):
        bl_full = BL_DICT[bl]
        for item in self.data:
            if item['bundesland'] == bl_full:
                return item['intensivBettenGesamt']

    def get_all_occupied_beds_by_bl(self,bl):
        bl_full = BL_DICT[bl]
        for item in self.data:
            if item['bundesland'] == bl_full:
                return item['intensivBettenBelegt']

    def get_all_emergency_beds_7d_by_bl(self,bl):
        bl_full = BL_DICT[bl]
        for item in self.data:
            if item['bundesland'] == bl_full:
                return item['intensivBettenNotfall7d']


    def get_all_beds(self):
        b_sum = 0
        for item in self.data:
            b_sum += item['intensivBettenGesamt']
        return b_sum

    def get_all_occupied_beds(self):
        bo_sum = 0
        for item in self.data:
            bo_sum += item['intensivBettenBelegt']
        return bo_sum

    def get_all_emergency_beds_7d(self):
        be_sum = 0
        for item in self.data:
            be_sum += item['intensivBettenNotfall7d']
        return be_sum


    def get_overall_occupancy_in_percent(self):
        return self.get_all_occupied_beds()/self.get_all_beds() * 100

    def get_overall_occupancy_in_percent_with_emergency_beds(self):
        return self.get_all_occupied_beds()/(self.get_all_beds() + self.get_all_emergency_beds_7d())* 100

    def get_date(self):
        for item in self.data:
            t = item['creationTimestamp']
            return datetime.datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list", help="Lists all available states and their abbreviations", action="store_true")
    parser.add_argument("-b", "--bundesland", help="Show the percentage of occupied beds in a specific state. Example: -b BY")
    parser.add_argument("-a", "--all", help="Show the Percentage of all occupied beds in Germany",action="store_true")
    parser.add_argument("-an", "--allwithemergency", help="Show the Percentage of all occupied beds in Germany including the 7 day emergency beds",action="store_true")
    parser.add_argument("-bn", "--bundeslandwithemergency", help="Show the percentage of occupied beds in a specific state including the 7 day emergency beds. Example: -bn BY")
    args = parser.parse_args()
    iu = IntensivregisterUpdate()
    if args.list:
        print(json.dumps(BL_DICT,indent=4))
    elif args.bundesland:
        print(iu.get_occupancy_by_bl_in_percent(args.bundesland))
    elif args.all:
        print(iu.get_overall_occupancy_in_percent())
    elif args.allwithemergency:
        print(iu.get_overall_occupancy_in_percent_with_emergency_beds())
    elif args.bundeslandwithemergency:
        print(iu.get_occupancy_by_bl_in_percent_with_7d_emgergancy_beds_in_percent(args.bundeslandwithemergency))
    else:
        print("Please use help to see your options (--help)")
