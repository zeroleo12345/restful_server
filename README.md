# 系统简介

[![CircleCI](https://circleci.com/gh/zeroleo12345/restful_server/tree/master.svg?style=svg&circle-token=eece7116845f82f71da5effde84461ddfb3d33be)](https://circleci.com/gh/zeroleo12345/restful_server/tree/master)

pppoe用户充值系统

## 环境
python3 + django 1 + docker

## 启动充值系统

```bash
# 启动步骤:
    decrypt docker.env                    # 8->7
    docker-compose build --no-cache
    docker-compose up -d redis mysql
    docker-compose up web

# 本地验证:
    因为Dockerfile内定义了8000端口映射到docker内部的80端口,
    浏览器访问 http://127.0.0.1:8000/
```
