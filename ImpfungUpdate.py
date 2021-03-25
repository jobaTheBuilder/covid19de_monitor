#!/usr/bin/env python3

import argparse
import requests
import json
import csv

API = 'https://api.corona-zahlen.org/vaccinations'
DELIVERY_API= 'https://impfdashboard.de/static/data/germany_deliveries_timeseries_v2.tsv'
DELIVERED_VAC_DICT = {"comirnaty": "biontech","moderna": "moderna","astra": "astraZeneca"}

class ImpfungUpdate:

    def __init__(self):
        self.prefix = ''
        result = requests.get(API)
        self.data = result.json()["data"]
        self.delivery_data = self.get_delivery_data()

    def get_delivery_data(self):
        tsv_f = requests.get(DELIVERY_API).content.decode('utf-8')
        data = csv.DictReader(tsv_f.splitlines(),delimiter="\t")
        result_data = {}
        for entry in data:
            vaccine = entry['impfstoff']
            if vaccine not in result_data.keys():
                result_data[vaccine] = int(entry['dosen'])
            else:
                result_data[vaccine] += int(entry['dosen'])
        return result_data


    def get_vac_data(self,area, key, isSecond=False):
        area_data = []
        if area == '':
            area_data = self.data
        else:
            area_data = self.data["states"][area]
        if isSecond:
            return area_data["secondVaccination"][key]
        else:
            return area_data[key]

    def get_vac_all(self, area):
        return self.get_vac_data(area,"administeredVaccinations")

    def get_vac_all_delta(self, area):
        return int(self.get_vac_first_delta(area)) + int(self.get_vac_second_delta(area))

    def get_vac_first(self, area):
        return self.get_vac_data(area,"vaccinated")

    def get_vac_second(self,area):
        return self.get_vac_data(area,"vaccinated",True)

    def get_vac_first_delta(self, area):
        return self.get_vac_data(area,"delta")

    def get_vac_second_delta(self,area):
        return self.get_vac_data(area,"delta",True)

    def get_vac_quote(self, area):
        return self.get_vac_data(area,"quote")

    def get_vac_by_brand(self,area,brand):
        if brand not in DELIVERED_VAC_DICT.values():
            if brand in DELIVERED_VAC_DICT.keys():
                brand = DELIVERED_VAC_DICT[brand]
        return self.get_vac_data(area,"vaccination")[brand] + self.get_vac_data(area,"vaccination",True)[brand]

    def get_all_vac_brands(self,area):
        return self.get_vac_data(area,"vaccination")

    def all_areas(self):
        abb = self.data["states"].keys()
        for key in abb:
            print("{key} for {name}".format(key=key,name=self.data["states"][key]["name"]))

    def get_all_delivered_vaccnies(self):
        return sum(self.delivery_data.values())

    def get_all_delivered_vaccines_quote(self):
        return round(self.get_vac_all("")/self.get_all_delivered_vaccnies()*10000) / 100

    def get_delivered_vaccines_by_brand(self,brand):
        if brand not in self.delivery_data.keys():
            for key, value in DELIVERED_VAC_DICT.items():
                if brand == value:
                    brand = key
        return self.delivery_data[brand]

    def get_delivered_vaccines_by_brand_quote(self,brand):
        return round(self.get_vac_by_brand("",brand)/self.get_delivered_vaccines_by_brand(brand) * 10000) / 100

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-bl", "--bundesland", help="Information about a Bundesland in germany")
    parser.add_argument("-a","--all",help="All accinaations in a specific area", action="store_true")
    parser.add_argument("-la","--listareas", help="Lists all available areas", action="store_true")
    parser.add_argument("-p", "--prefix", help="Print given prefix as string before the actual number. Example: -p 'Bayern Vaccinations' -bl Bayern -a")
    parser.add_argument("-d", "--difference", help="Difference in vaccinations to the day before for all vaccination", action="store_true")
    parser.add_argument("-df", "--differencefirst", help="Difference in vaccinations to the day before for the first vaccination", action="store_true")
    parser.add_argument("-ds", "--differencesecond", help="Difference in vaccinations to the day before for the second vaccination", action="store_true")
    parser.add_argument("-q", "--quote", help="Vaccinations quote", action="store_true")
    parser.add_argument("-vf", "--vaccinationfirst", help="Number of people who recived their first vaccination", action="store_true")
    parser.add_argument("-vs", "--vaccinationsecond", help="Number of people who recived their second vaccination", action="store_true")
    parser.add_argument("-vb","--vaccinebrand",help="Number of vaccinations for a specified vaccine")
    parser.add_argument("-lvb","--listvaccinebrand",help="Lists all available vaccine brands and the amount of times they were being used", action="store_true")
    parser.add_argument("-sv","--shippedvaccines",help="All shipped vaccines", action="store_true")
    parser.add_argument("-sq","--shippedvaccinatedquote",help="Quote of administered vaccinations / delivered vaccines in percent",action="store_true")
    parser.add_argument("-ls","--listshippedvaccines",help="Lists all shipped vaccines",action="store_true")
    parser.add_argument("-sb","--shippedvaccinebrand",help="Get all shipped vaccines by brand")
    parser.add_argument("-sbq","--shippedvaccinebrandquote",help="Get shipped vaccines vaccination quote by brand")
    args = parser.parse_args()

    iu = ImpfungUpdate()
    area = ''
    if args.prefix:
        iu.prefix = args.prefix
    if args.bundesland:
        area = args.bundesland.upper()
    if args.all:
        print(iu.prefix + f"{iu.get_vac_all(area):,}")
    elif args.listareas:
        iu.all_areas()
    elif args.difference:
        print(iu.prefix + f"{iu.get_vac_all_delta(area):,}")
    elif args.differencefirst:
        print(iu.prefix + f"{iu.get_vac_first_delta(area):,}")
    elif args.differencesecond:
        print(iu.prefix + f"{iu.get_vac_second_delta(area):,}")
    elif args.quote:
        print(iu.prefix + str(iu.get_vac_quote(area)))
    elif args.vaccinationfirst:
        print(iu.prefix + f"{iu.get_vac_first(area):,}")
    elif args.vaccinationsecond:
        print(iu.prefix + f"{iu.get_vac_second(area):,}")
    elif args.vaccinebrand:
        print(iu.prefix + f"{iu.get_vac_by_brand(area,args.vaccinebrand):,}")
    elif args.listvaccinebrand:
        print(iu.prefix + json.dumps(iu.get_all_vac_brands(area),indent=4))
    elif args.shippedvaccines:
        print(iu.prefix + f"{iu.get_all_delivered_vaccnies():,}")
    elif args.shippedvaccinatedquote:
        print(iu.prefix + str(iu.get_all_delivered_vaccines_quote()) + "%")
    elif args.listshippedvaccines:
        print(iu.prefix + json.dumps(iu.delivery_data,indent=4))
    elif args.shippedvaccinebrand:
        print(iu.prefix + f"{iu.get_delivered_vaccines_by_brand(args.shippedvaccinebrand):,}")
    elif args.shippedvaccinebrandquote:
        print(iu.prefix + str(iu.get_delivered_vaccines_by_brand_quote(args.shippedvaccinebrandquote)))
    else:
        print("Please use help to see your options (--help)")
