# coding=utf-8


class MessageMetaClass(type):
    def __new__(cls, name, bases, attrs):
        return super(MessageMetaClass, cls).__new__(cls, name, bases, attrs)


class BaseMessages():
    __metaclass__ = MessageMetaClass

    def __init__(self):
        pass
