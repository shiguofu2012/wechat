# coding=utf-8
'''
wechat jsapi API
'''
import time
from wechat.api.base import BaseWechatAPI
from wechat.utils import random_str, WechatSigner


class WechatJSAPI(BaseWechatAPI):
    '''jsapi class'''

    def _get_ticket(self):
        '''get ticket'''
        return self._get(
            req_path='ticket/getticket',
            params={'type': 'jsapi'}
            )

    @property
    def _ticket_key(self):
        return "{0}_jsapi_ticket".format(self.appid)

    def get_jsapi_ticket(self):
        ticket_key = self._ticket_key
        ticket = self.session.get(ticket_key)
        if not ticket:
            jsapi_resp = self._get_ticket()
            ticket = jsapi_resp['ticket']
            expire = jsapi_resp['expires_in']
            self.session.set(self._ticket_key, ticket, int(expire))
        return ticket

    def get_jsapi_data(self, url):
        ticket = self.get_jsapi_ticket()
        nonce = random_str(16)
        now = int(time.time())
        data = [
            "noncestr={0}".format(nonce),
            "jsapi_ticket={0}".format(ticket),
            "timestamp={0}".format(int(now)),
            "url={0}".format(url)]
        signer = WechatSigner(delimer='&')
        signer.add_data(*data)
        sign = signer.signature
        jsapi_data = {
            "appId": self.appid,
            'timestamp': now,
            'nonceStr': nonce,
            "signature": sign
            }
        return jsapi_data
