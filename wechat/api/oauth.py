# coding=utf-8
'''wechat oauth2.0 API'''

from urllib import quote
from wechat.api.base import BaseWechatAPI


class WechatAuth(BaseWechatAPI):
    """wechat H5 authorized"""

    OAUTH_URL = 'https://open.weixin.qq.com/connect/oauth2/authorize?'\
        'appid={appid}&redirect_uri={redirect_uri}&response_type=code'\
        '&scope={scope}&state={state}#wechat_redirect'

    @property
    def authorize_url(self, redirect_uri, scope='snsapi_userinfo', state=''):
        """get authorized url"""
        redirect_uri = quote(redirect_uri)
        url = self.OAUTH_URL.format(
            appid=self.appid,
            redirect_uri=redirect_uri,
            scope=scope,
            state=state
            )
        return url

    def user_access_token_key(self, openid):
        return "{0}_access_token".format(openid)

    def user_refresh_access_token_key(self, openid):
        return "{0}_refresh_token".format(openid)

    def fetch_user_access_token(self, code):
        """fetch user access token by authorized code"""
        params = {
            'appid': self.appid,
            'secret': self.appsec,
            'code': code,
            'grant_type': 'authorization_code'
            }
        resp = self._get(
            req_path='sns/oauth2/access_token',
            params=params,
            api_base_uri='https://api.weixin.qq.com/'
            )
        access_token = resp['access_token']
        expire = resp['expires_in']
        refresh_token = resp['refresh_token']
        openid = resp['openid']
        self.session.set(
                self.user_access_token_key(openid), access_token, int(expire))
        self.session.set(
                self.user_refresh_access_token_key(openid),
                refresh_token, 30 * 86400)
        return resp

    def refresh_user_access_token(self, refresh_token):
        '''fetch user access token by refresh token'''
        params = {
            'appid': self.appid,
            'secret': self.appsec,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
            }
        resp = self._get(
            req_path='sns/oauth2/refresh_token',
            params=params,
            api_base_uri='https://api.weixin.qq.com/'
            )
        openid = resp['openid']
        access_token = resp['access_token']
        expire = resp['expires_in']
        refresh_token = resp['refresh_token']
        self.session.set(
                self.user_access_token_key(openid), access_token, int(expire))
        self.session.set(
                self.user_refresh_access_token_key(openid),
                refresh_token, 30 * 86400)
        return resp

    def get_user_info(self, openid, access_token=None, lang='zh_CN'):
        params = {
            "openid": openid,
            "lang": lang
            }
        if access_token is None:
            access_token = self.session.get(self.user_access_token_key(openid))
            if not access_token:
                raise Exception("Missing access_token parameters")
            params.update({'access_token': access_token})
        return self._get(
            req_path='sns/userinfo',
            params=params,
            api_base_uri='https://api.weixin.qq.com/'
            )
