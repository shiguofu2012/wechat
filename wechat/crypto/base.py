# coding=utf-8

import struct
import socket
import base64
import json
from wechat.utils import random_str, byte2int
from wechat.crypto.pycrypto import WechatCipher


class BaseCrypto(object):

    def __init__(self, key, offset=None):
        if offset is None:
            offset = key[:16]
        self.cipher = WechatCipher(key, offset)

    def get_random_string(self):
        return random_str(16)

    def _encrypt(self, text, appid):
        if isinstance(text, unicode):
            text = text.encode("utf-8")
        net_len = struct.pack("I", socket.htonl(len(text)))
        rand_str = random_str(16)
        plain_text = rand_str + net_len + text + appid
        len_padding = 32 - (len(plain_text) % 32)
        if len_padding != 0:
            padding_str = len_padding * chr(len_padding)
            plain_text = plain_text + padding_str
        encrypted_str = self.cipher.encrypt(plain_text)
        return base64.b64encode(encrypted_str)

    def _decrypt(self, text, appid):
        if isinstance(text, unicode):
            text = text.encode("utf-8")
        plain_text = self.cipher.decrypt(base64.b64decode(text))
        padding_len = byte2int(plain_text[-1])
        content = plain_text[16: -padding_len]
        xml_len = socket.ntohl(struct.unpack('I', content[:4])[0])
        xml_content = content[4: xml_len + 4]
        from_appid = content[xml_len + 4:]
        if from_appid != appid:
            raise Exception(
                    "from appid: %s, appid: %s different" %
                    (from_appid, appid))
        return xml_content

    def _decrypt_userinfo(self, encrypted_msg):
        if isinstance(encrypted_msg, unicode):
            encrypted_msg = encrypted_msg.encode("utf-8")
        encrypted_msg = base64.b64decode(encrypted_msg)
        plain_text = self.cipher.decrypt(encrypted_msg)
        data_len = byte2int(plain_text[-1])
        data = plain_text[:-data_len]
        return json.loads(data)


class PrpCrypto(BaseCrypto):

    def decrypt(self, msg, appid):
        return self._decrypt(msg, appid)

    def encrypt(self, msg, appid):
        return self._encrypt(msg, appid)


class WeappCrypto(BaseCrypto):

    def __init__(self, key, offset):
        key = base64.b64decode(key)
        offset = base64.b64decode(offset)
        super(WeappCrypto, self).__init__(key, offset)

    def decrypt(self, msg):
        return self._decrypt_userinfo(msg)
