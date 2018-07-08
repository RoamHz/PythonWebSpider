from requests import Session
from config import *
from db import RedisQueue
from mysql import MySQL
from request import WeixinRequest
from urllib.parse import urlencode
import requests
from pyquery import PyQuery as pq
from requests import ReadTimeout, ConnectionError



class Spider():
    base_url = 'http://weixin.sogou.com/weixin'
    keyword = '世界杯'
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': 'SNUID=ABDB5DA1D1D4A1E78684A865D107AE0F; IPLOC=CN6101; SUID=7A0B8C715F20940A000000005B3D82E1; SUV=1530757856027923; ABTEST=0|1530757927|v1; weixinIndexVisited=1; sct=1; JSESSIONID=aaaEVzTuhjDDbeEJCJgrw; ppinf=5|1530758022|1531967622|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTo5Ok03NzIzMjkxN3xjcnQ6MTA6MTUzMDc1ODAyMnxyZWZuaWNrOjk6TTc3MjMyOTE3fHVzZXJpZDo0NDpvOXQybHVQbHhIcjJGZEh6UWxtWTk2elNSSzdnQHdlaXhpbi5zb2h1LmNvbXw; pprdig=nllAYaYxssp0hiUDLbEvvzmxf01k-Yp_ap-DE9ySNTT_ml1urWFbceFAl3tDw8mIzO-xRANMxd1RyOjH4hBYnHTtdad7i4cMcKCToqIkuNgoVg-v8hRMUAthv-42GI5QRC3QD5j-jVdSJ26-_0xZfS2YrhmYnKXvtpItdZpUI6I; sgid=13-35854231-AVs9g4blTLWoo7vKJzNYu4g; ppmdig=15307580220000006976bdc9e221344757bb35c7bc99b93f',
        'Host': 'weixin.sogou.com',
        'Referer': 'http://weixin.sogou.com/weixin?query=世界杯&_sug_type_=&sut=6402&lkt=4%2C1530757936771%2C1530757943164&s_from=input&_sug_=y&type=2&sst0=1530757943266&page=1&ie=utf8&w=01019900&dr=1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    session = Session()
    queue = RedisQueue()
    mysql = MySQL()

    #获取随机代理
    # PROXY_POOL_URL = 'http://127.0.0.1:5555/random'
    def get_proxy(self):
        try:
            response = requests.get(PROXY_POOL_URL)
            if response.status_code == 200:
                print('Get proxy', response.text)
                return response.text
            return None
        except requests.ConnectionError:
            return None

    def start(self):
        #全局更新Headers
        self.session.headers.update(self.headers)
        start_url = self.base_url + '?' + urlencode({'query': self.keyword, 'type': 2})
        weixin_request = WeixinRequest(url=start_url, callback=self.parse_index, need_proxy=True)
        #调度第一个请求
        self.queue.add(weixin_request)
    
    # from pyquery import Pyquery as pq
    #回调函数,解析索引页
    def parse_index(self, response):
        doc = pq(response.text)
        items = doc('.news-box .news-list li .txt-box h3 a').items()
        #本页所有的链接
        for item in items():
            url = item.attr('href')
            weixin_request = WeixinRequest(url=url, callback=self.parse_detail)
            yield weixin_request
        next = doc('#sogou_next').attr('href')
        #下一页
        if next:
            url = self.base_url + str(next)
            weixin_request = WeixinRequest(url=url, callback=self.parse_index, need_proxy=True)
            yield weixin_request

    #解析详情页
    def parse_detail(self, response):
        doc = pq(response.text)
        data = {
            'title': doc('.rich_media_title').text(),
            'content': doc('.rich_media_content').text(),
            'date': doc('#publish_time').text(),
            'wechat': doc('#js_profile_qrcode > div > p:nth-child(3) > span').text(),
            'nickname': doc('#js_profile_qrcode > div > strong').text()
        }
        yield data

    # from requests import ReadTimeout, ConnectionError
    def request(self, weixin_request):
        try:
            #判断是否需要代理
            if weixin_request.need_proxy:
                #获取代理
                proxy = self.get_proxy()
                if proxy:
                    proxies = {
                        'http': 'http://' + proxy,
                        'https': 'https://' + proxy
                    }
                    #调用Session的send()方法执行请求，请求调用了prepare()方法转化为Prepared Request
                    return self.session.send(weixin_request.prepare(), timeout=weixin_request.timeout, allow_redirects=False, proxies=proxies)
            return self.session.send(weixin_request.prepare(), timeout=weixin_request.timeout, allow_redirects=False)
        except (ConnectionError, ReadTimeout) as e:
            print(e.args)
            return False

    #错误处理
    def error(self, weixin_request):
        weixin_request.fail_time = weixin_request.fail_time + 1
        print('Request Faild', weixin_request.fail_time, 'Times', weixin_request.url)
        if weixin_request.fail_time < MAX_FAILED_TIME:
            self.queue.add(weixin_request)

    #调度请求
    # VALID_STATUES = [200]
    def schedule(self):
        while not self.queue.empty():
            weixin_request = self.queue.pop()
            callback = weixin_request.callback
            print('Schedule', weixin_request.url)
            response = self.request(weixin_request)
            if response and response.status_code in VALID_STATUSES:
                results = list(callback(response))
                if results:
                    for result in results:
                        print('New Result', result)
                        if isinstance(result, WeixinRequest):
                            self.queue.add(result)
                        if isinstance(result, dict):
                            self.mysql.insert('articles', result)
                else:
                    self.error(weixin_request)
            else:
                self.error(weixin_request)

    #入口
    def run(self):
        self.start()
        self.schedule()



if __name__ == '__main__':
    spider = Spider()
    spider.run()
