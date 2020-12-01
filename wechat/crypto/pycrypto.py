# coding=utf-8

from Crypto.Cipher import AES


class WechatCipher(object):

    def __init__(self, key, offset):
        self.cipher = AES.new(key, AES.MODE_CBC, offset)

    def encrypt(self, msg):
        return self.cipher.encrypt(msg)

    def decrypt(self, msg):
        return self.cipher.decrypt(msg)
