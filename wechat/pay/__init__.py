# coding=utf-8
"""
wechat pay client
"""

import inspect
# from wechat.constants import LOG
from wechat.utils import xml_to_dict, HttpRequest, pay_sign
from wechat.pay.base import WechatPayAPI
from wechat.pay.order import WechatOrder
from wechat.pay.refund import WechatRefund


def _is_api_end_point(obj):
    return isinstance(obj, WechatPayAPI)


class WechatPay(object):
    """
    微信支付接口

    """
    _http = HttpRequest()
    API_BASE_URL = 'https://api.mch.weixin.qq.com/'
    order = WechatOrder()
    refund = WechatRefund()

    def __new__(cls, *args, **kwargs):
        self = super(WechatPay, cls).__new__(cls, *args, **kwargs)
        api_endpoints = inspect.getmembers(self, _is_api_end_point)
        for name, _api in api_endpoints:
            api_cls = type(_api)
            _api = api_cls(self)
            setattr(self, name, _api)
        return self

    def __init__(self, appid, api_key, mch_id, mch_cert, mch_key):
        self.appid = appid
        self.api_key = api_key
        self.mch_id = mch_id
        self.mch_cert = mch_cert
        self.mch_key = mch_key
        self.timeout = 10

    def _handle_result(self, resp):
        """process wechat api return"""
        xml = resp
        resp_data = xml_to_dict(xml)
        return_code = resp_data['return_code']
        return_msg = resp_data.get("return_msg")
        result_code = resp_data.get("result_code")
        errcode = resp_data.get("err_code")
        err_code_des = resp_data.get("err_code_des")
        if return_code != 'SUCCESS' or result_code != 'SUCCESS':
            print(return_code, result_code, err_code_des)
            raise Exception(
                u"return_msg:{}, errcode:{}, errcode_des:{}".
                format(return_msg, errcode, err_code_des))
        return resp_data

    def get(self, url, **kwargs):
        """http get method"""
        if not url.startswith(("http", "https")):
            api_base_url = kwargs.pop("api_base_url", "") or self.API_BASE_URL
            url = "{base}{path}".format(base=api_base_url, path=url)
        resp = self._http.get(url, **kwargs)
        return self._handle_result(resp)

    def post(self, url, **kwargs):
        """http post method"""
        if not url.startswith(("http", "https")):
            api_base_url = kwargs.pop("api_base_url", "") or self.API_BASE_URL
            url = "{base}{path}".format(base=api_base_url, path=url)
        if self.mch_cert and self.mch_key and 'cert' not in kwargs:
            kwargs['cert'] = (self.mch_cert, self.mch_key)
        resp = self._http.post(url, **kwargs)
        return self._handle_result(resp)

    def parse_payment_result(self, xml_data):
        """check wechat pay ok pushed data"""
        data = xml_to_dict(xml_data)
        if not data:
            raise Exception("parse data error data: %s", xml_data)
        sign = data.pop("sign", "")
        real_sign = pay_sign(data, self.api_key)
        if sign != real_sign:
            raise Exception(
                    "sign error, sign: %s, real_sign: %s" % (sign, real_sign))
        return data
