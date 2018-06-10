import os
import requests
from urllib.parse import urlencode
from hashlib import md5
from multiprocessing.pool import Pool

GROUP_START = 1
GROUP_END = 2


def get_page(offset):
	#查看XHR中AJAX请求，找到请求头部，下拉观察请求的区别
	params = {
		'offset': offset,
		'format': 'json',
		'keyword': '街拍',
		'autoload': 'true',
		'count': '20',
		'cur_tab': '1',
		'from': 'search_tab'
	}
	#urlencode将params格式化为对应url
	url = 'https://www.toutiao.com/search_content/?' + urlencode(params)
	try:
		response = requests.get(url)
		if response.status_code == 200:
			return response.json()
	except requests.ConnectionError:
		return None

def get_images(json):
	#根据Preview查看对应的响应结构
	if json.get('data'):
		for item in json.get('data'):
			title = item.get('title')
			images = item.get('image_list')
			if images:
				for image in images:
					yield {
						'image': image.get('url'),
						'title': title
					}

def save_image(item):
	if not os.path.exists(item.get('title')):
		os.mkdir(item.get('title'))
	try:
		#得到大图的url，通过点击任意图片查看图片的区别发现只有一个字段不一样
		image_url = item.get('image').replace('list', 'origin')
		#得到合法的图片url，使用requests请求
		response = requests.get('http:' + image_url)
		if response.status_code == 200:
			#格式化存储，MD5查重
			file_path = '{0}/{1}.{2}'.format(item.get('title'), md5(response.content).hexdigest(), 'jpg')
			if not os.path.exists(file_path):
				with open(file_path, 'wb') as f:
					f.write(response.content)
			else:
				print('Already Downloaded', file_path)
	except requests.ConnectionError:
		print('Failed to Save Image')

def main(offset):
	json = get_page(offset)
	for item in get_images(json):
		print(item)
		save_image(item)


if __name__ == '__main__':
	#多进程爬取
	pool = Pool()
	groups = ([ x*20 for x in range(GROUP_START, GROUP_END+1) ])
	#map函数将偏移量传给main
	pool.map(main, groups)
	pool.close()
	pool.join