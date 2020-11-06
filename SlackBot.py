import logging
logging.basicConfig(level=logging.DEBUG)

from COVIDUpdate import COVIDUpdate

from slack import WebClient
from slack.errors import SlackApiError

client = WebClient(token="<BOT-TOKEN>")


target_areas = [{'GEN': 'Würzburg', 'BEZ': 'Kreisfreie Stadt'},
                {'GEN': 'Waldeck-Frankenberg', 'BEZ': 'Landkreis'}]
cu = COVIDUpdate()
result = cu.check(target_areas)

try:
  response = client.chat_postMessage(
    channel="<PREFFERED-CHANNEL>",
    text=str(result)
  )
except SlackApiError as e:
  # You will get a SlackApiError if "ok" is False
  assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
