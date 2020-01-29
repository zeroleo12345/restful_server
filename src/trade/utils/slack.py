import requests
# 第三方库
from dynaconf import settings

SLACK_WEB_HOOK = settings.get('SLACK_WEB_HOOK')


def send_slack_message(text):
    message = {
        'text': text
    }
    response = requests.post(SLACK_WEB_HOOK, json=message)
    response.raise_for_status()
    return response
