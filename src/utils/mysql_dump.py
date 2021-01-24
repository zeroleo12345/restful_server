import os
import subprocess
import datetime
# 第三方库
from dynaconf import settings
from qiniu import Auth, put_file

HOME = os.path.expanduser("~")
# 七牛秘钥
QN_ACCESS_KEY = settings.get('QN_ACCESS_KEY')
QN_SECRET_KEY = settings.get('QN_SECRET_KEY')
# 上传空间
QN_BUCKET = settings.get('QN_BUCKET')
# 构建鉴权对象
qn_auth = Auth(QN_ACCESS_KEY, QN_SECRET_KEY)


def init_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-host', metavar='<host>', type=str, help='host', required=True, default='localhost', dest='host')
    parser.add_argument('-u', metavar='<username>', type=str, help='username', required=True, dest='username')
    parser.add_argument('-P', metavar='<port>', type=int, help='port', required=False, default=3306, dest='port')
    parser.add_argument('-p', metavar='<password>', type=str, help='password', required=True, dest='password')
    parser.add_argument('-db', metavar='<database name>', type=str, help='database', required=True, dest='db')
    parser.add_argument('-dir', metavar='<destiny directory>', type=str, help='directory', required=True, dest='directory')
    return parser.parse_args()


def compress(file_path):
    """ 压缩 """
    cmd = 'gzip {file_path}'.format(file_path=file_path)
    ret = subprocess.check_output(cmd, shell=True)
    print(f'压缩命令: {cmd}, 结果: {ret}')

    gzip_file_path = file_path + '.gz'
    ret = os.path.isfile(gzip_file_path)
    if ret is False:
        raise Exception('gzip mysqldump failed')

    return gzip_file_path


def upload(file_path):
    # 要上传文件的本地路径
    if not os.path.exists(file_path):
        raise Exception('file {file_path} not exist'.format(file_path=file_path))

    # 上传到七牛后的文件名
    filename = os.path.basename(file_path)
    key = filename

    # 生成上传 Token，可以指定过期时间等
    token = qn_auth.upload_token(QN_BUCKET, key=key, expires=3600)

    # 上传
    ret, info = put_file(token, key=key, file_path=file_path)
    print(f'文件上传结果: {ret}, 细节: {info}')


def main():
    args = init_args()
    # 导出
    file_path = dump(
        host=args.host, port=args.port,
        username=args.username, password=args.password, db=args.db,
        directory=args.directory
    )
    # 压缩文件
    file_path = compress(file_path)
    # 上传文件到七牛
    upload(file_path)


def dump(host, port, username, password, db, directory):
    directory = os.path.expanduser(directory)
    if not os.path.exists(directory):
        os.mkdir(directory)

    now = datetime.datetime.now()
    filename = db + '_' + now.strftime('%d_%H:00') + '.sql'
    output = os.path.join(directory, filename)

    cmd = 'mysqldump --default-character-set=utf8mb4 -h{host} -P{port} -u{user} -p"{password}" --single-transaction {db} > {output}'.format(
        host=host, port=port, user=username,  password=password, db=db, output=output
    )

    ret = subprocess.check_output(cmd, shell=True)
    print(f'数据库导出命令: {cmd}, 结果: {ret}')

    # File check
    ret = os.path.isfile(output)
    if ret is False:
        raise Exception('File not exist')

    return output


main()


def usage():
    print("""
    容器内运行:
        python mysql_dump.py -host mysql -P 3306 -u root -p 'root' -db guanjia -dir '/app/data/backup/'

    主机上运行:
        python mysql_dump.py -host 127.0.0.1 -P 33333 -u root -p 'root' -db guanjia -dir './'

    """)
