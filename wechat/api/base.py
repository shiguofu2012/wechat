# coding=utf-8
'''
wechat base
'''

import logging
import json
import inspect
from redis import Redis
import requests
from wechat.constants import WeChatErrorCode

# logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)


def _is_api_endpoint(obj):
    return isinstance(obj, BaseWechatAPI)


class BaseWeChatClient(object):
    '''
    wechat client API;
    implement access_token get method;
    '''

    _http = requests.Session()
    API_BASE_URL = ''

    def __new__(cls, *args, **kwargs):
        self = super(BaseWeChatClient, cls).__new__(cls)
        api_endpoints = inspect.getmembers(self, _is_api_endpoint)
        for name, api in api_endpoints:
            api_cls = type(api)
            api = api_cls(self)
            setattr(self, name, api)
        return self

    def __init__(self, appid, access_token=None, session=None):
        '''
        @params:
        appid            wechat appid
        access_token     wechat access_token
        session          use session storage, maybe redis, memcache or other;
                         it should have set/get/expire method
        '''
        self.appid = appid
        self.session = session
        self.timeout = 10
        if session is None:
            self.session = Redis()
        if access_token:
            self.session.set(self.access_token_key, access_token)

    @property
    def access_token_key(self):
        """cache access_token key as a property"""
        return '{0}_token'.format(self.appid)

    @property
    def access_token(self):
        """get accesstoken as a property"""
        access_token = self.session.get(self.access_token_key)
        if access_token:
            return access_token
        self.fetch_access_token()
        return self.session.get(self.access_token_key)

    def _fetch_access_token(self, url, params):
        res = self._http.get(url=url, params=params)
        try:
            res.raise_for_status()
        except requests.RequestException as reqex:
            raise Exception("ex: %s" % reqex)
        result = res.json()
        if 'errcode' in result and result['errcode'] != 0:
            errmsg = result.get('errmsg', '')
            raise Exception("ex: %s" % errmsg)
        expire_in = result.get("expires_in", 7200)
        self.session.set(
                self.access_token_key, result['access_token'], int(expire_in))
        return result

    def fetch_access_token(self):
        raise NotImplementedError

    def _decode_result(self, res):
        """loads requests json result"""
        try:
            result = json.loads(
                    res.content.decode('utf-8', 'ignore'), strict=False)
        except (TypeError, ValueError):
            LOG.error("decode resp error", exc_info=True)
            return res
        return result

    def _handle_result(
            self, resp, method, req_path, result_processor, **kwargs):
        result = resp
        if not isinstance(result, dict):
            result = self._decode_result(resp)
        else:
            result = resp

        if not isinstance(result, dict):
            return result

        if 'errcode' in result and result['errcode'] != 0:
            errcode = result['errcode']
            errmsg = result.get('errmsg', '')
            if errcode in (
                    WeChatErrorCode.INVALID_CREDENTIAL.value,
                    WeChatErrorCode.INVALID_ACCESS_TOKEN.value,
                    WeChatErrorCode.EXPIRED_ACCESS_TOKEN.value):
                LOG.debug("access token expired, fetch a new one and retry")
                self.fetch_access_token()
                kwargs['params']['access_token'] = self.access_token
                return self._request(
                        method, req_path,
                        result_processor=result_processor, **kwargs)
            raise Exception("req: %s, ex: %s" % (req_path, errmsg))
        return result if not result_processor else result_processor(result)

    def _request(self, method, req_path, **kwargs):
        if not req_path.startswith(('http', 'https')):
            api_base = kwargs.pop('api_base_uri', '') or self.API_BASE_URL
            url = api_base + req_path
        else:
            url = req_path
        if 'params' not in kwargs:
            kwargs['params'] = {}
        if isinstance(kwargs['params'], dict) and \
                'access_token' not in kwargs['params'] and \
                'secret' not in kwargs['params'] and \
                url.find("api.weixin.qq") != -1:
            kwargs['params']['access_token'] = self.access_token
        if isinstance(kwargs.get('data', ''), dict):
            body = json.dumps(kwargs['data'], ensure_ascii=False)
            # body = body.encode('utf-8')
            kwargs['data'] = body
        kwargs['timeout'] = kwargs.get('timeout', self.timeout)
        result_processor = kwargs.pop('result_processor', None)
        res = self._http.request(method=method, url=url, **kwargs)
        try:
            res.raise_for_status()
        except requests.RequestException as reqex:
            raise Exception("request url: %s, ex: %s" % (url, reqex))
        return self._handle_result(
                res, method, url, result_processor, **kwargs)

    def get(self, req_path, **kwargs):
        """request get method"""
        return self._request(method='get', req_path=req_path, **kwargs)

    def post(self, req_path, **kwargs):
        """request post method"""
        return self._request(method='post', req_path=req_path, **kwargs)


class BaseWechatAPI(object):
    """wechat api base class"""
    def __init__(self, client=None):
        self._client = client

    def _get(self, req_path, **kwargs):
        return self._client.get(req_path, **kwargs)

    def _post(self, req_path, **kwargs):
        return self._client.post(req_path, **kwargs)

    @property
    def access_token(self):
        """api get access_token as a property"""
        return self._client.access_token

    @property
    def appid(self):
        """api get appid as a property"""
        return self._client.appid

    @property
    def appsec(self):
        """api get appsec as a property"""
        return self._client.appsec

    @property
    def session(self):
        """API access session"""
        return self._client.session
