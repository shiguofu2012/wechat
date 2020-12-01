# coding=utf-8


class WechatPayAPI(object):

    def __init__(self, client=None):
        self._client = client

    @property
    def appid(self):
        return self._client.appid

    @property
    def mch_id(self):
        return self._client.mch_id

    @property
    def api_key(self):
        return self._client.api_key

    def _get(self, url, **kwargs):
        return self._client.get(url, **kwargs)

    def _post(self, url, **kwargs):
        return self._client.post(url, **kwargs)
