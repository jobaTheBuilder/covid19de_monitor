import logging
logging.basicConfig(level=logging.DEBUG)

from COVIDUpdate import COVIDUpdate

import os
from slack import WebClient
from slack.errors import SlackApiError

client = WebClient(token="<BOT-TOKEN>")


target_areas = [{'GEN': 'Würzburg', 'BEZ': 'Kreisfreie Stadt'},
                    {'GEN': 'Waldeck-Frankenberg', 'BEZ': 'Landkreis'}]
rest_api = 'https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=1%3D1&outFields=OBJECTID,GEN,BEZ,last_update,cases7_per_100k&outSR=4326&f=json'
rest_api = 'https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=1%3D1&outFields=OBJECTID,GEN,BEZ,last_update,cases7_per_100k&outSR=4326&f=json'
cu = COVIDUpdate(rest_api)
result = cu.check(target_areas)

try:
  response = client.chat_postMessage(
    channel="<PREFFERED-CHANNEL>",
    text=result,

  )
except SlackApiError as e:
  # You will get a SlackApiError if "ok" is False
  assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
