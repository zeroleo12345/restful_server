# -*- coding: utf-8 -*-
import os
from decouple import config
from qiniu import Auth, put_file, etag

# 需要填写你的 Access Key 和 Secret Key
QN_ACCESS_KEY = config('QN_ACCESS_KEY')
QN_SECRET_KEY = config('QN_SECRET_KEY')

# 构建鉴权对象
q = Auth(QN_ACCESS_KEY, QN_SECRET_KEY)

# 要上传的空间
bucket = 'pppoe'

# 上传到七牛后保存的文件名
filename = 'test.jpg'
key = filename

# 生成上传 Token，可以指定过期时间等
token = q.upload_token(bucket, key=key, expires=3600)

# 要上传文件的本地路径
file_path = os.path.join('./media', filename)
if not os.path.exists(file_path):
    raise Exception(f'file {file_path} not exist')

ret, info = put_file(token, key=key, file_path=file_path)
print(info)
assert ret['key'] == key
assert ret['hash'] == etag(file_path)
