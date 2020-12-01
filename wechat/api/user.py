# coding=utf-8
'''
wechat user get API
'''

from wechat.api.base import BaseWechatAPI


class WechatUser(BaseWechatAPI):

    def get(self, user_id, lang='zh_CN'):
        """
        get subscriber user info
        """
        return self._get(
            'user/info',
            params={'openid': user_id,
                    'lang': lang})

    def user_list(self, next_openid=''):
        params = {'next_openid': next_openid}
        return self._get(
                'user/get',
                params=params
                )

    def create_tag(self, name):
        url = 'tags/create'
        params = {"tag": {'name': name}}
        return self._post(
                url,
                params=params
                )

    def get_tags(self):
        url = 'tags/get'
        return self._get(url, params={})

    def update_tag(self, tag_id, name):
        url = 'tags/update'
        data = {'tag': {'id': tag_id, 'name': name}}
        return self._post(url, data=data)

    def delete_tag(self, tag_id):
        url = 'tags/delete'
        data = {'tag': {"id": tag_id}}
        return self._post(url, data=data)
