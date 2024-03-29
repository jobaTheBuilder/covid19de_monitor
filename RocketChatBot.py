import os
from datetime import datetime
from threading import Timer
from COVIDUpdate import COVIDUpdate
from IntensivregisterUpdate import IntensivregisterUpdate
from ImpfungUpdate import ImpfungUpdate
import requests
import json

last_auto_update_result = None
last_auto_update_overall_result = None
last_auto_update_states = None
#from worldometer.com
#from worldometer.com
POPULATION_GERMANY = 84048123


with open('config/rocketchat.config.json') as config_file:
    config = json.load(config_file)

def next_update():
    now = datetime.now()
    seconds_today_until_now = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    seconds_until_timer = config['auto_update_hour'] * 60 * 60 + config['auto_update_minute'] * 60

    # Is the next trigger timestamp still today or tomorrow?
    if seconds_until_timer < seconds_today_until_now:
        return 86400 + seconds_until_timer - seconds_today_until_now
    else:
        return seconds_until_timer - seconds_today_until_now


def get_incidence_areas():
    global last_auto_update_result
    previous_result = last_auto_update_result
    result = ""

    try:
        resultCases = COVIDUpdate().check(config['auto_update_areas'])
        for area in sorted(resultCases.data):
            value = resultCases.data[area]

            extra_info = get_incidence_indicator(value)

            if previous_result:
                if area in previous_result.data:
                    previous_value = previous_result.data[area]
                    diff_pct = (value - previous_value) / previous_value

                    extra_info += f" (gestern: {previous_result.data[area]} "

                    extra_info += get_dif_indicator(diff_pct)

                    extra_info += ')'

            result += f">> {area}: *{value}* {extra_info}\n"

        result += '>> RKI ' + ', '.join(resultCases.dates)

        last_auto_update_result = resultCases

    except:
        result += "Inzidenzen für die Landkreise konnten nicht geladen werden"
    return result


def post_update():

    try:

        message = "**:mask: 7-Tage Inzidenzen**\n"
        message += get_overall_data() + "\n"
        message += get_incidence_areas()
        message += get_intensive_care()
        message += get_vac()
        message += get_hospitalization()

        requests.post(config['webhook_url'], {'text': message})

        Timer(next_update(), post_update, ()).start()
    except Exception as e:
        print(f"Error posting message: {e}")

def get_overall_data():
    global last_auto_update_overall_result

    try:
        data =  requests.get("https://api.corona-zahlen.org/germany").json()
        casesPerWeek = round(data["weekIncidence"],2)
        rValue = data["r"]["rValue7Days"]["value"]
        deltaCases = data["delta"]["cases"]
        result = f"> Deutschland: {casesPerWeek} {get_incidence_indicator(casesPerWeek)}"

        if last_auto_update_overall_result:
            old_cases = round(last_auto_update_overall_result["weekIncidence"],2)
            dif = (casesPerWeek - old_cases) / old_cases
            result += f" (gestern: {old_cases} {get_dif_indicator(dif)})"

        result += f"\n > r-Wert (7-Tage): {rValue}"

        if last_auto_update_overall_result:
            old_r_value = last_auto_update_overall_result["r"]["rValue7Days"]["value"]
            dif = rValue - old_r_value
            result += f" (gestern: {old_r_value} {get_dif_indicator(dif)})"

        result += f"\n > Tägliche Neuinfektionen: {deltaCases}"

        if last_auto_update_overall_result:
            oldDeltaCases = last_auto_update_overall_result["delta"]["cases"]
            dif = (deltaCases - oldDeltaCases) / oldDeltaCases
            result += f" (gestern: {oldDeltaCases} {get_dif_indicator(dif)})"

        last_auto_update_overall_result = data

        return result
    except:
        return "> Keine Daten für Deutschland verfügbar"


def get_vac():
    result = "\n\n <br> \n\n **:syringe: Impfungen**\n"
    try:
        iu = ImpfungUpdate()
        resultFirst = iu.get_vac_first('')
        resultSecond = iu.get_vac_second('')
        resultBooster = iu.get_vac_booster('')
        resultFirstQuote = round(resultFirst/POPULATION_GERMANY * 100,2)
        resultSecondQuote = round(resultSecond/POPULATION_GERMANY * 100,2)
        resultBoosterQuote = round(resultBooster/POPULATION_GERMANY * 100,2)
        resultDeliveredVaccines = iu.get_all_delivered_vaccnies()

        result += f"> Erstimpfung: {resultFirst:,}   ({resultFirstQuote}%)\n"
        result += f"> Zweitimpfung: {resultSecond:,}  ({resultSecondQuote}%)\n"
        result += f"> BoosterImpfung: {resultBooster:,}  ({resultBoosterQuote}%)\n"
        result += f"> Gelieferte Dosen: {resultDeliveredVaccines:,} (wöchentliche Aktualisierung)"

    except:
        result += "> Keine Impfdaten verfügbar. Vermutlich wurde die Exceltabelle vom RKI wieder geändert..."

    return result

def get_intensive_care():
    result = "\n\n <br> \n\n **:bed: Auslastung Intensivstationen**\n"
    try:
        resultBeds = IntensivregisterUpdate().get_overall_occupancy_in_percent()
        result += f"> {resultBeds}%"
    except:
        result += "Keine Daten verfügbar..."

    return result

def get_hospitalization():
    global last_auto_update_states

    result = "\n\n <br> \n\n **:hospital: 7-Tage-Inzidenz Hospitalisierungen**"
    states = config['auto_update_hospitalization']
    try:
        data =  requests.get("https://api.corona-zahlen.org/states").json()
        for state in states:
            if state in data["data"]:
                incidence = data["data"][state]["hospitalization"]["incidence7Days"]
                name = data["data"][state]["name"]
                indicator = get_hospitalization_indicator(incidence)
                result += f"\n > {name}: {incidence} {indicator} "

                if last_auto_update_states:
                    incidence_old = last_auto_update_states["data"][state]["hospitalization"]["incidence7Days"]
                    diff_pct = (incidence - incidence_old) / incidence_old
                    result += f" (gestern: {incidence_old} {get_dif_indicator(diff_pct)})"

    except:
        result += "\n Keine Hospitalisierungsraten verfügbar"

    return result

def get_dif_indicator(difference):
    indicator = ""
    if difference >= 0.1:
        indicator = ':arrow_double_up:'
    elif difference > 0.01:
        indicator = ':arrow_up_small:'
    elif difference < -0.1:
        indicator = ':arrow_double_down:'
    elif difference < -0.01:
        indicator = ':arrow_down_small:'
    else:
        indicator = ':left_right_arrow:'
    return indicator

def get_hospitalization_indicator(value):
    if value >= 9:
        return ":nine:"
    elif value >= 6:
        return ":six:"
    elif value >= 3:
        return ":three:"
    return ":zero:"

def get_incidence_indicator(value):
    indicator = ""
    if value >= 100:
        indicator = ':sos:'
    elif value >= 50:
        indicator = ':o2:'
    elif value >= 35:
        indicator = ':eight_pointed_black_star:'
    else:
        indicator += ':sparkle:'
    return indicator

if __name__ == "__main__":
    Timer(next_update(), post_update, ()).start()
