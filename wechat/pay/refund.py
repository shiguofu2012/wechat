# coding=utf-8
'''refund API'''

from wechat.pay.base import WechatPayAPI
from wechat.utils import pay_sign, random_str


class WechatRefund(WechatPayAPI):
    '''wechat refund operation'''
    def refund(self, **kwargs):
        '''refund api'''
        data = self.check_refund_params(**kwargs)
        params = {
            'data': data,
            'data_type': "xml"
            }
        return self._post(
            url='secapi/pay/refund',
            **params
            )

    def refund_query(self, **kwargs):
        data = {
            "appid": self.appid,
            "mch_id": self.mch_id,
            "nonce_str": random_str(32)
            }
        if 'out_trade_no' in kwargs:
            data.update({"out_trade_no": kwargs['out_trade_no']})
        elif 'transaction_id' in kwargs:
            data.update({'transaction_id': kwargs['transaction_id']})
        elif 'out_refund_no' in kwargs:
            data.update({'out_refund_no': kwargs['out_refund_no']})
        elif 'refund_id' in kwargs:
            data.update({'refund_id': kwargs['refund_id']})
        else:
            raise Exception("Missing parameters")
        data['nonce_str'] = random_str(32)
        data['sign'] = pay_sign(data, self.api_key)
        return self._post(
            url='pay/refundquery',
            data=data,
            data_type='xml'
            )

    def check_refund_params(self, **kwargs):
        '''check refund params'''
        if 'out_trade_no' not in kwargs and 'transaction_id':
            raise Exception("Missing parameters out_trade_no or transaction_id")
        must_keys = (
            "out_refund_no",
            "total_fee",
            "refund_fee")
        left_keys = set(must_keys) - set(kwargs)
        if left_keys:
            raise Exception("Missing refund parameters %s" % left_keys)
        if 'appid' not in kwargs:
            kwargs['appid'] = self.appid
        if 'mch_id' not in kwargs:
            kwargs['mch_id'] = self.mch_id
        if 'nonce_str' not in kwargs:
            kwargs['nonce_str'] = random_str(32)
        sign = pay_sign(kwargs, self.api_key)
        kwargs['sign'] = sign
        return kwargs
