# coding:utf-8
# 开发文档地址:    https://api.slack.com/incoming-webhooks

from decouple import config
import requests

SLACK_WEB_HOOK = config('SLACK_WEB_HOOK')

message = {
    # 'channel': '#alert',      # 实际不能改变channel
    'text': f'Slack Hello World!'
}

response = requests.post(SLACK_WEB_HOOK, json=message)
print(response.text)
response.raise_for_status()

