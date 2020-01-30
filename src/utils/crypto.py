import hashlib
import base64
#
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidKey

backend = default_backend()


def _autofill(key):
    if len(key) > 16:
        return key[:16]
    elif len(key) < 16:
        return key + '0'*(16-len(key))
    else:
        return key


def pkcs7_padding(data):
    if not isinstance(data, bytes):
        raise Exception('need type: bytes')

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    return padded_data


def pkcs7_unpadding(padded_data):
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    data = unpadder.update(padded_data)
    try:
        uppadded_data = data + unpadder.finalize()
    except ValueError:
        raise Exception('无效的加密信息!')
    return uppadded_data


def sha256(string):
    _sha256 = hashlib.sha256()
    _sha256.update(string.encode())
    return _sha256.hexdigest()


def md5(string):
    _md5 = hashlib.md5()
    _md5.update(string.encode())
    return _md5.hexdigest()


def scrypt_derive(salt: str, raw_password: str) -> bytes:
    """
    使用salt, 对raw_password原始密码加密
    :param salt:
    :param raw_password:
    :return:
    """
    kdf = Scrypt(
        salt=salt.encode(),
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=backend
    )
    return kdf.derive(raw_password.encode())


def scrypt_verify(salt: str, raw_password: str, password: bytes) -> bool:
    assert isinstance(password, bytes)
    #
    kdf = Scrypt(
        salt=salt.encode(),
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=backend
    )
    try:
        kdf.verify(raw_password.encode(), password)
        return True
    except InvalidKey:
        return False


def encrypt_aes(key, text, iv='\0'*16):
    """ aes比3des: 加解密速度快, 资源消耗低, 安全级别高 param: key: 密钥, 16个字符
            note: 当key或iv不足16个字符的时候, 后面补字符'0'; 当超过16个字符的时候, 截断为前面16个字符
            note: 标准Base64编码会出现字符+和/，在URL中不能作为参数，而urlsafe的base64编码，其实是把字符+和/分别变成-和_
        text: b''   // Byte类型
    """
    # 该模块采用如下定义：
    #   加解密算法为AES，密钥位长128，CBC模式，填充标准PKCS7  (有其他类型如: aes_256_cbc, aes_256_ecb)
    #   签名算法为SHA256的HMAC，密钥位长128位
    #   密钥可以设置过期时间
    key = _autofill(key)    # 当使用 aes_256时候, key需要32个字符; 而使用aes_128时, key需要16个字符
    iv = _autofill(iv)
    cipher = Cipher(algorithms.AES(key.encode()), modes.CBC(iv.encode()), backend=backend)
    encryptor = cipher.encryptor()
    text = pkcs7_padding(text.encode())
    s = encryptor.update(text)
    _enc = s + encryptor.finalize()
    return base64.urlsafe_b64encode(_enc).decode()


def decrypt_aes(key, text, iv='\0'*16):
    """ aes比3des: 加解密速度快, 资源消耗低, 安全级别高
    param:
        key: 密钥, 16个字符
        note: 当key或iv不足16个字符的时候, 后面补字符'0'; 当超过16个字符的时候, 截断为前面16个字符
        note: 标准Base64编码会出现字符+和/，在URL中不能作为参数，而urlsafe的base64编码，其实是把字符+和/分别变成-和_
    """
    key = _autofill(key)    # 当使用 aes_256时候, key需要32个字符; 而使用aes_128时, key需要16个字符
    iv = _autofill(iv)
    text = base64.urlsafe_b64decode(text)
    cipher = Cipher(algorithms.AES(key.encode()), modes.CBC(iv.encode()), backend=backend)
    decryptor = cipher.decryptor()
    return pkcs7_unpadding(decryptor.update(text)).decode()
