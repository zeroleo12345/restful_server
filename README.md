# 系统简介

[![CircleCI](https://circleci.com/gh/zeroleo12345/restful_server/tree/master.svg?style=svg&circle-token=eece7116845f82f71da5effde84461ddfb3d33be)](https://circleci.com/gh/zeroleo12345/restful_server/tree/master)

pppoe用户充值系统 (基于 python3 + django 1 + docker)


## 启动充值系统步骤
```bash
1. 修改配置
  - decrpyt .envrc.x
  - 修改.envrc. (原则: 尽量不用修改docker-compose.yml)

2. 运行docker
  - docker-compose build --no-cache
  - docker-compose up -d redis mysql
  - export ENVIRONMENT=unittest; export DEBUG=True; docker-compose up web     # 生产运行覆盖参数 DEBUG=False

3. 本地验证:
  - 浏览器访问 http://127.0.0.1:8000/   (Dockerfile内定义了8000端口映射到docker内的80端口)
```

## 测试案例
``` bash
sh dev/runtest_in_docker.sh
```
