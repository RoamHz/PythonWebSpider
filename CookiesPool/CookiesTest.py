import random
import redis


#存储模块
class RedisClient(object):
    def __init__(self, type, website, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        '''
        初始化Redis连接
        '''
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)
        self.type = type
        self.website = website

    def name(self):
        '''
        获取Hash的名称
        '''
        return "{type}: {website}".format(type=self.type, website=self.website)

    def set(self, username, value):
        '''
        设置键值对
        '''
        return self.db.hset(self.name(), username, value)

    def get(self, username):
        '''
        根据键名获取键值
        '''
        return self.db.hget(self.name(), username)

    def delete(self, username):
        '''
        根据键名删除键值对
        '''
        return self.db.hdel(self.name(), username)
    
    def count(self):
        '''
        获取数目
        '''
        return self.db.hlen(self.name())

    def random(self):
        '''
        随机得到键值， 用于随机Cookies获取
        '''
        return random.choice(self.db.hvals(self.name()))

    def usernames(self):
        return self.db.hkeys(self.name())

    def all(self):
        '''
        获取所有键值对
        '''
        return self.db.hgetall(self.name())


#生成模块
for username in accounts_usernames:
    if not username in cookies_usernames:
        password = self.accounts_db.get(username)
        print('正在生成Cookies', '账号', username, '密码'， password)
        result = self.new_cookies(username, password)

def get_cookies(self):
    return self.browser.get_cookies()

def main(self):
    self.open()
    if self.password_error():
        return {
            'status': 2,
            'content': '用户名或密码错误'
        }
    # 如果不需要验证码直接登录成功
    if self.login_successfully():
        cookies = self.get_cookies()
        return {
            'status': 1,
            'content': cookies
        }
    # 获取验证码图片
    image = self.get_image('captcha.png')
    numbers = self.detect_image(image)
    self.move(numbers)
    if self.login_successfully():
        cookies = self.get_cookies()
        return {
            'status': 1,
            'content': cookies
        }
    else:
        return {
            'status': 3,
            'content': '登录失败'
        }

result = self.new_cookies(username, password)
# 成功登录
if result.get('status') == 1:
    cookies = self.process_cookies(result.get('content'))
    print('成功获取Cookies', cookies)
    if self.cookies_db.set(username, json.dumps(cookies)):
        print('成功保存Cookies')
# 密码错误，移除账号
elif result.get('status') == 2:
    print(result.get('content'))
    if self.accounts_db.delete(username):
        print('成功删除账号')
else:
    print(result.get('content'))


# 检测模块