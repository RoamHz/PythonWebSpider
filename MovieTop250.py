#encoding=utf-8

from bs4 import BeautifulSoup
import requests

DOWNLOAD_URL = 'https://movie.douban.com/top250'


#def download_page(url):
data = requests.get(DOWNLOAD_URL)
soup = BeautifulSoup(data.text, 'lxml')
titles = soup.select('#content > div > div.article > ol > li:nth-child(1) > div > div.info > div.hd > a > span:nth-child(1)')
print(titles)