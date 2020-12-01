# coding=utf-8
'''
wechat user get API
'''

from wechat.api.base import BaseWechatAPI


class WechatQrcode(BaseWechatAPI):

    def create(self, qrcode_data):
        return self._post('qrcode/create', data=qrcode_data)

    def showqrcode(self, ticket):
        url = 'https://mp.weixin.qq.com/cgi-bin/showqrcode'
        params = {'ticket': ticket}
        res = self._get(url, params=params)
        return {'errcode': 0, 'errmsg': 'ok', 'data': res.content}
