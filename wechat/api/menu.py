# coding=utf-8
'''
wechat get/set menu API
'''

from wechat.api.base import BaseWechatAPI


class WechatMenu(BaseWechatAPI):
    """wechat service num menu operation"""
    def query(self):
        """query menu list"""
        return self._get('menu/get', result_processor=lambda x: x['menu'])

    def create(self, menu_data):
        """set menu to menu_data"""
        return self._post('menu/create', data=menu_data)
