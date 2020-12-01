# coding=utf-8
'''
constant
'''

import logging
from enum import Enum


# LOGFORMATTER = '%(levelname)s %(asctime)s %(process)d '\
#         '[%(filename)s:%(lineno)d] %(funcName)s %(message)s'
# logging.basicConfig(
#     level=logging.DEBUG,
#     format=LOGFORMATTER)
LOG = logging.getLogger(__name__)


class WeChatErrorCode(Enum):
    '''
    微信接口返回码
    '''
    SYSTEM_ERROR = -1000
    SYSTEM_BUSY = -1
    SUCCESS = 0
    INVALID_CREDENTIAL = 40001
    INVALID_CREDENTIAL_TYPE = 40002
    INVALID_ACCESS_TOKEN = 40014
    EXPIRED_ACCESS_TOKEN = 42001
