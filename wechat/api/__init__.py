# coding=utf-8
from wechat.api.base import BaseWeChatClient
from wechat.api.user import WechatUser
from wechat.api.qrcode import WechatQrcode
from wechat.api.menu import WechatMenu
from wechat.api.material import WechatMaterial
from wechat.api.jsapi import WechatJSAPI
from wechat.api.tools import WechaTools
from wechat.api.oauth import WechatAuth
from wechat.api.xcxapi import WeappAPI
from wechat.api.kefu_msg import WechatKefuMessage


class WechatClient(BaseWeChatClient):

    API_BASE_URL = 'https://api.weixin.qq.com/cgi-bin/'

    user = WechatUser()
    qrcode = WechatQrcode()
    menu = WechatMenu()
    material = WechatMaterial()
    jsapi = WechatJSAPI()
    tools = WechaTools()
    oauth = WechatAuth()
    weapp = WeappAPI()
    kefu_msg = WechatKefuMessage()

    def __init__(self, appid, appsec, access_token=None, session=None):
        super(WechatClient, self).__init__(appid, access_token, session)
        self.appid = appid
        self.appsec = appsec

    def fetch_access_token(self):
        """get access_token from wechat server"""
        return self._fetch_access_token(
                'https://api.weixin.qq.com/cgi-bin/token',
                params={
                    'grant_type': 'client_credential',
                    'appid': self.appid,
                    'secret': self.appsec})
