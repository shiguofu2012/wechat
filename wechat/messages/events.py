# coding=utf-8

from wechat.messages.message import BaseMessage, MessageMetaClass
from wechat.messages.fields import StringField

EVENTS_TYPE = {}


def register_event(event_type):
    def register(cls):
        EVENTS_TYPE[event_type] = cls
    return register


class BaseEvent(BaseMessage):
    """base class for all events"""
    __metaclass__ = MessageMetaClass
    type = 'event'
    event = ''


@register_event("subscribe")
class SubscribeEvent(BaseEvent):
    """user subscribe event"""
    __metaclass__ = MessageMetaClass
    event = 'subscribe'
    key = StringField("EventKey", "")
    ticket = StringField("Ticket", "")


@register_event("unsubscribe")
class UnsubscribeEvent(BaseEvent):
    """user unsubscribe event"""
    __metaclass__ = MessageMetaClass
    event = 'unsubscribe'


@register_event("scan")
class ScanEvent(BaseEvent):
    """use scan event"""
    __metaclass__ = MessageMetaClass
    event = 'scan'
    scene_id = StringField("EventKey")
    ticket = StringField("Ticket")


@register_event("click")
class ClickEvent(BaseEvent):
    """user define type"""
    __metaclass__ = MessageMetaClass
    event = 'click'
    key = StringField("EventKey")
