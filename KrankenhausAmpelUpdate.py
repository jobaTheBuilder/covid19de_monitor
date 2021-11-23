#!/usr/bin/env python3
from bs4 import BeautifulSoup
import requests

LGL_WEBSITE = "https://www.lgl.bayern.de/gesundheit/infektionsschutz/infektionskrankheiten_a_z/coronavirus/karte_coronavirus/index.htm"
WEEKLY_CASES = "Hospitalisierte Fälle der letzten 7 Tage"
CURRENT_CASES = "Belegung der Intensivbetten durch bestätigte COVID-19-Fälle (DIVI)"
YELLOW_STATUS_BORDER_WEEKLY = 1200
YELLOW_STATUS_BORDER_CURRENTLY = 450
RED_STATUS_BORDER = 600

class Status:
    GREEN = 0
    YELLOW = 1
    RED = 2

class KrankenhausAmpelUpdate:

    def __init__(self):
        self.fetch_data()


    def fetch_data(self):
        r = requests.get(LGL_WEBSITE)
        soup = BeautifulSoup(r.text, "html.parser")
        self.weekly_cases = int(soup.find(lambda tag:tag.name=="td" and WEEKLY_CASES in tag.text).find_next_siblings("td")[0].text)
        self.current_cases = int(soup.find(lambda tag:tag.name=="td" and CURRENT_CASES in tag.text).find_next_siblings("td")[0].text)

    def get_yellow_weekly_percentage(self):
        return  round(self.weekly_cases/YELLOW_STATUS_BORDER_WEEKLY * 1000)/10

    def get_yellow_current_percentage(self):
        return round(self.current_cases/YELLOW_STATUS_BORDER_CURRENTLY * 1000)/10

    def get_red_status_percentage(self):
        return round(self.current_cases/RED_STATUS_BORDER * 1000)/10

    def get_yellow_status_weekly_formatted(self):
        return "{wp}% ({wc}/{wb})".format(wp = self.get_yellow_weekly_percentage(), wc=self.weekly_cases, wb=YELLOW_STATUS_BORDER_WEEKLY)

    def get_yellow_status_currently_formatted(self):
        return "{cp}% ({cc}/{cb})".format(cp = self.get_yellow_current_percentage(), cc=self.current_cases, cb=YELLOW_STATUS_BORDER_CURRENTLY)

    def get_red_status_formatted(self):
        return "{cp}% ({cc}/{cb})".format(cp=self.get_red_status_percentage(), cc=self.current_cases, cb=RED_STATUS_BORDER)

    def get_status(self):
        if self.get_red_status_percentage() > 100:
            return Status().RED
        elif self.get_yellow_current_percentage() > 100 or self.get_yellow_weekly_percentage() > 100:
            return Status().YELLOW
        return Status().GREEN

