# coding=utf-8

import base64
import xmltodict
from wechat.utils import WechatSigner
from wechat.crypto.base import PrpCrypto


class BaseWechatCrypto(object):

    def __init__(self, token, encoding_aes_key, appid):
        self.key = base64.b64decode(encoding_aes_key + '=')
        assert len(self.key) == 32
        self.token = token
        self.appid = appid

    def _decrypt_message(self, msg, signature, timestamp, nonce):
        '''
        :param  msg: xml data or dict data of wechat post
        :param
        '''
        if not isinstance(msg, dict):
            msg = xmltodict.parse(msg)['xml']
        encrypt = msg['Encrypt']
        signer = WechatSigner()
        signer.add_data(self.token, timestamp, nonce, encrypt)
        if signer.signature != signature:
            raise Exception(
                    "signature from wx: %s, sign local: %s" %
                    (signer.signature, signature))
        return PrpCrypto(self.key).decrypt(encrypt, self.appid)

    def _encrypt_message(self, msg, nonce):
        pass


class WechatCrypto(BaseWechatCrypto):

    def __init__(self, token, encoding_aes_key, appid):
        super(WechatCrypto, self).__init__(token, encoding_aes_key, appid)

    def decrypt_message(self, msg, signature, timestamp, nonce):
        return self._decrypt_message(msg, signature, timestamp, nonce)

    def encrypt_message(self, msg, nonce):
        return self._encrypt_message(msg, nonce)
