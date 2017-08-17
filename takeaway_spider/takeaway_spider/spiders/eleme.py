# -*- coding: utf-8 -*-
import scrapy


class ElemeSpider(scrapy.Spider):
    name = 'eleme'

    def start_request(self):
        allowed_domains = ['ele.me']
        start_urls = ['https://www.ele.me/home/']

    def parse(self, response):
        if response.status == 200:
            # 当返回
            pass
