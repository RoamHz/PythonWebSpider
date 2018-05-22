#encoding=utf-8

from bs4 import BeautifulSoup
import requests
import codecs

DOWNLOAD_URL = 'https://movie.douban.com/top250'


def download_page(url):
    data = requests.get(url).content
    return data

def parse_html(html):
    soup = BeautifulSoup(html, 'lxml')
    movie_list = soup.find('ol', attrs={'class': 'grid_view'})
    movie_name_list = []
    rating_list = []

    for movie_li in movie_list.find_all('li'):
        detail = movie_li.find('div', attrs={'class': 'hd'})
        rating_detail = movie_li.find('div', attrs={'class': 'star'})
        movie_name = detail.find('span', attrs={'class': 'title'}).getText()
        ratings = rating_detail.find('span', attrs={'class': 'rating_num'}).getText()
        movie_name_list.append(movie_name)
        rating_list.append(ratings)

    next_page = soup.find('span', attrs={'class': 'next'}).find('a')
    if next_page:
        return movie_name_list, rating_list, DOWNLOAD_URL+next_page['href']
    return movie_name_list, rating_list, None

if __name__ == '__main__':
    url = DOWNLOAD_URL
    with codecs.open('movies', 'wb', encoding='utf-8') as fp:
        while url:
            html = download_page(url)
            movies, ratings, url = parse_html(html)
            zipped = zip(movies, ratings)
            m_r = []
            for i in zipped:
                m_r.append(i)
            # print(m_r)
            for item in m_r:
                fp.write(u'{0[0]}  {0[1]}\n'.format(item))
                # print("")
