# coding=utf-8
'''
push message fields type
'''

import copy
from datetime import datetime
from wechat.utils import ObjectDict


class FieldDescriptor(object):
    '''
    field descriptor for pushed message field
    '''
    def __init__(self, field):
        self.field = field
        self.attr_name = field.name

    def __get__(self, instance, instance_type=None):
        if instance is not None:
            value = instance._data.get(self.attr_name)
            if value is None:
                value = copy.deepcopy(self.field.default)
                instance._data[self.attr_name] = value
            if isinstance(value, dict):
                value = ObjectDict(value)
            if value and not isinstance(value, (dict, list, tuple)) and \
                    callable(self.field.converter):
                value = self.field.converter(value)
            return value
        return self.field

    def __set__(self, instance, value):
        instance._data[self.attr_name] = value


class BaseField(object):
    '''
    the wechat push message field base class
    '''
    converter = None

    def __init__(self, name, default=None):
        self.name = name
        self.default = default

    def to_xml(self, value):
        '''
        convert original message to wechat xml data this field
        @params
        value    ---  the value to be convert
        '''
        raise NotImplementedError

    def __repr__(self):
        _repr = "{klass}({name})".format(
            klass=self.__class__.__name__,
            name=repr(self.name)
            )
        return _repr

    def add_to_class(self, klass, name):
        '''
        add fieldDescriptor to message class
        '''
        self.klass = klass
        klass._fields[name] = self
        setattr(klass, name, FieldDescriptor(self))


class StringField(BaseField):
    '''
    string field
    '''

    def __to_text(self, value):
        if isinstance(value, unicode):
            value = value.encode("utf-8")
        return value

    converter = __to_text

    def to_xml(self, value):
        value = self.converter(value)
        tpl = '<{name}><![CDATA[{value}]]></{name}>'
        return tpl.format(name=self.name, value=value)


class IntField(BaseField):
    '''
    integer type
    '''
    converter = int

    def to_xml(self, value):
        value = self.converter(value) if value is not None else self.default
        tpl = "<{name}>{value}</{name}>"
        return tpl.format(name=self.name, value=value)


class DateTimeField(BaseField):
    '''
    datetime field
    '''

    def __converter(self, value):
        value = int(value)
        return datetime.fromtimestamp(value)

    converter = __converter

    def to_xml(self, value):
        value = self.converter(value) if value is not None else self.default
        tpl = "<{name}>{value}</{name}>"
        return tpl.format(name=self.name, value=value)


class ImageField(StringField):
    '''
    image push data fields
    '''

    def to_xml(self, value):
        tpl = "<Image><MediaId><![CDATA[{value}]]></MediaId></Image>"
        return tpl.format(value=value)


class VoiceField(StringField):
    '''voice push data field'''
    def to_xml(self, value):
        tpl = "<Voice><MediaId><![CDATA][{value}]></MediaId></Voice>"
        return tpl.format(value=value)


class VideoField(StringField):
    '''video push data field'''
    def to_xml(self, value):
        media = self.converter(value['media_id'])
        if 'title' in value:
            title = value['title']
        if 'description' in value:
            description = self.converter(value['description'])
        tpl = "<Video>\n\
            <MediaId><![CDATA[{media_id}]]></MediaId>\n\
            <Title><![CDATA[{title}]]></Title>\n\
            <Description><![CDATA[{description}]]></Description>\n\</Video>"
        return tpl.format(media_id=media, title=title, description=description)


class MusicField(StringField):
    '''music push data field'''
    def to_xml(self, value):
        media = self.converter(value['media_id'])
        if 'title' in value:
            title = value['title']
        if 'description' in value:
            description = value['description']
        if 'music_url' in value:
            music_url = value['music_url']
        if 'hq_music_url' in value:
            hq_music_url = value['hq_music_url']
        tpl = """<Music>
        <ThumbMediaId><![CDATA[{thumb_media_id}]]></ThumbMediaId>
        <Title><![CDATA[{title}]]></Title>
        <Description><![CDATA[{description}]]></Description>
        <MusicUrl><![CDATA[{music_url}]]></MusicUrl>
        <HQMusicUrl><![CDATA[{hq_music_url}]]></HQMusicUrl>
        </Music>"""
        return tpl.format(
            thumb_media_id=media,
            title=title,
            description=description,
            music_url=music_url,
            hq_music_url=hq_music_url)


class ArticlesField(StringField):
    '''article push data field'''
    def to_xml(self, value):
        items = []
        for item in value:
            title = self.converter(item.get("title", ""))
            description = self.converter(item.get("description", ''))
            image = self.converter(item.get("image", ''))
            url = self.converter(item.get("url", ''))
            item_tpl = """<item>
            <Title><!CDATA[{title}]></Title>
            <Description><![CDATA[{description}]]></Description>
            <PicUrl><!CDATA[{image}]></PicUrl>
            <Url><!CDATA[{url}]></Url></item>"""
            item = item_tpl.format(
                title=title,
                description=description,
                image=image,
                url=url)
            items.append(item)
        items_str = '\n'.join(items)
        tpl = """<ArticleCount>{article_count}</ArticleCount>
        <Articles>{articles}</Articles>"""
        return tpl.format(article_count=len(items), articles=items_str)
