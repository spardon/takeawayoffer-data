#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    饿了么 Model
'''
from base import MongoDoc


class ElemeRestaurant(MongoDoc):
    '''
        饿了么商户ID及地区
    '''

    __collection__ = 'eleme_restaurant'

    structure = dict(
        res_id=basestring,  # 商户id
        origin=basestring,  # 商户来源，默认为 eleme
        city=basestring,  # 商户所属城市
        name=basestring,  # 商户名称
        categroy=list,  # 所属分类，可能有多个
        address=basestring,  # 商户地址
        phone_num=basestring,  # 电话 可能有多个
        open_time=list,  # 营业时间 多段营业的情况
        rating=float,  # 评分
        rating_count=int,  # 评价总数
        order_num=int,  # 最近订单数量
        latitude=float,  # 纬度
        longitude=float,  # 经度
        activity=list,  # 活动
    )

    indexs = [
        {'field': 'res_id'},
        {'field': 'city'},
        {'field': 'name'},
        {'field': 'rating'},
    ]


class ElemeAreaInfo(MongoDoc):
    '''
        饿了么相关定位信息
        id: "10897473655955349371",
        name: "杭州绿城育华学校",
        address: "浙江省杭州市西湖区紫金港路杭州绿城育华学校旁",
        short_address: "紫金港路杭州绿城育华学校旁",
        latitude: 30.28947,
        longitude: 120.08537,
        city: "杭州市",
        request_id: "3545425242943446650",
        city_id: 2,
        geohash: "wtmkkd52zym",
        count: 2151
    '''
    __collection__ = 'eleme_area_info'

    structure = dict(
        name=basestring,
        address=basestring,
        short_address=basestring,
        latitude=float,
        longitude=float,
        city=basestring,
        city_id=int,
        geohash=basestring,
        count=int  # 附近商户数
    )

    indexs = [
        {'field': 'name'},
        {'field': 'geohash'}
    ]
