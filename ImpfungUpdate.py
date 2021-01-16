#!/usr/bin/env python3

import pandas
import requests
import argparse

API = 'https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Daten/Impfquotenmonitoring.xlsx?__blob=publicationFile'

class ImpfungUpdate:

    def __init__(self):
        self.prefix = ''
        self.area = 'Gesamt'
        result = requests.get(API)
        self.df = pandas.read_excel(result.content,sheet_name=1)


    def get_area_data_where(self,where):
        bl = self.df.loc[self.df['Bundesland'] == self.area]
        return bl[where].iloc[0]

    def get_vac_kum(self):
        return int(self.get_area_data_where('Impfungen kumulativ'))

    def get_dif_day_before(self):
        return int(self.get_area_data_where('Differenz zum Vortag'))

    def get_vac_per_1000(self):
        return int(self.get_area_data_where('Impfungen pro 1.000 Einwohner'))

    def all_areas(self):
        return self.df['Bundesland']


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-bl", "--bundesland", help="Information about a Bundesland in germany")
    parser.add_argument("-a","--all",help="All accinaations in a specific area", action="store_true")
    parser.add_argument("-la","--listareas", help="Lists all available areas", action="store_true")
    parser.add_argument("-p", "--prefix", help="Print given prefix as String before the actual number. Example: -p 'Bayern Vaccinations' -bl Bayern -a")
    parser.add_argument("-d", "--difference", help="Difference in Vaccinations to the day before", action="store_true")
    parser.add_argument("-t", "--thousand", help="Vaccinations per 1k citizens", action="store_true")
    args = parser.parse_args()
    iu = ImpfungUpdate()
    if args.prefix:
        iu.prefix = args.prefix
    if args.bundesland:
        iu.area = args.bundesland
    if args.all:
        print(iu.prefix + f"{iu.get_vac_kum():,}")
    elif args.listareas:
        areas = iu.all_areas()
        for i in range(17):
            print(areas[i])
    elif args.difference:
        print(iu.prefix + f"{iu.get_dif_day_before():,}")
    elif args.thousand:
        print(iu.prefix + str(iu.get_vac_per_1000()))
    else:
        print("Please use help to see your options (--help)")
