# coding=utf-8
'''
wechat user get API
'''
import json
from wechat.api.base import BaseWechatAPI


class WechatMaterial(BaseWechatAPI):

    def add_forever(self, _type, filepath):
        '''add forever material'''
        fileobject = open(filepath, 'rb')
        file_name = filepath.split("/")[-1]
        if _type == 'video':
            post_data = {
                    "media": ("file.mp4", fileobject.read(), "application/octet-stream")}
            desc = {"title": file_name, 'introduction': file_name}
            post_data.update(
                    {"description": (None, json.dumps(desc, ensure_ascii=False))})
        else:
            post_data = {"media": fileobject}
        return self._post(
            req_path='material/add_material',
            params={"type": _type},
            files=post_data)

    def add_news_forever(self, article_list):
        '''
        article should contains:
            title --- article title
            thumb_media_id --- thumb image media_id
            show_cover_pic ---
            content ---
            content_source_url

            need_open_comment
            only_fans_can_comment
            author --- author
            digest --- description
        '''
        data = {'articles': article_list}
        return self._post('material/add_news', data=data)

    def add_news_thumb(self, filepath):
        file_object = open(filepath, 'rb')
        return self._post(
                req_path="media/uploadimg",
                files={'media': file_object})

    def get_forever(self, media_id):
        '''get forever material by media_id'''
        return self._post('material/get_material', data={'media_id': media_id})

    def get_material_list(self, _type, page=1, count=20):
        offset = (page - 1) * count
        data = {'type': _type, 'offset': offset, 'count': count}
        return self._post('material/batchget_material', data=data)

    def del_forever_material(self, media_id):
        return self._post(
            req_path='material/del_material',
            data={'media_id': media_id}
            )

    def add_temp_material(self, _type, filepath):
        fileobject = open(filepath, "rb")
        return self._post(
            req_path='media/upload',
            params={'type': _type},
            files={"media": fileobject})

    def get_temp_material(self, media_id):
        return self._get(
            req_path='media/get',
            params={'media_id': media_id}
            )
