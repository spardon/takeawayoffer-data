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
        phone_num=list,  # 电话 可能有多个
        open_time=list,  # 营业时间 多段营业的情况
        rating=float,  # 评分
        rating_count=int,  # 评价总数
        oreder_num=int,  # 最近订单数量
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
