### 微信平台接口封装

主要封装了微信公众号/小程序的接口，经常使用的接口，部分可能没有增加，需要者可自行 添加

欢迎讨论 封装更易用

wechat: shiguofu039002

### How to use

```python
# 创建微信接口调用客户端
# appid/appsec为微信公众号/小程序的appid/appsec
# session 可选；为缓存token，需满足
# 1. 支持set(key, val, expire) 操作 设置token缓存
# 2. 支持get(key) string 操作获取token
# session 不传，则默认连接(localhost:6379
# 代码路径 (wechat/api/__init__.py)
client = WechatClient(APPID, APPSEC, session=session)
```

#### user相关操作

```python
# 根据openid获取用户信息（关注公众号）
userinfo = client.user.get(openid)
# 关注公众号列表
users = client.user.user_list(<next_openid>)
```

#### 二维码相关

```
client.qrcode.create({'action_name': 'QR_LIMIT_STR_SCENE', "action_info": {'scene': {'scene_str': 'card'}}})
```

#### 菜单相关

```python
client.menu.create(MENU_DAT)   # MENU_DAT为菜单全量数据
```

#### 素材相关

```python
client.material.get_material_list("news", 1, 5)  # 获取素材列表
```

#### 二维码认证相关

```python
client.oauth.refresh_user_access_token()
```

#### 消息发送

```python
data = {
            'touser': openid,
            'msgtype': 'mpnews',
            'mpnews': {'media_id': media_id}
       }
res = client.kefu_msg.send(data)
```

#### 消息推送(明文)

```python
data = "<xml><ToUserName><![CDATA[toUser]]></ToUserName><FromUserName><![CDATA[fromUser]]></FromUserName><CreateTime>1348831860</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[this is a test]]></Content><MsgId>1234567890123456</MsgId></xml>"
dict_data = xmltodict.parse(data)['xml']
text_msg = TextMessage(dict_data)       # 转换为message 对象,text_msg.ToUserName
print isinstance(text_msg, BaseMessage)
tr = TextReply(message=text_msg, content="test")
print tr  # reply message 直接return即可
```

#### 消息推送(加密)

```python
crypt = WechatCrypto('kfweiyou', 'qrzna45zzztzdm5px9vav9chrnjan66epn1iwcc6sgr', 'wx90b56449bc67ccc2')
msg = '<xml>\x0A    <ToUserName><![CDATA[gh_7289026be5e3]]></ToUserName>\x0A    <Encrypt><![CDATA[vLXs6z+aU+E4NMHs6Sbhlx28J2ZxXxXx09wCD0iMSM3sp+t8ADzruxi3xUaO9st6Y3o/039Cz1oTEQYW8RWszcOUIOV87rcNUcQJjOVriMAH+Zvrp5axdrLRgNsky1v82++lEkOIZPQaZKMBzdfowBsZDbTic3FhrVA2//Y4irjhCvwcmq2U9e9h4GZj+1qvAJiDLKwR/0uFYv+L+jyzFY3n41ftnf/mtQlJ56jqPRuYNKZAGx/tgMkrGyLzCasqqSzpnSSPoMopd1zW0O7r+2ozeD0nf09xqP/VYEoutt1xhSkaci8FKbUBquVBbT8nfA6/koafRn9D5ff65JM+YZia6CWfwKT2rxUdtvkGuSyBDGaBiLcgKiPoLG5J9C0PP059LCaArD66Q+tAlozeeYwbJQn3fk/OpOk3S8RF4Adg82WeXzBJDdJk8eJLTJI44ZHGaDSukCUc6KsmrWsOqg==]]></Encrypt>\x0A</xml>\x0A'
sig = '785947fdf0093a20d6f81848237179a04ab1d042'
timestamp = '1533088428'
nonce = '855436957'
print crypt.decrypt_message(msg, sig, timestamp, nonce)
```

#### 小程序数据解密

```python
iv = 'NH0JFobAiK5k5bPgVVNIfA=='
key = 'hOLOQF28PGbQEJB6geNbRA=='
encrypted = '22gV3dRumMrAEmzC03ccozS8DATCDRYSSSku/MEJAjT3wWS0F+NQ0JEDvXbzD3ZFgvSI43UQlmI1mQ7RvnIZqrbUXw8z5kjEsuhnXqdLzuNjxNEfj1hqoosZiVipFHlYHmMt8KjOXmVpfkaRMhfrVg=='
from wechat.crypto.base import WeappCrypto
crypt = WeappCrypto(key, iv)
print crypt.decrypt(encrypted)
```

