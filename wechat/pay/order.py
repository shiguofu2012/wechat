# coding=utf-8

'''wechat order operation'''

import time
from wechat.utils import pay_sign, random_str
from wechat.pay.base import WechatPayAPI


class WechatOrder(WechatPayAPI):
    '''wechat order object'''

    def create(self, **kwargs):
        '''create order to wechat server'''
        kwargs['data'] = self.check_create_params(**kwargs['data'])
        kwargs['data_type'] = 'xml'
        return self._post(
            url='pay/unifiedorder',
            **kwargs
            )

    def get_jsapi_data(self, ret_data):
        prepay_id = ret_data['prepay_id']
        now = int(time.time())
        data = {
            "appId": self.appid,
            "timeStamp": now,
            "nonceStr": random_str(32),
            "package": "prepay_id={0}".format(prepay_id),
            "signType": "MD5"
            }
        sign = pay_sign(data, self.api_key)
        data['paySign'] = sign
        return data

    def query(self, out_trade_no=None, transaction_id=None):
        '''query order state'''
        if out_trade_no is None and transaction_id is None:
            raise Exception("Missing parameter out_trade_no or transaction_id")
        data = {
            "appid": self.appid,
            "mch_id": self.mch_id,
            "nonce_str": random_str(32)
            }
        if out_trade_no:
            data.update({'out_trade_no': out_trade_no})
        elif transaction_id:
            data.update({"transaction_id": transaction_id})
        sign = pay_sign(data, self.api_key)
        data['sign'] = sign
        return self._post(
            url='pay/orderquery',
            data=data,
            data_type="xml"
            )

    def close(self, out_trade_no):
        data = {
            "appid": self.appid,
            "mch_id": self.mch_id,
            "nonce_str": random_str(32),
            "out_trade_no": out_trade_no
            }
        sign = pay_sign(data, self.api_key)
        data['sign'] = sign
        return self._post(
            url='pay/closeorder',
            data=data,
            data_type='xml'
            )

    def check_create_params(self, **kwargs):
        '''check the parameters of creating order'''
        must_keys = (
            "body",
            "out_trade_no",
            "total_fee",
            "spbill_create_ip",
            "notify_url",
            "trade_type"
            )
        left_keys = set(must_keys) - set(kwargs.keys())
        if left_keys:
            raise Exception("Missing params %s", left_keys)
        trade_type = kwargs['trade_type']
        if trade_type in ['JSAPI'] and 'openid' not in kwargs:
            raise Exception(
                    "Missing params: openid, trade_type: %s" % trade_type)
        elif trade_type in ['NATIVE'] and 'product_id' not in kwargs:
            raise Exception(
                    "Missing params: product_id, trade_type: %s" % trade_type)
        if 'appid' not in kwargs:
            kwargs['appid'] = self.appid
        if 'mch_id' not in kwargs:
            kwargs['mch_id'] = self.mch_id
        if 'nonce_str' not in kwargs:
            kwargs['nonce_str'] = random_str(32)
        sign = pay_sign(kwargs, self.api_key)
        kwargs['sign'] = sign
        return kwargs
