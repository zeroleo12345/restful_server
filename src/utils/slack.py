import requests
# 第三方库
from dynaconf import settings


class Slack(object):
    SLACK_WEB_HOOK = settings.get('SLACK_WEB_HOOK', default='')

    @classmethod
    def send_message(cls, text):
        assert cls.SLACK_WEB_HOOK
        #
        message = {
            'text': text
        }
        response = requests.post(cls.SLACK_WEB_HOOK, json=message)
        response.raise_for_status()
        return response
