# -*- coding: utf-8 -*-
import _env  # noqa
import scrapy
import json

from data.models.eleme import ElemeAreaInfo, ElemeRestaurant


class ElemeSpider(scrapy.Spider):
    name = 'eleme'

    allowed_domains = ['ele.me']
    # 测试样例 以杭州 '中学' '医院' 为关键字
    test_pos = ['医院', '大厦', '中心', '小区', '超市', '广场']
    base_url = 'https://www.ele.me/restapi/v2/pois?extras%5B%5D=count&geohash=wtmknpnr9yy3&keyword={pos}&limit=20&type=nearby'
    start_urls = ['https://www.ele.me/restapi/v2/pois?extras%5B%5D=count&geohash=wtmknpnr9yy3&keyword=中学&limit=20&type=nearby']

    def parse(self, response):
        if response.status == 200:
            # 当返回
            res = json.loads(response.body, encoding='utf-8')

            if res:
                for o in res:
                    del o['id'], o['request_id']
                    ElemeAreaInfo(o).upsert(dict(
                        latitude=o['latitude'],
                        longitude=o['longitude']
                    ))
                    page_num = o['count'] // 24 if o['count'] % 24 == 0 else (o['count'] // 24 + 1)
                    for page in xrange(page_num):

                        res_list_url = 'https://www.ele.me/restapi/shopping/restaurants?extras%5B%5D=activities&geohash={geohash}&latitude={lad}&limit=24&longitude={lgd}&offset={page}&terminal=web'.format(geohash=o['geohash'], lad=o['latitude'], lgd=o['longitude'], page=page * 24)
                        yield scrapy.Request(res_list_url, callback=self.parse_rest_link)

        for pos in self.test_pos:
            pos_url = self.base_url.format(pos=pos)
            yield scrapy.Request(pos_url, callback=self.parse)

    def parse_rest_link(self, response):
        '''
            解析具体某个地址的所有商户链接
        '''
        res = json.loads(response.body, encoding='utf-8')
        for o in res:
            url = 'https://www.ele.me/restapi/shopping/restaurant/{}?extras%5B%5D=activities&extras%5B%5D=license&extras%5B%5D=identification&extras%5B%5D=albums&extras%5B%5D=flavors'.format(o['id'])
            yield scrapy.Request(url, callback=self.parse_rest_detail)

    def parse_rest_detail(self, response):
        '''
            解析商户详细信息
        '''
        res = json.loads(response.body, encoding='utf-8')

        ElemeRestaurant(dict(
            res_id=res['id'],
            origin=u'eleme',
            city=u'杭州',
            name=res['name'],
            categroy=[o['name'] for o in res['flavors']],
            address=res['address'],
            phone_num=res['phone'],
            open_time=res['opening_hours'],
            rating=res['rating'],
            rating_count=res['rating_count'],
            order_num=res['recent_order_num'],
            latitude=res['latitude'],
            longitude=res['longitude'],
            activity=res['activities']
        )).upsert({'res_id': res['id']})
