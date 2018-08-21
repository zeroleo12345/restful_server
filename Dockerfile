# https://hub.docker.com/_/python/, 镜像名说明: 前缀python可选自url; 后缀:3.6-alpine为网页上的tag, 如不指定后缀, 则为:latest
FROM python:3.6.5-alpine3.6

# 一. 安装 linux package. (使用: 阿里云 alpine 镜像)
# 二. 安装 python package.
# 三. 清理不需保留的包 且 安装需保留的包.
ADD requirements /app/requirements/
RUN echo "http://mirrors.aliyun.com/alpine/v3.6/main/" > /etc/apk/repositories
RUN apk add --no-cache --virtual .build-deps \
    mariadb-dev curl-dev build-base gcc musl-dev python3-dev libffi-dev \
    && pip3 install --no-cache-dir -r /app/requirements/test.txt --trusted-host mirrors.aliyun.com --index-url http://mirrors.aliyun.com/pypi/simple \
    && apk del .build-deps \
    && export PYCURL_SSL_LIBRARY=openssl \
    && apk add --no-cache mariadb-client-libs libcurl

# WORKDIR: 如果目录不存在, 则自动创建
WORKDIR /app/src/
ADD src /app/src/

ADD bin /app/bin/
# docker-compose.yml 会覆盖 entrypoint
ENTRYPOINT ["/app/bin/restful_server_deamon.sh"]
