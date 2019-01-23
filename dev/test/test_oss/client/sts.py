#!/usr/bin/env python3
import json
import os
# 第三方库
from aliyunsdkcore import client
from aliyunsdksts.request.v20150401 import AssumeRoleRequest
import oss2

# 以下代码展示了STS的用法，包括角色扮演获取临时用户的密钥、使用临时用户的密钥访问OSS。

# STS入门教程请参看  https://yq.aliyun.com/articles/57895
# STS的官方文档请参看  https://help.aliyun.com/document_detail/28627.html

# 首先初始化AccessKeyId、AccessKeySecret、Endpoint等信息。
# 通过环境变量获取，或者把诸如“<你的AccessKeyId>”替换成真实的AccessKeyId等。
# 注意：AccessKeyId、AccessKeySecret为子用户的密钥。
# RoleArn可以在控制台的“访问控制  > 角色管理  > 管理  > 基本信息  > Arn”上查看。
#
# 以杭州区域为例，Endpoint可以是：
#   http://oss-cn-hangzhou.aliyuncs.com
#   https://oss-cn-hangzhou.aliyuncs.com
# 分别以HTTP、HTTPS协议访问。
"""
:param OSS_ACCESS_KEY: 子用户的 access key id
:param OSS_ACCESS_KEY_SECRET: 子用户的 access key secret
:param OSS_ARN: STS角色的Arn
"""
OSS_ACCESS_KEY = os.getenv('OSS_ACCESS_KEY')
OSS_ACCESS_KEY_SECRET = os.getenv('OSS_ACCESS_KEY_SECRET')
OSS_BUCKET_NAME = os.getenv('OSS_BUCKET_NAME')
OSS_REGION = os.getenv('OSS_REGION', 'cn-hongkong')
OSS_ENDPOINT = os.getenv('OSS_ENDPOINT')      # EndPoint（地域节点）
OSS_ARN = os.getenv('OSS_ARN')      # Role Arn      https://ram.console.aliyun.com/roles


def fetch_sts_token():
    clt = client.AcsClient(OSS_ACCESS_KEY, OSS_ACCESS_KEY_SECRET, OSS_REGION)
    req = AssumeRoleRequest.AssumeRoleRequest()

    req.set_accept_format('json')
    req.set_RoleArn(OSS_ARN)
    req.set_RoleSessionName('rethink-backend')

    body = clt.do_action_with_exception(req)

    j = json.loads(oss2.to_unicode(body))
    print('body:', j)

    """
    AssumeRole返回的临时用户密钥
    :str OSS_ACCESS_KEY: 临时用户的access key id
    :str access_key_secret: 临时用户的access key secret
    :int expiration: 过期时间，UNIX时间，自1970年1月1日UTC零点的秒数
    :str security_token: 临时用户Token
    :str request_id: 请求ID
    """
    access_key = j['Credentials']['AccessKeyId']
    access_key_secret = j['Credentials']['AccessKeySecret']
    security_token = j['Credentials']['SecurityToken']
    request_id = j['RequestId']
    expiration = oss2.utils.to_unixtime(j['Credentials']['Expiration'], '%Y-%m-%dT%H:%M:%SZ')
    return access_key, access_key_secret, security_token, request_id, expiration


access_key, access_key_secret, security_token, request_id, expiration = fetch_sts_token()
print(f'STS access_key: {access_key}, access_key_secret: {access_key_secret}')
print(f'STS security_token: {security_token}, request_id: {request_id}, expiration: {expiration}')

# 客户端使用临时授权
auth = oss2.StsAuth(access_key, access_key_secret, security_token)
# 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME)

# 上传一段字符串。Object名是motto.txt，内容是一段名言。
bucket.put_object('motto.txt', 'Never give up. - Jack Ma')
# 下载到本地文件
# bucket.get_object_to_file('motto.txt', '本地座右铭.txt')
# 删除名为motto.txt的Object
# bucket.delete_object('motto.txt')
