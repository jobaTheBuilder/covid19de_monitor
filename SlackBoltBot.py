import os
from datetime import datetime
from slack_bolt import App
from threading import Timer
from COVIDUpdate import COVIDUpdate
import json

last_auto_update_result = None

with open('config/slack.config.json') as config_file:
    config = json.load(config_file)

app = App(
    token=config['slack_token'],
    signing_secret=config['slack_signing_secret']
)


def next_update():
    now = datetime.now()
    seconds_today_until_now = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    seconds_until_timer = config['auto_update_hour'] * 60 * 60 + config['auto_update_minute'] * 60

    # Is the next trigger timestamp still today or tomorrow?
    if seconds_until_timer < seconds_today_until_now:
        return 86400 + seconds_until_timer - seconds_today_until_now
    else:
        return seconds_until_timer - seconds_today_until_now


def build_message(result, previous_result=None):
    blocks = []

    for area in sorted(result.data):
        value = result.data[area]

        extra_info = ''
        if value >= 100:
            extra_info += ':sos:'
        elif value >= 50:
            extra_info += ':o2:'
        elif value >= 35:
            extra_info += ':eight_pointed_black_star:'
        else:
            extra_info += ':sparkle:'

        if previous_result:
            if area in previous_result.data:
                previous_value = previous_result.data[area]
                diff_pct = (value - previous_value) / previous_value

                extra_info += f"  (gestern: {previous_result.data[area]}"

                if diff_pct >= 0.1:
                    extra_info += ' :arrow_double_up:'
                elif diff_pct > 0.01:
                    extra_info += ' :arrow_up_small:'
                elif diff_pct < -0.01:
                    extra_info += ' :arrow_down_small:'
                elif diff_pct < -0.1:
                    extra_info += ' :arrow_double_down:'
                else:
                    extra_info += ' :left_right_arrow:'

                extra_info += ')'

        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f"{area}: *{value}* {extra_info}"
            }
        })

    blocks.append({
        'type': 'context',
        'elements': [
            {
                'type': 'mrkdwn',
                'text': '*RKI* ' + ', '.join(result.dates)
            }
        ]
    })

    return blocks


def post_update():
    global last_auto_update_result

    try:
        result = COVIDUpdate().check(config['auto_update_areas'])
        app.client.chat_postMessage(
            channel=config['auto_update_channel'],
            blocks=build_message(result, previous_result=last_auto_update_result)
        )
        last_auto_update_result = result

        Timer(next_update(), post_update, ()).start()
    except Exception as e:
        print(f"Error posting message: {e}")


if __name__ == "__main__":
    Timer(next_update(), post_update, ()).start()
    app.start(3000)
