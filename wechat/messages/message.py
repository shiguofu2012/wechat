# coding=utf-8
'''
wechat push message format
'''
import copy
from wechat.messages.fields import BaseField, IntField, StringField, \
        DateTimeField, FieldDescriptor
# from wechat.constants import LOG

MESSAGE_TYPES = {}


def register_mesage(msg_type):
    '''register message type decorator'''
    def register(cls):
        '''register'''
        MESSAGE_TYPES[msg_type] = cls
        return cls
    return register


class MessageMetaClass(type):
    '''
    meta class for message type
    '''
    def __new__(mcs, name, bases, attrs):
        for base in bases:
            if not hasattr(base, '_fields'):
                continue

            for key, value in base.__dict__.items():
                if key in attrs:
                    continue
                if isinstance(value, FieldDescriptor):
                    attrs[key] = copy.deepcopy(value.field)

        mcs = super(MessageMetaClass, mcs).__new__(mcs, name, bases, attrs)
        mcs._fields = {}

        for name, field in mcs.__dict__.items():
            if isinstance(field, BaseField):
                field.add_to_class(mcs, name)
        return mcs


class BaseMessage(object):
    '''
    message base class
    '''
    __metaclass__ = MessageMetaClass

    type = 'unknown'
    _id = IntField("MsgId", 0)
    source = StringField("FromUserName")
    target = StringField("ToUserName")
    create_time = DateTimeField("CreateTime")
    timestamp = IntField("CreateTime")

    def __init__(self, message):
        self._data = message

    def __repr__(self):
        _repr = "{klass}({msg})".format(
            klass=self.__class__.__name__,
            msg=repr(self._data)
            )
        return _repr

    def __str__(self):
        return self.__repr__()


@register_mesage('text')
class TextMessage(BaseMessage):
    """receive wechat server push text message"""
    type = 'text'
    content = StringField("Content")


@register_mesage("image")
class ImageMessage(BaseMessage):
    """receieve wechat server pushed image message"""
    __metaclass__ = MessageMetaClass
    type = 'image'
    media_id = StringField("MediaId")
    image = StringField("PicUrl")


@register_mesage("voice")
class VoiceMessage(BaseMessage):
    """receieve wechat server pushed voice message"""
    __metaclass__ = MessageMetaClass
    type = 'voice'
    media_id = StringField("MediaId")
    format = StringField("Format")
    recognition = StringField("Recognition")


@register_mesage("video")
class VideoMessage(BaseMessage):
    """recieve wechat server pushed video message"""
    __metaclass__ = MessageMetaClass
    type = 'video'
    media_id = StringField("MediaId")
    thumb_media_id = StringField("ThumbMediaId")


@register_mesage("shortvideo")
class ShortVideoMessage(BaseMessage):
    """recieve wechat server pushed shortvideo message"""
    __metaclass__ = MessageMetaClass
    type = 'video'
    media_id = StringField("MediaId")
    thumb_media_id = StringField("ThumbMediaId")


@register_mesage("link")
class LinkMessage(BaseMessage):
    """recieve wechat server pushed link message"""
    __metaclass__ = MessageMetaClass
    type = 'link'
    title = StringField("Title")
    description = StringField("Description")
    url = StringField("Url")


@register_mesage("event")
class EventMessage(BaseMessage):
    """recieve wechat server pushed event message"""
    __metaclass__ = MessageMetaClass
    type = 'event'
    event = StringField("Event")
    event_key = StringField("EventKey")


class UnknownMessage(BaseMessage):
    """unknown type mesasge"""
    pass
