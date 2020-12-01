# coding=utf-8

from wechat.api.base import BaseWechatAPI


class WechaTools(BaseWechatAPI):

    def short_url(self, long_url):
        """
        long url to short url
        """
        data = {
            'action': 'long2short',
            'long_url': long_url
            }
        return self._post(
            req_path='shorturl',
            params={},
            data=data
            )
