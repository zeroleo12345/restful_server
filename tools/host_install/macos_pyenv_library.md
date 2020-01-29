### MySQL-python 库
[MAC OS X下安装MySQL-python](https://www.jianshu.com/p/5f4537d2c10f)

``` bash
export PATH="$PATH":/usr/local/mysql/bin
pip install -r requirements/requirements.txt
```

### Cryptography 库
``` bash
pip install cryptography --global-option=build_ext --global-option="-L/usr/local/opt/openssl/lib" --global-option="-I/usr/local/opt/openssl/include"

或者

export CPPFLAGS=-I/usr/local/opt/openssl/include; export LDFLAGS=-L/usr/local/opt/openssl/lib; pip install cryptography
```
