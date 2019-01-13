#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
from decouple import config
from qiniu import Auth, put_file, etag

# 回调域名地址
API_SERVER_URL = config('API_SERVER_URL')
# 需要填写你的 Access Key 和 Secret Key
QN_ACCESS_KEY = config('QN_ACCESS_KEY')
QN_SECRET_KEY = config('QN_SECRET_KEY')

# 构建鉴权对象
q = Auth(QN_ACCESS_KEY, QN_SECRET_KEY)

# 要上传的空间
bucket = 'pppoe'

# 上传到七牛后保存的文件名
directory, filename = 'test', 'test.jpg'
key = f'{directory}/{filename}'

# 生成上传 Token，可以指定过期时间等
policy = {
    'endUser': '1',

    # 七牛回调服务端, 方式1
    # 'callbackUrl': f'{API_SERVER_URL}/debug',    # 上传成功后，七牛云向业务服务器发送 POST 请求的 URL
    # 'callbackBodyType': 'application/x-www-form-urlencoded',
    # 'callbackBody': 'bucket=${bucket}&key=$(key)&etag=$(etag)&fname=${fname}&fsize=${fsize}&mimeType=${mimeType}&endUser=${endUser}',

    # 七牛回调服务端, 方式2
    'callbackUrl': f'{API_SERVER_URL}/debug',    # 上传成功后，七牛云向业务服务器发送 POST 请求的 URL
    'callbackBodyType': 'application/json',
    'callbackBody': '''{"bucket": "${bucket}", "key": "$(key)", "hash": "$(etag)", "fname": "$(fname)", "fsize": "$(fsize)", "endUser": "$(endUser)"}''',

    # 返回给客户端的内容格式
    # 'returnBody': '''{"bucket": "${bucket}", "key": "$(key)", "hash": "$(etag)", "fname": "$(fname)", "fsize": "$(fsize)", "endUser": "$(endUser)"}''',
}
token = q.upload_token(bucket, key=key, expires=3600, policy=policy)
print('token: ', token)

# 要上传文件的本地路径
file_path = os.path.join('./media', filename)
if not os.path.exists(file_path):
    raise Exception(f'file {file_path} not exist')

ret, info = put_file(token, key=key, file_path=file_path)
print('ret:', ret)
print('info:', info)
if info.ok():
    assert ret['key'] == key
    assert ret['hash'] == etag(file_path)
