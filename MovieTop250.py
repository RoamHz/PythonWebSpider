#encoding=utf-8

from bs4 import BeautifulSoup
import requests

DOWNLOAD_URL = 'https://movie.douban.com/top250'


def download_page(url):
    data = requests.get(url).content
    return data

def parse_html(html):
    soup = BeautifulSoup(html, 'lxml')
    movie_list = soup.find('ol', attrs={'class': 'grid_view'})
    movie_name_list = []

    for movie_li in movie_list.find_all('li'):
        detail = movie_li.find('div', attrs={'class': 'hd'})
        movie_name = detail.find('span', attrs={'class': 'title'}).getText()
        movie_name_list.append(movie_name)

    next_page = soup.find('span', attrs={'class': 'next'}).find('a')
    if next_page:
        return movie_name_list, DOWNLOAD_URL+next_page['href']
    return movie_name_list, None

if __name__ == '__main__':
    url = DOWNLOAD_URL
    while url:
        html = download_page(url)
        movies, url = parse_html(html)
        print(movies)