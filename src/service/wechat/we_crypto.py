from trade import settings
#
from wechatpy.exceptions import InvalidSignatureException, InvalidAppIdException
from wechatpy.utils import check_signature
from wechatpy.crypto import WeChatCrypto
from wechatpy import parse_message


class WeCrypto(object):
    we_crypto = WeChatCrypto(token=settings.MP_TOKEN, encoding_aes_key=settings.MP_AES_KEY, app_id=settings.MP_APP_ID)

    @classmethod
    def decrypt_and_parse_message(cls, xml: str, msg_signature: str, timestamp: str, nonce: str):
        if msg_signature:
            try:
                xml = cls.we_crypto.decrypt_message(msg=xml, signature=msg_signature, timestamp=timestamp, nonce=nonce)
            except (InvalidAppIdException, InvalidSignatureException) as e:
                raise e
        return parse_message(xml)

    @classmethod
    def encrypt_message(cls, xml: str, msg_signature: str, timestamp: str, nonce: str):
        if msg_signature:
            return cls.we_crypto.encrypt_message(xml, nonce, timestamp)
        else:
            return xml

    @staticmethod
    def is_right_signature(signature: str, timestamp: str, nonce: str):
        try:
            check_signature(settings.MP_TOKEN, signature, timestamp, nonce)
            return True
        except InvalidSignatureException:
            return False
