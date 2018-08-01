#encoding=utf-8

import requests
from lxml import etree
from bs4 import BeautifulSoup


class Login(object):
    def __init__(self):
        self.headers = {
            'Referer': 'https://github.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Host': 'github.com'
        }
        self.login_url = 'https://github.com/login'
        self.post_url = 'https://github.com/session'
        self.logined_url = 'https://github.com/settings/profile'
        self.session = requests.Session()
    
    def token(self):
        response = self.session.get(self.login_url, headers=self.headers)
        selector = etree.HTML(response.text)
        token = selector.xpath('//div//input[2]/@value')
        return token
    
    def login(self, email, password):
        post_data = {
            'commit': 'Sign in',
            'utf8': '✓',
            'authenticity_token': self.token(),
            'login': email,
            'password': password
        }
        response = self.session.post(self.post_url, data=post_data, headers=self.headers)
        if response.status_code == 200:
            # test = etree.HTML(response.text)
            # print(test)
            # soup = BeautifulSoup(response.text, "lxml")
            self.dynamics(response.text)
        
        response = self.session.get(self.logined_url, headers=self.headers)
        if response.status_code == 200:
            self.profile(response.text)

    def dynamics(self, html):
        # selector = etree.HTML(html)
        # print(html)
        # dynamics = html.xpath('//div[contains(@class, "news")]//div[contains(@class, "alert")]')
        soup = BeautifulSoup(html, 'lxml')
        print(soup)
        dynamics = soup.find('div', attrs={'id': 'user-repositories-list'})
        for item in dynamics.findall('h3'):
            print(item)
        # for item in dynamics:
        #     dynamic = ' '.join(item.xpath('.//div[@class="title"]//text()')).strip()
        #     print(dynamic)
    
    def profile(self, html):
        selector = etree.HTML(html)
        name = selector.xpath('//input[@id="user_profile_name"]/@value')[0]
        email = selector.xpath('//select[@id="user_profile_email"]/option[@value!=""]/text()')
        print(name, email)


if __name__ == "__main__":
    githublogin = Login()
    githublogin.login(email='test@qq.com', password='password')
