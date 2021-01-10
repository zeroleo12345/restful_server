# 系统简介

[![CircleCI](https://circleci.com/gh/zeroleo12345/restful_server/tree/master.svg?style=svg&circle-token=eece7116845f82f71da5effde84461ddfb3d33be)](https://circleci.com/gh/zeroleo12345/restful_server/tree/master)

pppoe用户充值系统 (基于 python3 + django 2.1.13 + docker)

公众号调试地址: `https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx54d296959ee50c0b&redirect_uri=http://wechat.lynatgz.cn&response_type=code&scope=snsapi_userinfo`


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
  - 浏览器访问 http://127.0.0.1:8000/   (docker-compose.yml内定义了8000端口映射到docker内的80端口)
```


- 其他程序
```
# 定时任务: 更新微信支付订单状态; 统计订单金额
python src/manage.py timer_processor
```


## 测试案例
``` bash
sh tools/runtest_in_docker.sh
```


## 连接MySQL
``` bash
pip install mycli
mycli -h 127.0.0.1 -P 33333 -u root --password=root -D trade
```


## Migration
``` bash
# 首次执行需指定app
docker-compose exec api  python src/manage.py makemigrations trade

# 非首次执行
docker-compose exec api  python src/manage.py makemigrations
docker-compose exec api  python src/manage.py migrate --database=default

# 清理历史migrations文件, 并重新生成表结构
  - 清理目录文件:  rm -rf migrations/*
  - 清理数据库:    DROP DATABASE trade; CREATE DATABASE trade CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  - 执行上面的Migration动作
```


## 导出数据库 / 备份数据库
``` bash
mysqldump --default-character-set=utf8mb4 -h 127.0.0.1 -P 33333 -u root --password=root -c --databases trade > ./dump.sql
```
