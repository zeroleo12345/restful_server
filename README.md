# 系统简介

[![CircleCI](https://circleci.com/gh/zeroleo12345/restful_server/tree/master.svg?style=svg&circle-token=eece7116845f82f71da5effde84461ddfb3d33be)](https://circleci.com/gh/zeroleo12345/restful_server/tree/master)

pppoe用户充值系统 (基于 python3 + django 1.11 + docker)


## 环境变量说明
``` bash
ENVIRONMENT:
    非production: 不会创建公众号菜单; get_user_info_from_wechat 时不会调用fetch_access_token();
```


## 启动充值系统步骤

- 主程序
``` bash
1. 修改配置
  - decrypt .env.x
  - direnv allow .
  - 修改.env   (原则: 尽量不修改docker-compose.yml)

2. 构建 docker
  - docker-compose build --no-cache

3. 运行 docker
  - docker-compose up -d redis mysql
  Debug 版本:   export ENVIRONMENT=unittest; export DEBUG=True; docker-compose up api
  Release 版本: export ENVIRONMENT=production; export DEBUG=False; docker-compose up api    # 或者执行 bin/release.sh

4. 本地验证:
  - 浏览器访问 http://127.0.0.1:8000/   (Dockerfile内定义了8000端口映射到docker内的80端口)
```


- 其他程序
```
# 更新微信支付订单状态
python manage.py manage_order

# 统计订单金额
python manage.py statistics
```


## 测试案例
``` bash
sh dev/runtest_in_docker.sh
```


## 连接MySQL
``` bash
pip install mycli
mycli -h 127.0.0.1 -P 33333 -u root --password=root -D trade
```


## Migration
``` bash
docker-compose exec api  python manage.py makemigrations
docker-compose exec api  python manage.py migrate --database=default

# 清理历史migrations文件, 并重新生成表结构
  - 清理目录文件:  rm -rf migrations/*
  - 清理数据库:    drop database trade; create database trade;
  - 执行上面的Migration动作
```
