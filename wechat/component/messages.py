# coding=utf-8

from wechat.messages.fields import StringField, DateTimeField, IntField
from wechat.messages.message import MessageMetaClass

COMPONENT_MESSAGE_TYPE = {}


def register_message(msg_type):
    def register(cls):
        COMPONENT_MESSAGE_TYPE[msg_type] = cls
    return register


class BaseComponentMessage(object):

    __metaclass__ = MessageMetaClass
    type = 'unknown'
    appid = StringField("AppId")
    create_time = DateTimeField("CreateTime")

    def __init__(self, message):
        self._data = message

    def __repr__(self):
        _repr = "{klass}({msg})".format(
            klass=self.__class__.__name__,
            msg=self._data
            )
        return _repr


@register_message("component_verify_ticket")
class ComponentVerifyTicketMessage(BaseComponentMessage):
    type = 'component_verify_ticket'
    verify_ticket = StringField("ComponentVerifyTicket")


@register_message("authorized")
class ComponentAuthorizedMessage(BaseComponentMessage):
    type = 'authorized'
    authorized_code = StringField("AuthorizationCode")
    authorized_appid = StringField("AuthorizerAppid")
    authorized_code_expire = IntField("AuthorizationCodeExpiredTime")
    pre_auth_code = StringField("PreAuthCode")


@register_message("unauthorized")
class ComponentUnauthorizedMessage(BaseComponentMessage):
    type = 'unauthorized'
    unauthorized_appid = StringField("AuthorizerAppid")


@register_message("updateauthorized")
class ComponentUpdateauthMessage(BaseComponentMessage):
    type = 'updateauthorized'
    update_appid = StringField("AuthorizerAppid")
    authorized_code = StringField("AuthorizationCode")
    authorized_code_expire = StringField("AuthorizationCodeExpiredTime")
    pre_auth_code = StringField("PreAuthCode")


class ComponentUnknownMessage(BaseComponentMessage):
    type = 'unknown'
