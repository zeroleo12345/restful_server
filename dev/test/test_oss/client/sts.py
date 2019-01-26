#!/usr/bin/env python3
import json
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


def get_x_oss_callback(oss_callback_url):
    # 准备回调参数，更详细的信息请参考 https://help.aliyun.com/document_detail/31989.html
    callback_dict = {
        'callbackUrl': f'{oss_callback_url}',
        # 'callbackHost': 'oss-cn-hangzhou.aliyuncs.com',

        # 'callbackBodyType': 'application/x-www-form-urlencoded',
        # 'callbackBody': 'object=${object}&size=${size}&mimeType=${mimeType}',

        'callbackBodyType': 'application/json',
        'callbackBody': '''{"bucket": ${bucket}, "object": ${object}, "etag": ${etag}, "size": ${size}}''',
    }
    # 回调参数是json格式，并且base64编码
    callback_param = json.dumps(callback_dict).strip()
    x_oss_callback = oss2.utils.b64encode_as_string(callback_param)
    return x_oss_callback


def fetch_sts_token(key, oss_access_key_id, oss_access_key_secret, oss_arn, oss_bucket_name, oss_region):
    role = AssumeRoleRequest.AssumeRoleRequest()
    role.set_accept_format('json')
    role.set_RoleArn(oss_arn)
    role.set_RoleSessionName('rethink-backend')
    resource = f'["acs:oss:*:*:{oss_bucket_name}/{key}"]'
    policy = '{"Statement": [ { "Action": [ "oss:*" ], "Effect": "Allow", "Resource": %s} ], "Version": "1" }' % (resource,)
    role.set_Policy(policy)

    clt = client.AcsClient(oss_access_key_id, oss_access_key_secret, oss_region)
    body = clt.do_action_with_exception(role)

    j = json.loads(oss2.to_unicode(body))
    print('body:', j)

    """
    AssumeRole返回的临时用户密钥
    :str access_key_id: 临时用户的access key id
    :str access_key_secret: 临时用户的access key secret
    :int expiration: 过期时间，UNIX时间，自1970年1月1日UTC零点的秒数
    :str security_token: 临时用户Token
    :str request_id: 请求ID
    """
    access_key_id = j['Credentials']['AccessKeyId']
    access_key_secret = j['Credentials']['AccessKeySecret']
    security_token = j['Credentials']['SecurityToken']
    request_id = j['RequestId']
    expiration = oss2.utils.to_unixtime(j['Credentials']['Expiration'], '%Y-%m-%dT%H:%M:%SZ')
    return access_key_id, access_key_secret, security_token, request_id, expiration


def upload_and_callback(key, access_key_id, access_key_secret, security_token, x_oss_callback, oss_endpoint, oss_bucket_name):
    # 参考:  https://yq.aliyun.com/articles/68863
    # 方式1: 回调参数放在消息头中的 x-oss-callback。这种方式比较常用，推荐该方式；
    headers = {}
    if x_oss_callback:
        headers['x-oss-callback'] = x_oss_callback
    # 方式2: 通过 QueryString 中的参数callback携带回调参数. (例如callback=x_oss_callback).。
    pass

    # 方式1: 非临时授权
    # auth = oss2.Auth(access_key_id, access_key_secret)
    # bucket = oss2.Bucket(auth, OSS_ENDPOINT, oss_bucket_name)

    # 方式2: 客户端临时授权
    auth = oss2.StsAuth(access_key_id, access_key_secret, security_token)
    # 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
    bucket = oss2.Bucket(auth, oss_endpoint, oss_bucket_name)

    # 上传
    response = bucket.put_object(key, "Anything you're good at contributes to happiness.", headers)
    print(f'response: ', response.resp.read())
    print(f'json: ', response.resp.response.json())


def upload(access_key_id, access_key_secret, security_token, oss_endpoint, oss_bucket_name):
    # 客户端使用临时授权
    auth = oss2.StsAuth(access_key_id, access_key_secret, security_token)
    # 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
    bucket = oss2.Bucket(auth, oss_endpoint, oss_bucket_name)

    # 上传一段字符串。Object名是motto.txt，内容是一段名言。
    bucket.put_object('motto.txt', 'Never give up. - Jack Ma')
    # 下载到本地文件
    # bucket.get_object_to_file('motto.txt', '本地座右铭.txt')
    # 删除名为motto.txt的Object
    # bucket.delete_object('motto.txt')


if __name__ == "__main__":
    import os
    """
    :param OSS_ACCESS_KEY_ID: 子用户的 access key id
    :param OSS_ACCESS_KEY_SECRET: 子用户的 access key secret
    :param OSS_ARN: STS角色的Arn
    """
    OSS_ACCESS_KEY_ID = os.getenv('OSS_ACCESS_KEY_ID')
    OSS_ACCESS_KEY_SECRET = os.getenv('OSS_ACCESS_KEY_SECRET')
    OSS_BUCKET_NAME = os.getenv('OSS_BUCKET_NAME')
    OSS_REGION = os.getenv('OSS_REGION', 'cn-hongkong')
    OSS_ENDPOINT = os.getenv('OSS_ENDPOINT')      # EndPoint（地域节点）
    OSS_ARN = os.getenv('OSS_ARN')      # Role Arn      https://ram.console.aliyun.com/roles
    OSS_CALLBACK_URL = os.getenv('OSS_CALLBACK_URL')
    KEY = 'file/quote.txt'

    access_key_id, access_key_secret, security_token, request_id, expiration = fetch_sts_token(KEY, OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET, OSS_ARN, OSS_BUCKET_NAME, OSS_REGION)
    x_oss_callback = get_x_oss_callback(OSS_CALLBACK_URL)
    print(f'STS access_key_id: {access_key_id}, access_key_secret: {access_key_secret}')
    print(f'STS security_token: {security_token}, request_id: {request_id}, expiration: {expiration}')

    # KEY = data['key']
    # access_key_id = data['access_key_id']
    # access_key_secret = data['access_key_secret']
    # security_token = data['security_token']
    # x_oss_callback = data['x_oss_callback']
    # from pprint import pprint; import pdb; pdb.set_trace()
    upload_and_callback(KEY, access_key_id, access_key_secret, security_token, x_oss_callback, OSS_ENDPOINT, OSS_BUCKET_NAME)
