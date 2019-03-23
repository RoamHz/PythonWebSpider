# -*- coding: utf-8 -*-
import scrapy
from tutorial.items import QuoteItem


class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        # pass
        quotes = response.css('.quote')
        for quote in quotes:
            item = QuoteItem()
            item['text'] = quote.css('.text::text').extract_first()
            item['author'] = quote.css('.author::text').extract_first()
            item['tags'] = quote.css('.tags .tag::text').extract()
            yield item
        _next = response.css('.page .next a::attr(href)').extract_first()
        url = response.urljoin(_next)
        yield scrapy.Request(url=url, callback=self.parse)
