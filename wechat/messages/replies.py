# coding=utf-8
'''
reply message
'''

import logging
import time
from wechat.messages.fields import StringField, IntField, ImageField, \
        VoiceField, VideoField, MusicField, ArticlesField
from wechat.messages.message import MessageMetaClass

LOG = logging.getLogger(__name__)


class BaseReply(object):
    '''base class for all replymessage'''
    __metaclass__ = MessageMetaClass
    source = StringField("FromUserName")
    target = StringField("ToUserName")
    timestamp = IntField("CreateTime", time.time())
    type = 'unknown'

    def __init__(self, **kwargs):
        self._data = {}
        message = kwargs.pop("message", None)
        if message:
            if 'source' not in kwargs:
                kwargs['source'] = message.target
            if 'target' not in kwargs:
                kwargs['target'] = message.source
        if 'timestamp' not in kwargs:
            kwargs['timestamp'] = time.time()
        for name, value in kwargs.items():
            field = self._fields.get(name)
            if field:
                self._data[field.name] = value
            else:
                setattr(self, name, value)

    def render(self):
        '''render to xml data'''
        tpl = '<xml>\n{data}\n</xml>'
        nodes = []
        msg_type = '<MsgType><![CDATA[{msg_type}]]></MsgType>'.format(
            msg_type=self.type
            )
        nodes.append(msg_type)
        for name, field in self._fields.items():
            value = getattr(self, name, field.default)
            node_xml = field.to_xml(value)
            nodes.append(node_xml)
        data = '\n'.join(nodes)
        return tpl.format(data=data)

    def __str__(self):
        return self.render()


class EmptyReply(BaseReply):
    '''reply nothing passive'''

    __metaclass__ = MessageMetaClass

    def render(self):
        return ''


class TextReply(BaseReply):
    '''reply text message passive'''
    __metaclass__ = MessageMetaClass
    type = 'text'
    content = StringField("Content")


class ImageReply(BaseReply):
    '''reply image message passive'''
    type = 'image'
    image = ImageField("Image")

    @property
    def media_id(self):
        '''image media id'''
        return self.image

    @media_id.setter
    def media_id(self, value):
        self.image = value


class VoiceReply(BaseReply):
    '''reply voice message passive'''
    type = 'voice'
    voice = VoiceField("Voice")

    @property
    def media_id(self):
        '''voice media id'''
        return self.voice

    @media_id.setter
    def media_id(self, value):
        self.voice = value


class VideoReply(BaseReply):
    '''reply video message passive'''
    type = 'video'
    video = VideoField("Video", {})

    @property
    def media_id(self):
        '''video media id'''
        return self.video.get("media_id")

    @media_id.setter
    def media_id(self, value):
        video = self.video
        video['media_id'] = value
        self.video = video

    @property
    def title(self):
        '''video title'''
        return self.video.get("title")

    @title.setter
    def title(self, value):
        video = self.video
        video['title'] = value
        self.video = video

    @property
    def description(self):
        '''video description'''
        return self.video.get("description")

    @description.setter
    def description(self, value):
        video = self.video
        video['description'] = value
        self.video = video


class MusicReply(BaseReply):
    '''reply music message pssive'''
    type = 'music'
    music = MusicField("Music", {})

    @property
    def thumb_media_id(self):
        '''music thumb pic media id'''
        return self.music.get("media_id")

    @thumb_media_id.setter
    def thumb_media_id(self, value):
        music = self.music
        music['media_id'] = value
        self.music = music

    @property
    def title(self):
        '''music title'''
        return self.music.get("title")

    @title.setter
    def title(self, value):
        music = self.music
        music['title'] = value
        self.music = music

    @property
    def description(self):
        '''music description'''
        return self.music.get("description")

    @description.setter
    def descritpion(self, value):
        music = self.music
        music['description'] = value
        self.music = music

    @property
    def music_url(self):
        '''music url'''
        return self.music.get("music_url")

    @music_url.setter
    def music_url(self, value):
        music = self.music
        music['music_url'] = value
        self.music = music

    @property
    def hq_music_url(self):
        '''high quility music url'''
        return self.music.get("hq_music_url")

    @hq_music_url.setter
    def hq_music_url(self, value):
        music = self.music
        music['hq_music_url'] = value
        self.music = music


class ArticlesReply(BaseReply):
    '''reply news message'''
    type = 'news'
    articles = ArticlesField('Articles', [])

    def add_article(self, article):
        '''add article'''
        articles = self.articles
        articles.append(article)
        self.articles = articles
