# coding=utf-8


from wechat.api.base import BaseWechatAPI


class WechatKefuMessage(BaseWechatAPI):

    def send(self, msg_data):
        url = 'message/custom/send'
        return self._post(url, data=msg_data)
