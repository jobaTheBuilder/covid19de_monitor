#!/usr/bin/env python3

import requests
import json
import argparse
import datetime
import io
import threading

BL_API = 'https://www.intensivregister.de/api/public/reporting/laendertabelle'
LK_API = 'https://diviexchange.blob.core.windows.net/%24web/DIVI_Intensivregister_Auszug_pro_Landkreis.csv'
BL_DICT = {'BW': 'BADEN_WUERTTEMBERG','BY' : 'BAYERN','BE': 'BERLIN','BB': 'BRANDENBURG','HB': 'BREMEN','HH': 'HAMBURG','HE': 'HESSEN','MV': 'MECKLENBURG_VORPOMMERN','NI': 'NIEDERSACHSEN','NW': 'NORDRHEIN_WESTFALEN','RP': 'RHEINLAND_PFALZ','SL': 'SAARLAND','SN': 'SACHSEN','ST': 'SACHSEN_ANHALT','SH': 'SCHLESWIG_HOLSTEIN','TH': 'THUERINGEN'}
GS_DICT = {}
with open('ags-dict.json', encoding='utf-8') as json_file:
    GS_DICT = json.load(json_file,)

class IntensivregisterUpdate:


    def __init__(self):
        self.prefix = ''
        th_bl = threading.Thread(self.update_bl_data())
        th_lk = threading.Thread(self.update_lk_data())
        th_bl.start()
        th_lk.start()
        th_bl.join()
        th_lk.join()

        
    def update_lk_data(self):
        result = requests.get(LK_API)
        self.lk_data = self.parse_csv_to_json(result.text)["data"]

    def update_bl_data(self):
        self.bl_data = self.get_data_as_json()

    def get_data_as_json(self):
        response = requests.get(BL_API)
        return response.json()["data"]


    def get_occupancy_by_bl_in_percent(self,bl):
        bl_full = BL_DICT[bl]
        for item in self.bl_data:
            if item['bundesland'] == bl_full:
                return item['bettenBelegtToBettenGesamtPercent']

    def get_occupancy_by_bl_in_percent_with_7d_emgergancy_beds_in_percent(self,bl):
        return self.get_all_occupied_beds_by_bl(bl)/(self.get_all_beds_by_bl(bl)+self.get_all_emergency_beds_7d_by_bl(bl)) * 100

    def get_all_beds_by_bl(self,bl):
        bl_full = BL_DICT[bl]
        for item in self.bl_data:
            if item['bundesland'] == bl_full:
                return item['intensivBettenGesamt']

    def get_all_occupied_beds_by_bl(self,bl):
        bl_full = BL_DICT[bl]
        for item in self.bl_data:
            if item['bundesland'] == bl_full:
                return item['intensivBettenBelegt']

    def get_all_emergency_beds_7d_by_bl(self,bl):
        bl_full = BL_DICT[bl]
        for item in self.bl_data:
            if item['bundesland'] == bl_full:
                return item['intensivBettenNotfall7d']


    def get_all_beds(self):
        b_sum = 0
        for item in self.bl_data:
            b_sum += item['intensivBettenGesamt']
        return b_sum

    def get_all_occupied_beds(self):
        bo_sum = 0
        for item in self.bl_data:
            bo_sum += item['intensivBettenBelegt']
        return bo_sum

    def get_all_emergency_beds_7d(self):
        be_sum = 0
        for item in self.bl_data:
            be_sum += item['intensivBettenNotfall7d']
        return be_sum


    def get_overall_occupancy_in_percent(self):
        return self.get_all_occupied_beds()/self.get_all_beds() * 100

    def get_overall_occupancy_in_percent_with_emergency_beds(self):
        return self.get_all_occupied_beds()/(self.get_all_beds() + self.get_all_emergency_beds_7d())* 100

    def get_date(self):
        for item in self.bl_data:
            t = item['creationTimestamp']
            return datetime.datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ')

    def parse_csv_to_json(self,csv_as_string):
        csvfile = io.StringIO(csv_as_string)

        arr=[]
        headers = []

        # Read in the headers/first row
        for header in csvfile.readline().split(','):
            headers.append(header)

        # Extract the information into the "xx" : "yy" format.
        for line in csvfile.readlines():
            lineStr = '\n'
            for i,item in enumerate(line.split(',')):
                lineStr+='"'+headers[i].replace('\r\n','') +'" : "' + item.replace('\r\n','') + '",\n'
            arr.append(lineStr)

        csvfile.close()

        #convert the array into a JSON string:
        jsn = '{ "data":['
        jsnEnd = ']}'
        for i in range(len(arr)-1):
            if i == len(arr)-2:
                jsn+="{"+str(arr[i])[:-2]+"}"
            else:
                jsn+="{"+str(arr[i])[:-2]+"},"
        jsn+=jsnEnd

        return json.loads(jsn)

    def get_lk_data(self,lk_name):
        gs = ""
        try:
            gs = GS_DICT[lk_name]
        except:
            return None
        for entry in self.lk_data:
            if int(entry["gemeindeschluessel"]) == gs:
                return entry


    def lk_data_formatted(self,lk_data):
        if (lk_data == None):
            return "Your Landkreis or Stadt isn't in the list. See -la to list all Landkreise and Städte."
        fb = int(lk_data["betten_frei"])
        ob = int(lk_data["betten_belegt"])
        ab = fb + ob
        rate = round(ob/ab*100,2)
        return ("Occupancy Rate: {percent}% ({ob}/{ab})").format(percent=rate, ob=ob ,ab=ab)

    def lk_data_for_areas(self,areas):
        result = ""
        for area in areas:
            BEZ = area["BEZ"]
            GEN = area["GEN"]
            if BEZ != "Landkreis":
                BEZ = "Stadt"
            result += "{gen} {bez}: {rate}\n".format(gen=GEN,bez=BEZ,rate=self.lk_data_formatted(self.get_lk_data(GEN + " " + BEZ)))
        return result[:-2]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-lb", "--listbundeslander", help="Lists all available states and their abbreviations", action="store_true")
    parser.add_argument("-lk", "--landkreis", help="Print Landkreis occupancy rate", type=str)
    parser.add_argument("-s", "--stadt", help="Print Stadt occupancy rate", type=str)
    parser.add_argument("-b", "--bundesland", help="Show the percentage of occupied beds in a specific state. Example: -b BY")
    parser.add_argument("-d", "--deutschland", help="Show the Percentage of all occupied beds in Germany",action="store_true")
    parser.add_argument("-dn", "--deutschlandwithemergency", help="Show the Percentage of all occupied beds in Germany including the 7 day emergency beds",action="store_true")
    parser.add_argument("-bn", "--bundeslandwithemergency", help="Show the percentage of occupied beds in a specific state including the 7 day emergency beds. Example: -bn BY")
    parser.add_argument("-p", "--prefix", help="Print given prefix as String before the actual number. Example: -p 'BY beds' -bn BY")
    parser.add_argument("-la","--listareas", help="Prints all names of the Landreise and Städte",action="store_true")
    parser.add_argument("-a","--areas", help="Receives JSON file with defined areas of interest.")
    args = parser.parse_args()
    iu = IntensivregisterUpdate()
    if args.prefix:
        iu.prefix = args.prefix
        args = parser.parse_args()
    if args.listbundeslander:
        print(json.dumps(BL_DICT,indent=4))
    elif args.bundesland:
        print(iu.prefix + str(iu.get_occupancy_by_bl_in_percent(args.bundesland)))
    elif args.deutschland:
        print(iu.prefix + str(iu.get_overall_occupancy_in_percent()))
    elif args.deutschlandwithemergency:
        print(iu.prefix + str(iu.get_overall_occupancy_in_percent_with_emergency_beds()))
    elif args.bundeslandwithemergency:
        print(iu.prefix + str(iu.get_occupancy_by_bl_in_percent_with_7d_emgergancy_beds_in_percent(args.bundeslandwithemergency)))
    elif args.landkreis:
        result = iu.lk_data_formatted(iu.get_lk_data(args.landkreis + " Landkreis"))
        if result != None:
            print(iu.prefix + str(result))
    elif args.stadt:
        result = iu.lk_data_formatted(iu.get_lk_data(args.stadt + " Stadt"))
        if result != None:
            print(iu.prefix + str(result))
    elif args.areas:
        with open(args.areas) as json_file:
            example_area = json.load(json_file)
        result = iu.lk_data_for_areas(example_area)
        print(iu.prefix + str(result))
    elif args.listareas:
        l = list(GS_DICT.keys())
        l.sort()
        for e in l:
            print(e)
    else:
        print("Please use help to see your options (--help)")
