# -*- coding: utf-8 -*-
import scrapy


class ElemeSpider(scrapy.Spider):
    name = 'eleme'
    allowed_domains = ['ele.me']
    start_urls = ['http://ele.me/']

    def parse(self, response):
        pass
