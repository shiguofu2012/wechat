# coding=utf-8
'''
utils function
'''
import hashlib
import random
import json
from xml.parsers.expat import ExpatError
import requests
import xmltodict
from wechat.constants import LOG


class ObjectDict(dict):
    '''
    Makes a dictionary behave like an object, with attribute-style access.
    '''

    def __getattr__(self, key):
        if key in self:
            return self[key]
        return None

    def __setattr__(self, key, value):
        self[key] = value


class WechatSigner(object):
    '''wechat data signer'''

    def __init__(self, delimer=''):
        self._data = []
        self.delimer = delimer

    def add_data(self, *args):
        '''add signed data'''
        for data in args:
            self._data.append(data)

    @property
    def signature(self):
        '''signature calc'''
        self._data.sort()
        str_to_sign = self.delimer.join(self._data)
        return hashlib.sha1(str_to_sign).hexdigest()


class HttpRequest(object):
    '''http get/post method'''

    _http = requests.session()
    timeout = 10

    def _request(self, method, url, **kwargs):
        if isinstance(kwargs.get("data", ""), dict):
            data = kwargs['data']
            if 'data_type' not in kwargs or \
                    kwargs.get("data_type").lower() == 'json':
                kwargs['data'] = json.dumps(data)
            else:
                kwargs['data'] = dict_to_xml(data)
            kwargs.pop("data_type", '')
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        resp = self._http.request(
            method=method,
            url=url,
            **kwargs
            )
        try:
            resp.raise_for_status()
        except requests.RequestException as reqex:
            LOG.error(
                    "method: %s, url: %s, ex: %s",
                    method, url, reqex, exc_info=True)
            raise Exception("request url: %s ex: %s", url, reqex)
        return resp.content

    def get(self, url, **kwargs):
        '''http get'''
        return self._request(
            method='GET',
            url=url,
            **kwargs
            )

    def post(self, url, **kwargs):
        '''http post'''
        return self._request(
            method='POST',
            url=url,
            **kwargs
            )


def check_signature(token, signature, timestamp, nonce):
    """
    check wechat callback signature

    :param token: wechat callback token, write by ourself
    :param signature: wechat signature sent by wechat server
    :param timestamp: wechat timestamp sent by wechat server
    :param nonce: wechat nonce sent by wechat server
    """
    signer = WechatSigner()
    signer.add_data(token, timestamp, nonce)
    if signer.signature != signature:
        raise Exception(
            "sign from wecaht: %s, diff with sign local: %s" %
            (signature, signer.signature))


def random_str(length):
    """
    return random string
    :param   length: random string length
    :return: random string
    """
    all_strs = 'abcdefghijklmnopqrstuvwxyz0123456789'
    rand_str_list = random.sample(all_strs, length)
    return ''.join(rand_str_list)


def dict_to_xml(data):
    '''dict data to xml data'''
    xml = ['<xml>\n']
    for key in sorted(data):
        value = data[key]
        if isinstance(value, unicode):
            value = value.encode("utf-8")
        if isinstance(value, int) or \
                (isinstance(value, (str, unicode)) and value.isdigit()):
            xml.append("<{0}>{1}</{0}>\n".format(key, value))
        else:
            xml.append("<{0}><![CDATA[{1}]]></{0}>\n".format(key, value))
    xml.append("</xml>")
    return ''.join(xml)


def xml_to_dict(data_str):
    '''xml data to dict data'''
    dict_data = {}
    try:
        dict_data = xmltodict.parse(data_str)
    except (xmltodict.ParsingInterrupted, ExpatError):
        LOG.error("xml parse error: %s", data_str, exc_info=True)
    return dict_data.get('xml', {})


def byte2int(char):
    '''byte to int'''
    return ord(char)


def format_params(params):
    '''sort signed data'''
    params_list = []
    for key in sorted(params):
        value = params[key]
        if isinstance(value, unicode):
            value = params[key].encode("utf-8")
        tmp_str = "{0}={1}".format(key, value)
        params_list.append(tmp_str)
    return "&".join(params_list)


def pay_sign(params, api_key=''):
    '''wechat pay sign data'''
    params = format_params(params)
    if api_key:
        params += "&key={0}".format(api_key)
    return hashlib.md5(params).hexdigest().upper()
