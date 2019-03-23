# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urlencode
from images360.items import ImagesItem
import json


class ImagesSpider(scrapy.Spider):
    name = 'images'
    allowed_domains = ['images.so.com']
    start_urls = ['http://images.so.com/']

    def parse(self, response):
        # pass
        result = json.loads(response.text)
        # print(result.get('list'))
        for image in result.get('list'):
            item = ImagesItem()
            item['id'] = image.get('imageid')
            item['url'] = image.get('img_url')
            item['title'] = image.get('group_title')
            item['thumb'] = image.get('img_thumb_url')
            yield item

    def start_requests(self):
        data = {'ch': 'photography', 'listtype': 'new'}
        base_url = 'https://image.so.com/zj?'
        for page in range(1, self.settings.get('MAX_PAGE') + 1):
            data['sn'] = page * 30
            params = urlencode(data)
            url = base_url + params
            yield scrapy.Request(url, self.parse)