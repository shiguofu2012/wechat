# coding=utf-8

from wechat.api.base import BaseWechatAPI


class WeappAPI(BaseWechatAPI):

    def fetch_user_session(self, code):
        params = {
            'appid': self.appid,
            "secret": self.appsec,
            'js_code': code,
            'grant_type': 'authorization_code'
            }
        return self._get(
            req_path='sns/jscode2session',
            params=params,
            api_base_uri='https://api.weixin.qq.com/'
            )

    def generate_qrcode(self, page, scene, width, is_hyaline):
        '''
        :param page: the path path of qrcode
        :param scene: the params pass to the page;
        :param is_hyaline: 是否是透明
        :param width: the width of the qrcode
        '''
        params = {
                'scene': scene,
                'page': page,
                'width': width,
                'is_hyaline': is_hyaline
                }
        return self._post(
                req_path='wxa/getwxacodeunlimit',
                data=params,
                api_base_uri='https://api.weixin.qq.com/'
                )

    def send_template_msg(self, data):
        url = 'https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send'
        must_key = ("touser", "template_id", "form_id")
        can_be_null_keys = ("page", "data")
        send_data = {}
        for key in must_key:
            send_data[key] = data[key]
        for key in can_be_null_keys:
            value = data.get(key)
            if value:
                send_data[key] = value
        return self._post(
                params={},
                req_path=url,
                data=send_data
        )

    def send_subscribe_msg(self,data):
        url = "https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={}"
        must_key = ("touser", "template_id", "data")
        can_be_null_keys = ("page", "miniprogram_state", "lang")
        send_data = {}
        for key in must_key:
            send_data[key] = data[key]
        for key in can_be_null_keys:
            value = data.get(key)
            if value:
                send_data[key] = value
        return self._post(
            params={},
            req_path=url,
            data=send_data
        )