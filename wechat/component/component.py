# coding=utf-8
"""
wechat component API
"""

import json
from urllib import quote
import requests
import xmltodict
from redis import Redis
from wechat.crypto import WechatCrypto
from wechat.constants import WeChatErrorCode, LOG
from wechat.component.messages import COMPONENT_MESSAGE_TYPE, \
        ComponentUnknownMessage


class BaseWechatComponent(object):
    """base class for component client"""

    _http = requests.Session()
    API_BASE_URL = 'https://api.weixin.qq.com/cgi-bin/'

    def __init__(
            self,
            component_appid,
            component_appsec,
            component_token,
            component_aeskey,
            component_ticket=None,
            session=None):
        self.component_appid = component_appid
        self.component_appsec = component_appsec
        self.crypto = WechatCrypto(
                component_token, component_aeskey, component_appid)
        if session is None:
            self.session = Redis()
        else:
            self.session = session
        if component_ticket:
            self.session.set(
                    self.component_verify_ticket_key, component_ticket, 600)

    def _decode_result(self, res):
        """loads requests json result"""
        try:
            result = json.loads(
                    res.content.decode('utf-8', 'ignore'), strict=False)
        except (TypeError, ValueError):
            LOG.debug("decode resp error", exc_info=True)
            return res
        return result

    def _handle_result(self, resp, req_path, method, **kwargs):
        if not isinstance(resp, dict):
            result = self._decode_result(resp)
        else:
            result = resp
        if not isinstance(result, dict):
            return result
        if 'errcode' in result and result['errcode'] != 0:
            errcode = result['errcode']
            errmsg = result.get("errmsg", '')
            if errcode in (
                    WeChatErrorCode.INVALID_CREDENTIAL.value,
                    WeChatErrorCode.INVALID_ACCESS_TOKEN.value,
                    WeChatErrorCode.EXPIRED_ACCESS_TOKEN.value):
                LOG.debug("access token expire, fetch a new one and try again")
                self.fetch_access_token()
                if 'params' in kwargs:
                    kwargs['params']['component_access_token'] = \
                            self.access_token
                return self._request(req_path, method, **kwargs)
            raise Exception("req_path: %s, error: %s" % (req_path, errmsg))
        return result

    def _request(self, req_path, method, **kwargs):
        url = self.API_BASE_URL + req_path

        if isinstance(kwargs.get('data', ''), dict):
            body = json.dumps(kwargs['data'], ensure_ascii=False)
            LOG.debug(body)
            # body = body.encode('utf-8')
            kwargs['data'] = body

        res = self._http.request(
            method=method,
            url=url,
            **kwargs
            )
        try:
            res.raise_for_status()
        except requests.RequestException as reqex:
            raise Exception("req url: %s, ex: %s" % (req_path, reqex))
        return self._handle_result(res, req_path, method, **kwargs)

    def get(self, req_path, **kwargs):
        '''simple get method'''
        return self._request(
            method='get',
            req_path=req_path,
            **kwargs)

    def post(self, req_path, **kwargs):
        '''simple post method'''
        return self._request(
            method='post',
            req_path=req_path,
            **kwargs
            )

    @property
    def component_verify_ticket_key(self):
        '''component ticket cache key'''
        return "{0}_ticket".format(self.component_appid)

    @property
    def component_verify_ticket(self):
        '''component ticket as a property'''
        return self.session.get(self.component_verify_ticket_key)

    @property
    def access_token_key(self):
        '''access_token cache key'''
        return "{0}_token".format(self.component_appid)

    @property
    def access_token(self):
        '''component access token as a property'''
        access_token = self.session.get(self.access_token_key)
        if access_token:
            return access_token
        self.fetch_access_token()
        return self.session.get(self.access_token_key)

    def fetch_access_token(self):
        post_data = {
            'component_appid': self.component_appid,
            'component_appsecret': self.component_appsec,
            'component_verify_ticket': self.component_verify_ticket}
        resp_data = self.post(
            req_path="component/api_component_token",
            data=post_data
            )
        expires = int(resp_data.get("expires_in", 7200))
        access_token = resp_data.get("component_access_token", "")
        self.session.set(self.access_token_key, access_token, expires)
        return resp_data


class ComponentClient(BaseWechatComponent):
    PRE_AUTH_URL = 'https://mp.weixin.qq.com/cgi-bin/componentloginpage?'\
            'component_appid={0}&pre_auth_code={1}&redirect_uri={2}&'\
            'auth_type={3}'
    MOBILE_AUTH_URL = 'https://mp.weixin.qq.com/safe/bindcomponent?'\
        'action=bindcomponent&no_scan=1&component_appid={0}&'\
        'pre_auth_code={1}&redirect_uri={2}&auth_type={3}#wechat_redirect'

    def get_pre_auth_url(self, redirect_url, auth_type=2):
        redirect_url = quote(redirect_url)
        pre_auth_url = self.PRE_AUTH_URL.format(
            self.component_appid, self.pre_auth_code, redirect_url, auth_type)
        return pre_auth_url

    def get_mobile_auth_url(self, redirect_url, auth_type=2):
        redirect_url = quote(redirect_url)
        pre_auth_url = self.MOBILE_AUTH_URL.format(
            self.component_appid, self.pre_auth_code, redirect_url, auth_type
            )
        return pre_auth_url

    @property
    def pre_auth_code(self):
        result = self.post(
            req_path="component/api_create_preauthcode",
            params={"component_access_token": self.access_token},
            data={"component_appid": self.component_appid}
            )
        return result['pre_auth_code']

    def parse_pushed_data(self, msg, msg_signature, timestamp, nonce):
        content = self.crypto.decrypt_message(
                msg, msg_signature, timestamp, nonce)
        message = xmltodict.parse(content)['xml']
        message_type = message['InfoType'].lower()
        message_class = COMPONENT_MESSAGE_TYPE.get(
                message_type, ComponentUnknownMessage)
        msg = message_class(message)
        if msg.type == 'component_verify_ticket':
            self.session.set(
                    self.component_verify_ticket_key, msg.verify_ticket)

    def query_auth(self, authorized_code):
        post_data = {
            "component_appid": self.component_appid,
            "authorization_code": authorized_code
            }
        query_result = self.post(
            req_path='component/api_query_auth',
            params={"component_access_token": self.access_token},
            data=post_data
            )
        return query_result

    def refresh_authorizer_token(
            self, authorized_appid, authorizer_refresh_token):
        post_data = {
            "component_appid": self.component_appid,
            "authorizer_appid": authorized_appid,
            "authorizer_refresh_token": authorizer_refresh_token}
        return self.post(
            req_path="component/api_authorizer_token",
            params={"component_access_token": self.access_token},
            data=post_data
            )

    def get_authorized_info(self, authorized_appid):
        post_data = {
            "component_appid": self.component_appid,
            "authorizer_appid": authorized_appid
            }
        return self.post(
            req_path="component/api_get_authorizer_info",
            params={"component_access_token": self.access_token},
            data=post_data
            )
